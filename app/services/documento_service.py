import os
from datetime import datetime

from flask import current_app, has_app_context
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.documento import Documento
from app.models.assinante_documento import AssinanteDocumento
from app.models.registro_blockchain import RegistroBlockchain
from app.services.pdf_service import gerar_pdf_assinado_com_certificado

from app.services.hash_service import gerar_hash_arquivo

PRIORIDADES = ["baixa", "normal", "alta", "urgente"]


def obter_upload_folder() -> str:
    if has_app_context():
        return current_app.config.get(
            "UPLOAD_FOLDER",
            os.path.join("uploads", "documentos")
        )

    return os.getenv("UPLOAD_FOLDER", os.path.join("uploads", "documentos"))


def validar_prioridade(prioridade: str) -> str:

    if not prioridade:
        return "normal"

    prioridade = prioridade.lower().strip()

    if prioridade not in PRIORIDADES:
        raise ValueError("Prioridade inválida.")

    return prioridade


def salvar_documento_original(
        arquivo,
        usuario_id: int,
        prioridade: str | None = "normal"
):
    if not arquivo:
        raise ValueError("Nenhum Arquivo enviado.")

    nome_seguro = secure_filename(arquivo.filename)

    if not nome_seguro:
        raise ValueError("Nome de arquivo inválido.")

    if not nome_seguro.lower().endswith(".pdf"):
        raise ValueError("O arquivo precisa ser um PDF.")

    prioridade_validada = validar_prioridade(prioridade)

    upload_folder = obter_upload_folder()

    os.makedirs(upload_folder, exist_ok=True)

    caminho_arquivo = os.path.join(upload_folder, nome_seguro)

    arquivo.save(caminho_arquivo)

    hash_original = gerar_hash_arquivo(caminho_arquivo)

    documento = Documento(
        nome_arquivo_original=nome_seguro,
        caminho_arquivo=caminho_arquivo,
        hash_original=hash_original,
        status="aguardando_assinatura",
        usuario_id=usuario_id,
        prioridade=prioridade_validada
    )

    db.session.add(documento)
    db.session.commit()

    return documento


def buscar_documento_por_id(documento_id: int) -> Documento:
    documento = db.session.get(Documento, documento_id)

    if not documento:
        raise ValueError("Documento não encontrado.")

    return documento


def validar_documento_para_assinatura(documento: Documento) -> None:

    if documento.status in ["cancelado", "recusado"]:
        raise ValueError("Este documento não pode ser assinado.")

    if documento.status == "registrado_blockchain":
        raise ValueError("Documento já foi registrado na blockchain.")

    if documento.status not in ["aguardando_assinatura", "assinado"]:
        raise ValueError("Documento nãop pode ser finalizado neste status.")


def validar_documento_para_finalizacao(documento: Documento) -> None:

    if documento.status in ["cancelado", "recusado"]:
        raise ValueError("Documento cancelado ou recusado.")

    if documento.status == "registrado_blockchain":
        raise ValueError("Documento já foi registrado na blockchain.")

    if documento.status not in ["aguardando_assinatura", "assinado"]:
        raise ValueError("Documento não pode ser finalizado neste status.")


def todos_assinantes_assinaram(documento_id: int) -> bool:

    assinantes = AssinanteDocumento.query.filter_by(
        documento_id=documento_id
    ).all()

    if not assinantes:
        return False

    return all(assinante.status == "assinado" for assinante in assinantes)


def cancelar_documento(
        documento_id: int,
        usuario_id: int,
        motivo: str | None = None
) -> Documento:

    documento = buscar_documento_por_id(documento_id)

    if documento.usuario_id != usuario_id:
        raise ValueError(
            "Você não tem permissão para cancelar este documento.")

    if documento.status in ["assinado", "registrado_blockchain"]:
        raise ValueError("Não é possivél cancelar um documento já finalizado.")

    documento.status = "cancelado"
    documento.cancelado_em = datetime.now()
    documento.motivo_cancelamento = motivo

    assinantes = AssinanteDocumento.query.filter_by(
        documento_id=documento_id
    ).all()

    for assinante in assinantes:
        if assinante.status in ["pedente", "visualizado"]:
            assinante.status = "cancelado"

    db.session.commit()

    return documento


def atualizar_prioridade_documento(
        documento_id: int,
        usuario_id: int,
        nova_prioridade: str
) -> Documento:

    documento = buscar_documento_por_id(documento_id)

    if documento.usuario_id != usuario_id:
        raise ValueError("Você não tem permissão para alterar este documento.")

    documento.prioridade = validar_prioridade(nova_prioridade)

    db.session.commit()

    return documento


def atualizar_documento_assinado(
    documento: Documento,
    caminho_pdf_assinado: str,
    nome_pdf_assinado: str
) -> Documento:

    hash_assinado = gerar_hash_arquivo(caminho_pdf_assinado)

    documento.nome_arquivo_assinado = nome_pdf_assinado
    documento.caminho_arquivo_assinado = caminho_pdf_assinado
    documento.hash_arquivo_assinado = hash_assinado
    documento.status = "assinado"

    db.session.commit()

    return documento


def finalizar_documento(documento_id: int) -> Documento:
    from app.services.assinatura_service import listar_assinaturas_documento
    from app.services.blockchain_service import registrar_documento_blockchain

    documento = buscar_documento_por_id(documento_id)

    validar_documento_para_finalizacao(documento)

    if not todos_assinantes_assinaram(documento_id):
        raise ValueError("Ainda existem assinantes pendentes.")

    assinaturas = listar_assinaturas_documento(documento_id)

    nome_pdf_assinado, caminho_pdf_assinado = gerar_pdf_assinado_com_certificado(
        documento=documento,
        assinaturas=assinaturas
    )

    documento = atualizar_documento_assinado(
        documento=documento,
        caminho_pdf_assinado=caminho_pdf_assinado,
        nome_pdf_assinado=nome_pdf_assinado
    )

    referencia_documento = f"DOC-{documento.id}"

    resultado_blockchain = registrar_documento_blockchain(
        hash_arquivo_assinado=documento.hash_arquivo_assinado,
        referencia_documento=referencia_documento
    )

    registro = RegistroBlockchain(
        documento_id=documento.id,
        documento_ref=resultado_blockchain["referencia_documento"],
        hash_registrado=resultado_blockchain["hash_registrado"],
        tx_hash=resultado_blockchain["tx_hash"],
        endereco_contrato=resultado_blockchain["contract_address"],
        endereco_carteira=resultado_blockchain["wallet_address"],
        numero_bloco=resultado_blockchain.get("block_number"),
        rede=resultado_blockchain["rede"],
        status=resultado_blockchain["status"]
    )

    documento.status = "registrado_blockchain"

    db.session.add(registro)
    db.session.commit()

    return documento
