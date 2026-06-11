import os
from urllib.parse import urljoin

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, send_file, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_

from app.extensions import db
from app.models.assinante_documento import AssinanteDocumento
from app.models.documento import Documento
from app.models.registro_blockchain import RegistroBlockchain
from app.services.assinante_service import (
    adicionar_assinante,
    buscar_assinante_por_token,
    marcar_como_visualizado,
    recusar_assinatura,
    validar_usuario_do_convite,
)
from app.services.assinatura_service import assinar_documento
from app.services.blockchain_service import consultar_documento_blockchain
from app.services.crypto_services import verificar_assinatura_hash
from app.services.documento_service import (
    cancelar_documento,
    finalizar_documento,
    salvar_documento_original,
    todos_assinantes_assinaram,
)
from app.services.hash_service import gerar_hash_arquivo
from app.services.email_service import enviar_convite_assinatura

documentos_bp = Blueprint("documentos", __name__, url_prefix="/documentos")


def resolver_caminho_arquivo(caminho_arquivo: str | None) -> str | None:
    if not caminho_arquivo:
        return None

    if os.path.isabs(caminho_arquivo):
        return caminho_arquivo

    base_dir = os.path.dirname(current_app.root_path)
    return os.path.join(base_dir, caminho_arquivo)


def formatar_tamanho_arquivo(caminho_arquivo: str | None) -> str:
    caminho_resolvido = resolver_caminho_arquivo(caminho_arquivo)

    if not caminho_resolvido or not os.path.exists(caminho_resolvido):
        return "-"

    tamanho = os.path.getsize(caminho_resolvido)

    if tamanho < 1024:
        return f"{tamanho} B"

    if tamanho < 1024 * 1024:
        return f"{tamanho / 1024:.1f} KB"

    return f"{tamanho / (1024 * 1024):.1f} MB"


