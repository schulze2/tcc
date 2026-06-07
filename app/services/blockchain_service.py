import json
import os
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
ABI_PATH = BASE_DIR / 'blockchain' / 'RegistroDocumentosABI.json'


def carregar_abi():
    with open(ABI_PATH, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def conectar_blockchain():
    web3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))

    if not web3.is_connected():
        raise ConnectionError(
            "Não foi possível conectar à rede Ethereum Sepolia testnet.")

    return web3


def obter_contrato(web3: Web3):
    endereco_contrato = Web3.to_checksum_address(
        os.getenv("CONTRACT_ADDRESS")
    )

    abi = carregar_abi()

    return web3.eth.contract(
        address=endereco_contrato,
        abi=abi
    )


def preparar_hash_bytes32(hash_hex: str):
    if not hash_hex:
        raise ValueError("Hash não informado")

    if hash_hex.startswith("0x"):
        hash_formatado = "0x" + hash_hex
    else:
        hash_formatado = "0x" + hash_hex

    if len(hash_formatado) != 66:
        raise ValueError(
            "Hash inválido. O SHA-256 precisa ter 64 caracteres hexadecimais."
        )

    return hash_formatado


def consultar_documento_blockchain(hash_arquivo: str):
    web3 = conectar_blockchain()
    contrato = obter_contrato(web3)

    hash_bytes32 = preparar_hash_bytes32(hash_arquivo)

    resultado = contrato.functions.consultarDocumento(hash_bytes32).call()

    return {
        "hash_arquivo": web3.to_hex(resultado[0]),
        "referencia_documento": resultado[1],
        "registrado_por": resultado[2],
        "data_registro": resultado[3]
    }


def registrar_documento_blockchain(
    hash_arquivo_assinado: str,
    referencia_documento: str
):
    web3 = conectar_blockchain()
    contrato = obter_contrato(web3)

    carteira_endereco = Web3.to_checksum_address(
        os.getenv("WALLET_ADDRESS")
    )

    chave_privada = os.getenv("PRIVATE_KEY")

    endereco_contrato = Web3.to_checksum_address(
        os.getenv("CONTRACT_ADDRESS")
    )

    chain_id = int(os.getenv("CHAIN_ID", "11155111"))

    hash_bytes32 = preparar_hash_bytes32(hash_arquivo_assinado)

    ja_existe = contrato.functions.documentoExiste(hash_bytes32).call()

    if ja_existe:
        raise ValueError("Este hash já foi registrado na blockChain.")

    nonce = web3.eth.get_transaction_count(carteira_endereco)

    transacao = contrato.functions.registrarDocumento(
        hash_bytes32,
        referencia_documento
    ).build_transaction({
        "from": carteira_endereco,
        "nonce": nonce,
        "chainId": chain_id,
        "gas": 300_000,
        "maxFeePerGas": web3.to_wei("30", "gwei"),
        "maxPriorityFeePerGas": web3.to_wei("2", "gwei"),
    })

    transacao_assinada = web3.eth.account.sign_transaction(
        transacao,
        private_key=chave_privada
    )

    tx_hash = web3.eth.send_raw_transaction(
        transacao_assinada.rawTransaction
    )

    recibo = web3.eth.wait_for_transaction_receipt(tx_hash)

    if recibo.status != 1:
        raise Exception("A transação falhou na blockchain.")

    return {
        "tx_hash": web3.to_hex(tx_hash),
        "hash_registrado": hash_arquivo_assinado,
        "referencia_documento": referencia_documento,
        "contract_address": endereco_contrato,
        "wallet_address": carteira_endereco,
        "block_number": recibo.blockNumber,
        "rede": os.getenv("BLOCKCHAIN_NETWORK", "Sepolia"),
        "status": "Confirmado"
    }
