import hashlib


def gerar_hash_arquivo(caminho_arquivo: str) -> str:
    sha256 = hashlib.sha256()

    with open(caminho_arquivo, "rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(4096), b""):
            sha256.update(bloco)

    return sha256.hexdigest()