def montar_item_documento(documento: Documento, tipo: str, convite=None) -> dict:
    status_visual = {
        "aguardando_assinatura": {
            "texto": "Pendente",
            "icone": "lucide:clock",
            "classe": "bg-amber-500/10 border border-amber-500/20 text-amber-400",
        },
        "assinado": {
            "texto": "Assinado",
            "icone": "lucide:check-circle-2",
            "classe": "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400",
        },
        "registrado_blockchain": {
            "texto": "Finalizado e registrado",
            "icone": "lucide:link",
            "classe": "bg-sky-500/10 border border-sky-500/20 text-sky-400",
        },
        "recusado": {
            "texto": "Recusado",
            "icone": "lucide:x-circle",
            "classe": "bg-red-500/10 border border-red-500/20 text-red-400",
        },
        "cancelado": {
            "texto": "Cancelado",
            "icone": "lucide:ban",
            "classe": "bg-red-500/10 border border-red-500/20 text-red-400",
        },
    }
    prioridade_visual = {
        "baixa": {
            "texto": "Baixa",
            "icone": "lucide:chevron-down",
            "classe": "bg-slate-500/10 border border-slate-500/20 text-slate-300",
        },
        "normal": {
            "texto": "Normal",
            "icone": "lucide:minus",
            "classe": "bg-white/5 border border-white/10 text-white/60",
        },
        "alta": {
            "texto": "Alta",
            "icone": "lucide:chevron-up",
            "classe": "bg-amber-500/10 border border-amber-500/20 text-amber-400",
        },
        "urgente": {
            "texto": "Urgente",
            "icone": "lucide:flame",
            "classe": "bg-red-500/10 border border-red-500/20 text-red-400",
        },
    }

    criado_em = documento.criado_em
    status = status_visual.get(
        documento.status,
        {
            "texto": documento.status.replace("_", " ").title(),
            "icone": "lucide:file-question",
            "classe": "bg-white/10 border border-white/10 text-white/60",
        }
    )

    todos_assinaram = todos_assinantes_assinaram(documento.id)
    dono_pode_finalizar = (
        tipo in ["proprietario", "proprietario_convite"]
        and documento.status in ["aguardando_assinatura", "assinado"]
        and todos_assinaram
    )

    if documento.status == "registrado_blockchain":
        status = status_visual["registrado_blockchain"]
    elif dono_pode_finalizar and documento.status == "assinado":
        status = {
            "texto": "Registro blockchain pendente",
            "icone": "lucide:link",
            "classe": "bg-amber-500/10 border border-amber-500/20 text-amber-400",
        }
    elif dono_pode_finalizar:
        status = {
            "texto": "Pronto para finalizar",
            "icone": "lucide:file-check-2",
            "classe": "bg-sky-500/10 border border-sky-500/20 text-sky-400",
        }
    elif convite is not None:
        status_convite = {
            "pendente": {
                "texto": "Pendente",
                "icone": "lucide:clock",
                "classe": "bg-amber-500/10 border border-amber-500/20 text-amber-400",
            },
            "visualizado": {
                "texto": "Visualizado",
                "icone": "lucide:eye",
                "classe": "bg-sky-500/10 border border-sky-500/20 text-sky-400",
            },
            "assinado": {
                "texto": "Assinado por você",
                "icone": "lucide:check-circle-2",
                "classe": "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400",
            },
            "recusado": {
                "texto": "Recusado por você",
                "icone": "lucide:x-circle",
                "classe": "bg-red-500/10 border border-red-500/20 text-red-400",
            },
            "cancelado": {
                "texto": "Cancelado",
                "icone": "lucide:ban",
                "classe": "bg-red-500/10 border border-red-500/20 text-red-400",
            },
        }
        status = status_convite.get(convite.status, status)

    return {
        "documento": documento,
        "convite": convite,
        "tipo": tipo,
        "nome": documento.nome_arquivo_original,
        "status": status,
        "prioridade": prioridade_visual.get(
            documento.prioridade or "normal",
            prioridade_visual["normal"]
        ),
        "tamanho": formatar_tamanho_arquivo(documento.caminho_arquivo),
        "data": criado_em.strftime("%d/%m/%Y %H:%M") if criado_em else "-",
        "autor": documento.usuario.nome if documento.usuario else "-",
        "pode_assinar": convite is not None and convite.status in ["pendente", "visualizado"],
        "pode_cancelar": (
            tipo in ["proprietario", "proprietario_convite"]
            and documento.status == "aguardando_assinatura"
            and not todos_assinaram
        ),
        "pode_recusar": convite is not None and convite.status in ["pendente", "visualizado"],
        "pode_finalizar": dono_pode_finalizar,
        "tem_pdf_assinado": bool(documento.caminho_arquivo_assinado),
    }


def usuario_pode_acessar_documento(documento_id: int) -> bool:
    email_usuario = current_user.email.lower().strip()

    documento = db.session.get(Documento, documento_id)

    if not documento:
        return False

    if documento.usuario_id == current_user.id:
        return True

    convite = AssinanteDocumento.query.filter(
        AssinanteDocumento.documento_id == documento_id,
        or_(
            AssinanteDocumento.usuario_id == current_user.id,
            AssinanteDocumento.email == email_usuario
        )
    ).first()

    return convite is not None


def vincular_convite_por_email(assinante: AssinanteDocumento) -> None:
    email_usuario = current_user.email.lower().strip()

    if assinante.usuario_id is None and assinante.email == email_usuario:
        assinante.usuario_id = current_user.id
        assinante.nome = current_user.nome
        db.session.commit()


def enviar_email_convite(assinante: AssinanteDocumento) -> None:
    link_convite = url_for(
        "documentos.convite",
        token_convite=assinante.token_convite,
        _external=True
    )

    enviar_convite_assinatura(
        destinatario=assinante.email,
        nome_assinante=assinante.nome,
        nome_documento=assinante.documento.nome_arquivo_original,
        link_convite=link_convite,
        possui_conta=assinante.usuario_id is not None
    )


