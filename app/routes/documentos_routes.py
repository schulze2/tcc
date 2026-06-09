import os

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_

from app.extensions import db
from app.models.assinante_documento import AssinanteDocumento
from app.models.documento import Documento
from app.services.assinante_service import (
    adicionar_assinante,
    buscar_assinante_por_token,
    marcar_como_visualizado,
    recusar_assinatura,
    validar_usuario_do_convite,
)
from app.services.assinatura_service import assinar_documento
from app.services.documento_service import cancelar_documento, salvar_documento_original
from app.services.email_service import enviar_convite_assinatura

documentos_bp = Blueprint("documentos", __name__, url_prefix="/documentos")


def formatar_tamanho_arquivo(caminho_arquivo: str | None) -> str:
    if not caminho_arquivo or not os.path.exists(caminho_arquivo):
        return "-"

    tamanho = os.path.getsize(caminho_arquivo)

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
            "texto": "Registrado",
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

    criado_em = documento.criado_em
    status = status_visual.get(
        documento.status,
        {
            "texto": documento.status.replace("_", " ").title(),
            "icone": "lucide:file-question",
            "classe": "bg-white/10 border border-white/10 text-white/60",
        }
    )

    if convite is not None:
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
        "tamanho": formatar_tamanho_arquivo(documento.caminho_arquivo),
        "data": criado_em.strftime("%d/%m/%Y %H:%M") if criado_em else "-",
        "autor": documento.usuario.nome if documento.usuario else "-",
        "pode_assinar": convite is not None and convite.status in ["pendente", "visualizado"],
        "pode_cancelar": tipo in ["proprietario", "proprietario_convite"],
        "pode_recusar": convite is not None and convite.status in ["pendente", "visualizado"],
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
        Documento.status.in_(["aguardando_assinatura", "assinado", "registrado_blockchain"])
    ).order_by(Documento.criado_em.desc()).all()

    convites = AssinanteDocumento.query.join(Documento).filter(
        or_(
            AssinanteDocumento.usuario_id == current_user.id,
            AssinanteDocumento.email == current_user.email.lower().strip()
        ),
        AssinanteDocumento.status.in_(["pendente", "visualizado", "assinado", "recusado"]),
        Documento.status.in_(["aguardando_assinatura", "assinado", "registrado_blockchain", "recusado"])
    ).order_by(AssinanteDocumento.convidado_em.desc()).all()

    documentos_por_id = {
        documento.id: montar_item_documento(documento, "proprietario")
        for documento in documentos_criados
    }

    for convite in convites:
        item_existente = documentos_por_id.get(convite.documento_id)

        if item_existente:
            item_existente["convite"] = convite
            item_existente["pode_assinar"] = convite.status in ["pendente", "visualizado"]
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

    if not documento.caminho_arquivo or not os.path.exists(documento.caminho_arquivo):
        flash("Arquivo do documento não encontrado.", "error")
        return redirect(url_for("documentos.index"))

    return send_file(
        documento.caminho_arquivo,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=documento.nome_arquivo_original
    )


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
        flash("Não foi possível ler a chave privada. Envie um arquivo .pem válido.", "error")
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
                flash("Documento preparado. Alguns convites não puderam ser enviados por e-mail.", "warning")
            else:
                flash("Documento preparado, mas os convites não puderam ser enviados por e-mail.", "warning")

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
