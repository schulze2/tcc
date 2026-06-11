from flask_mail import Message

from app.extensions import mail


def enviar_convite_assinatura(
    destinatario: str,
    nome_assinante: str,
    nome_documento: str,
    link_convite: str,
    possui_conta: bool
) -> None:
    """
    Envia por e-mail o convite para assinatura de um documento.

    Ajusta as instruções conforme o destinatário já tenha conta ou precise
    criar uma usando o mesmo e-mail do convite.
    """

    assunto = "Convite para assinatura digital de documento"

    if possui_conta:
        instrucoes = (
            "Você já possui conta no sistema. "
            "Acesse o link abaixo, faça login e assine o documento."
        )
    else:
        instrucoes = (
            "Você ainda não possui conta no sistema. "
            "Acesse o link abaixo e crie uma conta usando este mesmo e-mail "
            "para conseguir assinar o documento."
        )

    corpo = f"""
    Olá, {nome_assinante}.

    Você foi convidado para assinar digitalmente o documento:

    {nome_documento}

    {instrucoes}

    Link do convite:
    {link_convite}

    Atenciosamente,
    Sistema de Assinatura Digital
    """

    mensagem = Message(
        subject=assunto,
        recipients=[destinatario],
        body=corpo
    )

    mail.send(mensagem)