@documentos_bp.route("/")
@login_required
def index():
    documentos_criados = Documento.query.filter(
        Documento.usuario_id == current_user.id,
        Documento.status.in_(
            ["aguardando_assinatura", "assinado", "registrado_blockchain", "recusado"])
    ).order_by(Documento.criado_em.desc()).all()

    convites = AssinanteDocumento.query.join(Documento).filter(
        or_(
            AssinanteDocumento.usuario_id == current_user.id,
            AssinanteDocumento.email == current_user.email.lower().strip()
        ),
        AssinanteDocumento.status.in_(
            ["pendente", "visualizado", "assinado", "recusado"]),
        Documento.status.in_(
            ["aguardando_assinatura", "assinado", "registrado_blockchain", "recusado"])
    ).order_by(AssinanteDocumento.convidado_em.desc()).all()

    documentos_por_id = {
        documento.id: montar_item_documento(documento, "proprietario")
        for documento in documentos_criados
    }

    for convite in convites:
        item_existente = documentos_por_id.get(convite.documento_id)

        if item_existente:
            item_existente["convite"] = convite
            item_existente["pode_assinar"] = convite.status in [
                "pendente", "visualizado"]
            item_existente["tipo"] = "proprietario_convite"
            continue

        documentos_por_id[convite.documento_id] = montar_item_documento(
            convite.documento,
            "convite",
            convite
        )

    documentos = list(documentos_por_id.values())

    documentos.sort(
        key=lambda item: item["documento"].criado_em,
        reverse=True
    )

    return render_template(
        "documentos/documentos.html",
        title="Meus Documentos",
        usuario=current_user,
        documentos=documentos
    )


@documentos_bp.route("/<int:documento_id>/visualizar")
@login_required
def visualizar(documento_id: int):
    documento = db.session.get(Documento, documento_id)

    if not documento:
        abort(404)

    if not usuario_pode_acessar_documento(documento_id):
        abort(403)

    caminho_visualizacao = resolver_caminho_arquivo(
        documento.caminho_arquivo_assinado or documento.caminho_arquivo
    )
    nome_visualizacao = documento.nome_arquivo_assinado or documento.nome_arquivo_original

    if not caminho_visualizacao or not os.path.exists(caminho_visualizacao):
        flash("Arquivo do documento não encontrado.", "error")
        return redirect(url_for("documentos.index"))

    return send_file(
        caminho_visualizacao,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=nome_visualizacao
    )


@documentos_bp.route("/<int:documento_id>/download/original")
@login_required
def download_original(documento_id: int):
    documento = db.session.get(Documento, documento_id)

    if not documento:
        abort(404)

    if not usuario_pode_acessar_documento(documento_id):
        abort(403)

    caminho = resolver_caminho_arquivo(documento.caminho_arquivo)

    if not caminho or not os.path.exists(caminho):
        flash("Arquivo original não encontrado.", "error")
        return redirect(url_for("documentos.index"))

    return send_file(
        caminho,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=documento.nome_arquivo_original
    )


@documentos_bp.route("/<int:documento_id>/download/assinado")
@login_required
def download_assinado(documento_id: int):
    documento = db.session.get(Documento, documento_id)

    if not documento:
        abort(404)

    if not usuario_pode_acessar_documento(documento_id):
        abort(403)

    caminho = resolver_caminho_arquivo(documento.caminho_arquivo_assinado)

    if not caminho or not os.path.exists(caminho):
        flash("PDF assinado ainda não foi gerado.", "error")
        return redirect(url_for("documentos.index"))

    return send_file(
        caminho,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=documento.nome_arquivo_assinado
    )


