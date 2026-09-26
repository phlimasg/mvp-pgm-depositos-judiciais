import os
import requests
import logging
from requests.auth import HTTPBasicAuth
from mail import enviar_email_erro, enviar_email_sucesso

def enviar_arquivos_para_api(pasta_destino: str, url_api: str, usuario: str, senha: str):
    """
    Envia todos os arquivos .ret de uma pasta para a API FastAPI (autenticação Basic Auth).
    """
    os.environ["NO_PROXY"] = "10.32.96.228,localhost,127.0.0.1"
    arquivos = [
        os.path.join(pasta_destino, f)
        for f in os.listdir(pasta_destino)
        if f.endswith(".ret") and os.path.isfile(os.path.join(pasta_destino, f))
    ]

    if not arquivos:
        logging.info("Nenhum arquivo .ret encontrado para envio.")
        return

    logging.info(f"Encontrados {len(arquivos)} arquivo(s) para envio à API.")

    # monta o campo "files" conforme sua rota FastAPI
    files = []
    for caminho in arquivos:
        nome = os.path.basename(caminho)
        files.append(("files", (nome, open(caminho, "rb"), "application/octet-stream")))

    try:
        logging.info(f">>> Enviando arquivos...")
        response = requests.post(
            url_api,
            files=files,
            auth=HTTPBasicAuth(usuario, senha),
            timeout=480
        )

        if response.status_code in (200, 201):
            logging.info(f"✅ Arquivos enviados com sucesso! ({response.status_code})")
            logging.info(f"Resposta: {response.text}")
        else:
            logging.error(f"❌ Falha ao enviar arquivos: {response.status_code} - {response.text}")

    except Exception as e:
        logging.error(f"⚠️ Erro ao enviar arquivos para API: {e}")
        enviar_email_erro(e)
