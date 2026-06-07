from datetime import datetime

from app.extensions import db
from app.models.assinatura import Assinatura
from app.models.chave_publica import ChavePublica
from app.models.assinante_documento import AssinanteDocumento

from app.services.documento_service import (
    buscar_documento_por_id,
    validar_documento_para_assinatura
)

from app.services.crypto_services import assinar_hash


def buscar_chave_publica_ativa(usuario_id: int) -> ChavePublica:

    chave_publica = ChavePublica.query.filter_by(
        id_usuario=usuario_id,
        status="ativa"
    ).first()

    if not chave_publica:
        raise ValueError(
            "Chave pública ativa não encontrada para este usuário.")

    return chave_publica


def buscar_assinante_por_id(assinante_id: int) -> AssinanteDocumento:

    assinante = db.session.get(AssinanteDocumento, assinante_id)

    if not assinante:
        raise ValueError("Assinante não encontrado.")

    return assinante


def assinar_documento(
    documento_id: int,
    assinante_id: int,
    chave_privada: str,
    senha_chave_privada: str
) -> Assinatura:

    documento = buscar_documento_por_id(documento_id)

    validar_documento_para_assinatura(documento)

    assinante = buscar_assinante_por_id(assinante_id)

    if assinante.documento_id != documento_id:
        raise ValueError("Assinante não está associado a este documento.")

    if assinante.status in ["recusado", "cancelado"]:
        raise ValueError("Este convite não pode mais ser assinado")

    if assinante.status == "assinado":
        raise ValueError("Este documento já foi assinado por este usuário.")

    if assinante.usuario_id is None:
        raise ValueError(
            "Assinante precisa estar vinculado a um usúario para assinar.")

    assinatura_existente = Assinatura.query.filter_by(
        assinante_id=assinante_id
    ).first()

    if assinatura_existente:
        raise ValueError("Já existe uma assinatura para este assinante.")

    chave_publica = buscar_chave_publica_ativa(assinante.usuario_id)

    hash_assinado = documento.hash_original

    assinatura_digital = assinar_hash(
        hash_assinado=hash_assinado,
        chave_privada_pem=chave_privada,
        senha_chave=senha_chave_privada
    )

    assinatura = Assinatura(
        documento_id=documento_id,
        assinante_id=assinante_id,
        hash_assinatura=hash_assinado,
        assinatura_digital=assinatura_digital,
        algoritmo="ECC/ECDSA-P256",
        chave_publica_id=chave_publica.id,
        assinado_em=datetime.now()
    )

    assinante.status = "assinado"
    assinante.assinado_em = datetime.now()

    db.session.add(assinatura)
    db.session.commit()

    return assinatura


def listar_assinaturas_por_documento(documento_id: int) -> list[Assinatura]:

    return Assinatura.query.filter_by(documento_id=documento_id).all()


def buscar_assinatura_por_id(assinatura_id: int) -> Assinatura:

    assinatura = db.session.get(Assinatura, assinatura_id)

    if not assinatura:
        raise ValueError("Assinatura não encontrada.")

    return assinatura


def verificar_assinatura_existente(assinante_id: int) -> bool:

    assinatura = Assinatura.query.filter_by(assinante_id=assinante_id).first()

    return assinatura is not None