@documentos_bp.route("/<int:documento_id>/verificar")
@login_required
def verificar(documento_id: int):
    documento = db.session.get(Documento, documento_id)

    if not documento:
        abort(404)

    if not usuario_pode_acessar_documento(documento_id):
        abort(403)

    caminho_original = resolver_caminho_arquivo(documento.caminho_arquivo)
    caminho_assinado = resolver_caminho_arquivo(
        documento.caminho_arquivo_assinado)
    problemas = []

    original_integro = False
    if caminho_original and os.path.exists(caminho_original):
        original_integro = gerar_hash_arquivo(
            caminho_original) == documento.hash_original
    else:
        problemas.append("Arquivo original não encontrado.")

    assinado_integro = None
    if documento.hash_arquivo_assinado:
        if caminho_assinado and os.path.exists(caminho_assinado):
            assinado_integro = gerar_hash_arquivo(
                caminho_assinado) == documento.hash_arquivo_assinado
        else:
            assinado_integro = False
            problemas.append("PDF assinado não encontrado.")

    detalhes_assinaturas = []

    for assinatura in documento.assinaturas:
        chave_publica = assinatura.chave_publica
        assinatura_valida = bool(chave_publica) and verificar_assinatura_hash(
            hash_assinado=assinatura.hash_assinatura,
            assinatura_digital=assinatura.assinatura_digital,
            chave_publica_pem=chave_publica.chave_publica
        )

        if assinatura.hash_assinatura != documento.hash_original:
            assinatura_valida = False

        if not assinatura_valida:
            problemas.append(
                f"Assinatura de {assinatura.assinante.email} inválida."
            )

        detalhes_assinaturas.append({
            "assinante": assinatura.assinante.nome,
            "email": assinatura.assinante.email,
            "assinado_em": assinatura.assinado_em.strftime("%d/%m/%Y %H:%M:%S"),
            "hash": assinatura.hash_assinatura,
            "algoritmo": assinatura.algoritmo,
            "valida": assinatura_valida,
        })

    if not detalhes_assinaturas:
        problemas.append(
            "Nenhuma assinatura digital registrada para este documento.")

    valido = (
        original_integro
        and all(item["valida"] for item in detalhes_assinaturas)
        and (assinado_integro is not False)
    )

    return jsonify({
        "ok": valido,
        "documento": documento.nome_arquivo_original,
        "status": documento.status,
        "hash_original": documento.hash_original,
        "hash_assinado": documento.hash_arquivo_assinado,
        "original_integro": original_integro,
        "assinado_integro": assinado_integro,
        "assinaturas": detalhes_assinaturas,
        "problemas": problemas,
    })


@documentos_bp.route("/<int:documento_id>/blockchain/verificar")
@login_required
def verificar_blockchain(documento_id: int):
    documento = db.session.get(Documento, documento_id)

    if not documento:
        abort(404)

    if not usuario_pode_acessar_documento(documento_id):
        abort(403)

    if not documento.hash_arquivo_assinado:
        return jsonify({
            "ok": False,
            "documento": documento.nome_arquivo_original,
            "status": documento.status,
            "problemas": ["Este documento ainda nao possui PDF assinado para consulta."],
        }), 400

    registro_local = RegistroBlockchain.query.filter_by(
        documento_id=documento.id,
        hash_registrado=documento.hash_arquivo_assinado
    ).order_by(RegistroBlockchain.registrado_em.desc()).first()

    def montar_url_explorer(tx_hash: str | None) -> str | None:
        if not tx_hash:
            return None

        base_url = os.getenv(
            "BLOCKCHAIN_EXPLORER_TX_URL",
            "https://sepolia.etherscan.io/tx/"
        )

        return urljoin(base_url.rstrip("/") + "/", tx_hash)

    def serializar_registro(registro):
        if not registro:
            return None

        return {
            "documento_ref": registro.documento_ref,
            "hash_registrado": registro.hash_registrado,
            "tx_hash": registro.tx_hash,
            "endereco_contrato": registro.endereco_contrato,
            "endereco_carteira": registro.endereco_carteira,
            "numero_bloco": registro.numero_bloco,
            "rede": registro.rede,
            "status": registro.status,
            "registrado_em": registro.registrado_em.strftime("%d/%m/%Y %H:%M:%S"),
            "explorer_url": montar_url_explorer(registro.tx_hash),
        }

    problemas = []
    resultado_rede = None

    try:
        resultado_rede = consultar_documento_blockchain(
            documento.hash_arquivo_assinado
        )
    except Exception as e:
        current_app.logger.exception(
            "Falha ao consultar blockchain para documento %s",
            documento_id
        )
        problemas.append(str(e))

    hash_rede = (resultado_rede or {}).get("hash_arquivo")
    hash_rede_normalizado = (hash_rede or "").lower().replace("0x", "")
    hash_documento = documento.hash_arquivo_assinado.lower()
    referencia_rede = (resultado_rede or {}).get("referencia_documento") or ""
    encontrado_na_rede = (
        bool(resultado_rede)
        and hash_rede_normalizado == hash_documento
        and bool(referencia_rede.strip())
    )

    if not encontrado_na_rede and not problemas:
        problemas.append(
            "Nenhum registro correspondente foi encontrado no contrato inteligente."
        )

    return jsonify({
        "ok": encontrado_na_rede,
        "documento": documento.nome_arquivo_original,
        "status": documento.status,
        "hash_assinado": documento.hash_arquivo_assinado,
        "registro_local": serializar_registro(registro_local),
        "registro_rede": resultado_rede,
        "problemas": problemas,
    })


