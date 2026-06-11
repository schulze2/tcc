import secrets
from datetime import datetime

from app.extensions import db
from app.models.usuario import Usuario
from app.models.assinante_documento import AssinanteDocumento


def gerar_token_convite() -> str:
    """Gera um token seguro para identificar o convite de assinatura."""

    return secrets.token_urlsafe(32)


def normalizar_email(email: str) -> str:
    """Valida, remove espaços e converte o e-mail para minúsculas."""

    if not email:
        raise ValueError("E-mail é obrigatório.")

    return email.lower().strip()


def adicionar_assinante(
    documento_id: int,
    nome: str,
    email: str
) -> AssinanteDocumento:
    """
    Adiciona um assinante ao documento.

    Se já existir usuário com esse e-mail, o convite é vinculado
    automaticamente ao usuário.
    """

    if not nome:
        raise ValueError("Nome do assinante é obrigatório.")

    email_normalizado = normalizar_email(email)

    assinante_existente = AssinanteDocumento.query.filter_by(
        documento_id=documento_id,
        email=email_normalizado
    ).first()

    if assinante_existente:
        raise ValueError("Esse e-mail já foi convidado para este documento.")

    usuario = Usuario.query.filter_by(
        email=email_normalizado
    ).first()

    if usuario:
        usuario_id = usuario.id
        nome_assinante = usuario.nome
    else:
        usuario_id = None
        nome_assinante = nome.strip()

    assinante = AssinanteDocumento(
        documento_id=documento_id,
        usuario_id=usuario_id,
        nome=nome_assinante,
        email=email_normalizado,
        status="pendente",
        token_convite=gerar_token_convite(),
        convidado_em=datetime.now()
    )

    db.session.add(assinante)
    db.session.commit()

    return assinante


def buscar_assinante_por_token(token_convite: str) -> AssinanteDocumento:
    """Busca o assinante pelo token público do convite."""

    assinante = AssinanteDocumento.query.filter_by(
        token_convite=token_convite
    ).first()

    if not assinante:
        raise ValueError("Convite inválido ou não encontrado.")

    return assinante


def listar_assinantes_documento(documento_id: int) -> list[AssinanteDocumento]:
    """Lista todos os assinantes vinculados a um documento."""

    return AssinanteDocumento.query.filter_by(
        documento_id=documento_id
    ).all()


def marcar_como_visualizado(assinante: AssinanteDocumento) -> AssinanteDocumento:
    """Marca um convite pendente como visualizado e registra a data."""

    if assinante.status == "pendente":
        assinante.status = "visualizado"
        assinante.visualizado_em = datetime.now()
        db.session.commit()

    return assinante


def validar_usuario_do_convite(
    assinante: AssinanteDocumento,
    usuario_logado_id: int
) -> None:
    """
    Garante que somente o usuário vinculado ao convite possa assinar.
    """

    if assinante.usuario_id is None:
        raise ValueError(
            "Este convite ainda não está vinculado a uma conta. "
            "Crie uma conta usando o mesmo e-mail do convite."
        )

    if assinante.usuario_id != usuario_logado_id:
        raise PermissionError("Este convite pertence a outro usuário.")


def vincular_convites_pendentes_usuario(usuario: Usuario) -> None:
    """
    Quando um usuário se cadastra, vincula automaticamente
    convites enviados anteriormente para o e-mail dele.
    """

    email_normalizado = normalizar_email(usuario.email)

    convites = AssinanteDocumento.query.filter_by(
        email=email_normalizado,
        usuario_id=None
    ).all()

    for convite in convites:
        convite.usuario_id = usuario.id
        convite.nome = usuario.nome

    db.session.commit()


def recusar_assinatura(
    token_convite: str,
    motivo: str | None = None
) -> AssinanteDocumento:
    """
    Registra a recusa de um convite e bloqueia o documento para novas assinaturas.

    Também cancela os demais convites que ainda estavam pendentes ou visualizados.
    """

    assinante = buscar_assinante_por_token(token_convite)
    documento = assinante.documento

    if documento.status in [
        "cancelado",
        "assinado",
        "registrado_blockchain",
        "recusado"
    ]:
        raise ValueError("Este documento não permite mais alterações.")

    if assinante.status == "assinado":
        raise ValueError("Você já assinou este documento.")

    assinante.status = "recusado"
    assinante.recusado_em = datetime.now()
    assinante.motivo_recusa = motivo

    documento.status = "recusado"
    documento.cancelado_em = datetime.now()
    documento.motivo_cancelamento = (
        f"Recusado por {assinante.email}: "
        f"{motivo or 'sem motivo informado'}"
    )

    outros_assinantes = AssinanteDocumento.query.filter(
        AssinanteDocumento.documento_id == documento.id,
        AssinanteDocumento.id != assinante.id,
        AssinanteDocumento.status.in_(["pendente", "visualizado"])
    ).all()

    for outro in outros_assinantes:
        outro.status = "cancelado"

    db.session.commit()

    return assinante
