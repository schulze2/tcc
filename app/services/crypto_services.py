from Crypto.PublicKey import ECC


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