@documentos_bp.route("/convites/<token_convite>")
def convite(token_convite: str):
    try:
        assinante = buscar_assinante_por_token(token_convite)
    except ValueError:
        flash("Convite inválido ou não encontrado.", "error")
        return redirect(url_for("main.index"))

    if current_user.is_authenticated:
        vincular_convite_por_email(assinante)

        try:
            validar_usuario_do_convite(assinante, current_user.id)
            marcar_como_visualizado(assinante)
            usuario_autorizado = True
        except (PermissionError, ValueError):
            usuario_autorizado = False
    else:
        usuario_autorizado = False

    return render_template(
        "documentos/convite.html",
        title="Convite de Assinatura",
        usuario=current_user if current_user.is_authenticated else None,
        assinante=assinante,
        documento=assinante.documento,
        usuario_autorizado=usuario_autorizado
    )


@documentos_bp.route("/<int:documento_id>/cancelar", methods=["POST"])
@login_required
def cancelar(documento_id: int):
    try:
        cancelar_documento(
            documento_id=documento_id,
            usuario_id=current_user.id,
            motivo=request.form.get("motivo")
        )
        flash("Documento cancelado com sucesso.", "success")
    except ValueError as e:
        db.session.rollback()
        flash(str(e), "error")

    return redirect(url_for("documentos.index"))


@documentos_bp.route("/<int:documento_id>/finalizar", methods=["POST"])
@login_required
def finalizar(documento_id: int):
    documento = db.session.get(Documento, documento_id)

    if not documento:
        abort(404)

    if documento.usuario_id != current_user.id:
        abort(403)

    try:
        documento = finalizar_documento(documento_id)

        if documento.status == "registrado_blockchain":
            flash("Documento finalizado e registrado com sucesso.", "success")
        else:
            flash("Documento finalizado. Registro na blockchain pendente.", "warning")
    except ConnectionError as e:
        current_app.logger.exception(
            "Blockchain indisponível ao finalizar documento %s",
            documento_id
        )
        flash(
            f"PDF assinado gerado, mas a blockchain está indisponível: {e}",
            "warning"
        )
    except ValueError as e:
        db.session.rollback()
        flash(str(e), "error")
    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Falha ao finalizar documento %s",
            documento_id
        )
        flash("Não foi possível finalizar o documento agora.", "error")

    return redirect(url_for("documentos.index"))


@documentos_bp.route("/convites/<int:assinante_id>/recusar", methods=["POST"])
@login_required
def recusar_convite(assinante_id: int):
    try:
        assinante = db.session.get(AssinanteDocumento, assinante_id)

        if not assinante:
            raise ValueError("Convite de assinatura inválido.")

        vincular_convite_por_email(assinante)
        validar_usuario_do_convite(assinante, current_user.id)
        recusar_assinatura(
            token_convite=assinante.token_convite,
            motivo=request.form.get("motivo")
        )
        flash("Convite recusado com sucesso.", "success")
    except PermissionError as e:
        flash(str(e), "error")
    except ValueError as e:
        db.session.rollback()
        flash(str(e), "error")

    return redirect(url_for("documentos.index"))


