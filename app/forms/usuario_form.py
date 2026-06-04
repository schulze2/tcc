from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from wtforms_sqlalchemy.fields import QuerySelectField

from app.models.cargo import Cargo


def obter_cargos():
    return Cargo.query.all()


class CadastroUsuarioForm(FlaskForm):
    nome = StringField("Nome Completo", validators=[
        DataRequired(message="O nome é obrigatório."),
        Length(min=5, max=100, message="O Nome deve ter 5 a 100 caracteres.")
    ])

    email = EmailField("Email", validators=[
        DataRequired(message="O email é obrigatório."),
        Email(message="Digite um email válido.")
    ])

    oab = StringField("Número da OAB", validators=[
        DataRequired(message="O número da OAB é obrigatório."),
        Length(min=5, max=14,
               message="O número da OAB deve ter entre 5 e 14 caracteres.")
    ])

    senha = PasswordField("Senha", validators=[
        DataRequired(message="A senha é obrigatória."),
        Length(min=8, message="A senha deve ter pelo menos 8 caracteres.")
    ])

    confirmar_senha = PasswordField("Confirmar Senha", validators=[
        DataRequired(message="A confirmação de senha é obrigatória."),
        EqualTo('senha', message="As senhas devem coincidir.")
    ])

    senha_chave = PasswordField("Senha da Chave", validators=[
        DataRequired(message="A senha da chave é obrigatória."),
        Length(min=6, message="A senha da chave deve ter pelo menos 6 caracteres.")
    ])

    confirmar_senha_chave = PasswordField("Confirmar Senha da Chave", validators=[
        DataRequired(message="A confirmação da senha da chave é obrigatória."),
        EqualTo('senha_chave', message="As senhas da chave devem coincidir.")
    ])

    cargo = QuerySelectField(
        'Cargo',
        query_factory=obter_cargos,
        allow_blank=False,
        blank_text="Selecione um cargo",
        get_label='cargo',
        validators=[DataRequired(message="O cargo é obrigatório.")]
    )

    submit = SubmitField("Registrar")
