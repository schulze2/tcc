from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from app.models.usuario import Usuario
from app.models.chave_publica import ChavePublica
from app.services.crypto_services import gerar_chave_eccdsa
from app.services.assinante_service import vincular_convites_pendentes_usuario

from app.extensions import db


def criar_usuario(nome, email, oab, senha, cargo, senha_chave):
    """
    Cria um usuário com senha criptografada e par de chaves ECC/ECDSA.

    Também salva a chave pública ativa e vincula convites pendentes enviados
    anteriormente para o mesmo e-mail.
    """

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

        vincular_convites_pendentes_usuario(usuario)

        return usuario, chave_privada_pem

    except IntegrityError:
        db.session.rollback()
        raise ValueError(
            "Ocorreu um erro ao criar o usuário. Tente novamente.")


def autenticar_usuario(email, senha):
    """Valida as credenciais do usuário e retorna o registro autenticado."""

    email_normalizado = email.strip().lower()
    usuario = Usuario.query.filter_by(email=email_normalizado).first()

    if not usuario:
        raise ValueError("Usuário não encontrado.")

    if not check_password_hash(usuario.senha, senha):
        raise ValueError("E-mail ou senha incorretos.")

    return usuario
