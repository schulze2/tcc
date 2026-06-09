from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import base64


def gerar_chave_eccdsa(senha_chave):
    chave_privada = ECC.generate(curve='P-256')

    chave_publica = chave_privada.public_key()

    chave_privada_pem = chave_privada.export_key(
        format="PEM",
        passphrase=senha_chave,
        protection="PBKDF2WithHMAC-SHA512AndAES256-CBC"
    )

    chave_publica_pem = chave_publica.export_key(format="PEM")
    return chave_privada_pem, chave_publica_pem


def assinar_hash(
        hash_assinado: str,
        chave_privada_pem: str,
        senha_chave: str
) -> str:

    try:
        chave_privada = ECC.import_key(
            chave_privada_pem,
            passphrase=senha_chave
        )
    except ValueError:
        raise ValueError(
            "Senha da chave privada inválida ou chave privada incorreta.")

    hash_obj = SHA256.new(bytes.fromhex(hash_assinado))

    assinador = DSS.new(chave_privada, 'fips-186-3')

    assinatura = assinador.sign(hash_obj)

    return base64.b64encode(assinatura).decode('utf-8')


def verificar_assinatura_hash(
        hash_assinado: str,
        assinatura_digital: str,
        chave_publica_pem: str
) -> bool:

    try:
        chave_publica = ECC.import_key(chave_publica_pem)
        hash_obj = SHA256.new(bytes.fromhex(hash_assinado))
        assinatura = base64.b64decode(assinatura_digital)
        verificador = DSS.new(chave_publica, 'fips-186-3')
        verificador.verify(hash_obj, assinatura)
        return True
    except Exception:
        return False
