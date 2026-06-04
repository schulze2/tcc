from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from app.models.usuario import Usuario
from app.models.chave_publica import ChavePublica
from app.services.crypto_services import gerar_chave_eccdsa

from app.extensions import db


def criar_usuario(nome, email, oab, senha, cargo, senha_chave):

    email_normalizado = email.strip().lower()

    usuario_existente = Usuario.query.filter_by(
        email=email_normalizado).first()

    if usuario_existente:
        raise ValueError("Já existe um usuário com este email.")

    chave_privada_pem, chave_publica_pem = gerar_chave_eccdsa(senha_chave)

    usuario = Usuario(
        nome=nome,
        email=email_normalizado,
        oab=oab,
        senha=generate_password_hash(senha),
        cargo=cargo
    )

    chave_publica = ChavePublica(
        chave_publica=chave_publica_pem,
        usuario=usuario,
        status='ativa'
    )

    try:
        db.session.add(usuario)
        db.session.add(chave_publica)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        raise ValueError(
            "Ocorreu um erro ao criar o usuário. Tente novamente.")

    return usuario, chave_privada_pem
