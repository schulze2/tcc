import os
from datetime import datetime

import pymupdf


OUTPUT_FOLDER = "uploads/documentos_assinados"


def criar_pasta_saida() -> None:
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def gerar_nome_pdf_assinado(documento) -> str:
    nome_original = documento.nome_arquivo_original

    if nome_original.lower().endswith(".pdf"):
        nome_base = nome_original[:-4]
    else:
        nome_base = nome_original

    return f"{nome_base}_assinado_{documento.id}.pdf"


def inserir_linha(pagina, texto: str, x: int, y: int, tamanho: int = 8) -> int:
    pagina.insert_text(
        (x, y),
        texto,
        fontsize=tamanho,
        fontname="helv"
    )

    return y + 15


def nova_pagina_certificado(doc):
    return doc.new_page(width=595, height=842)


def garantir_espaco(doc, pagina, y: int):
    if y > 780:
        pagina = nova_pagina_certificado(doc)
        y = 50

    return pagina, y


def abreviar_valor(valor: str | None, inicio: int = 24, fim: int = 16) -> str:
    if not valor:
        return "-"

    if len(valor) <= inicio + fim + 3:
        return valor

    return f"{valor[:inicio]}...{valor[-fim:]}"


def gerar_pdf_assinado_com_certificado(documento, assinaturas: list) -> tuple[str, str]:
    criar_pasta_saida()

    nome_pdf_assinado = gerar_nome_pdf_assinado(documento)
    caminho_pdf_assinado = os.path.join(OUTPUT_FOLDER, nome_pdf_assinado)

    doc = pymupdf.open(documento.caminho_arquivo)

    pagina = nova_pagina_certificado(doc)

    x = 50
    y = 50

    pagina.insert_text(
        (x, y),
        "CERTIFICADO DE ASSINATURAS DIGITAIS",
        fontsize=16,
        fontname="helv"
    )

    y += 35

    linhas_cabecalho = [
        f"Documento: {documento.nome_arquivo_original}",
        f"ID do documento: {documento.id}",
        f"Hash original: {documento.hash_original}",
        f"Data de geração do certificado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        "Este documento foi assinado digitalmente utilizando ECC/ECDSA.",
    ]

    for linha in linhas_cabecalho:
        pagina, y = garantir_espaco(doc, pagina, y)
        y = inserir_linha(pagina, linha, x, y, tamanho=8)

    y += 15

    pagina, y = garantir_espaco(doc, pagina, y)
    pagina.insert_text(
        (x, y),
        "ASSINATURAS",
        fontsize=12,
        fontname="helv"
    )

    y += 25

    if not assinaturas:
        pagina, y = garantir_espaco(doc, pagina, y)
        y = inserir_linha(
            pagina,
            "Nenhuma assinatura registrada.",
            x,
            y,
            tamanho=8
        )
    else:
        for assinatura in assinaturas:
            pagina, y = garantir_espaco(doc, pagina, y)

            assinante = assinatura.assinante

            bloco = [
                "----------------------------------------",
                f"ID da assinatura: {assinatura.id}",
                f"Assinante: {assinante.nome}",
                f"E-mail: {assinante.email}",
                f"Data/Hora da assinatura: {assinatura.assinado_em.strftime('%d/%m/%Y %H:%M:%S')}",
                f"Algoritmo: {assinatura.algoritmo}",
                f"Hash do documento assinado: {assinatura.hash_assinatura}",
                f"Assinatura digital: {abreviar_valor(assinatura.assinatura_digital)}",
                f"Chave pública ID: {assinatura.chave_publica_id}",
            ]

            for linha in bloco:
                pagina, y = garantir_espaco(doc, pagina, y)
                y = inserir_linha(pagina, linha, x, y, tamanho=8)

            y += 12

    doc.save(caminho_pdf_assinado)
    doc.close()

    return nome_pdf_assinado, caminho_pdf_assinado