@documentos_bp.route("/<int:documento_id>/assinar", methods=["POST"])
@login_required
def assinar(documento_id: int):
    assinante_id = request.form.get("assinante_id", type=int)
    chave_privada = request.files.get("chave_privada")
    senha_chave_privada = request.form.get("senha_chave_privada", "").strip()

    if not assinante_id:
        flash("Convite de assinatura inválido.", "error")
        return redirect(url_for("documentos.index"))

    if not chave_privada or not chave_privada.filename:
        flash("Envie o arquivo da chave privada .pem.", "error")
        return redirect(url_for("documentos.index"))

    if not senha_chave_privada:
        flash("Informe a senha da chave privada.", "error")
        return redirect(url_for("documentos.index"))

    try:
        assinante = db.session.get(AssinanteDocumento, assinante_id)

        if not assinante or assinante.documento_id != documento_id:
            raise ValueError("Convite de assinatura inválido.")

        vincular_convite_por_email(assinante)
        validar_usuario_do_convite(assinante, current_user.id)

        chave_privada_pem = chave_privada.read().decode("utf-8")

        assinar_documento(
            documento_id=documento_id,
            assinante_id=assinante_id,
            chave_privada=chave_privada_pem,
            senha_chave_privada=senha_chave_privada
        )

        flash("Documento assinado com sucesso.", "success")
    except UnicodeDecodeError:
        flash(
            "Não foi possível ler a chave privada. Envie um arquivo .pem válido.", "error")
    except PermissionError as e:
        flash(str(e), "error")
    except ValueError as e:
        db.session.rollback()
        flash(str(e), "error")

    return redirect(url_for("documentos.index"))


@documentos_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo_documento():
    if request.method == "POST":
        arquivo = request.files.get("arquivo")
        nomes = request.form.getlist("assinantes_nome[]")
        emails = request.form.getlist("assinantes_email[]")

        assinantes = [
            (nome.strip(), email.strip())
            for nome, email in zip(nomes, emails)
            if nome.strip() or email.strip()
        ]

        if not assinantes:
            flash("Informe ao menos um assinante.", "error")
            return redirect(url_for("documentos.novo_documento"))

        if any(not nome or not email for nome, email in assinantes):
            flash("Preencha nome e e-mail de todos os assinantes.", "error")
            return redirect(url_for("documentos.novo_documento"))

        documento = None

        try:
            documento = salvar_documento_original(
                arquivo=arquivo,
                usuario_id=current_user.id,
                prioridade=request.form.get("prioridade", "normal")
            )

            convites_criados = []

            for nome, email in assinantes:
                assinante = adicionar_assinante(
                    documento_id=documento.id,
                    nome=nome,
                    email=email
                )
                convites_criados.append(assinante)

            emails_enviados = 0

            for assinante in convites_criados:
                try:
                    enviar_email_convite(assinante)
                    emails_enviados += 1
                except Exception:
                    current_app.logger.exception(
                        "Falha ao enviar convite de assinatura para %s",
                        assinante.email
                    )

            if emails_enviados == len(convites_criados):
                flash("Documento preparado e convites enviados com sucesso.", "success")
            elif emails_enviados > 0:
                flash(
                    "Documento preparado. Alguns convites não puderam ser enviados por e-mail.", "warning")
            else:
                flash(
                    "Documento preparado, mas os convites não puderam ser enviados por e-mail.", "warning")

            return redirect(url_for("documentos.index"))
        except ValueError as e:
            db.session.rollback()
            if documento is not None:
                caminho_arquivo = documento.caminho_arquivo
                db.session.delete(documento)
                db.session.commit()

                if caminho_arquivo and os.path.exists(caminho_arquivo):
                    os.remove(caminho_arquivo)

            flash(str(e), "error")
            return redirect(url_for("documentos.novo_documento"))

    return render_template("documentos/novo_documento.html", title="Novo Documento", usuario=current_user)
