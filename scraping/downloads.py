import logging
import os
import re
import shutil
import time
from datetime import datetime

padrao_duplicata = re.compile(r"\(\d+\)\.ret$")

def mover_arquivos_lidos(pasta_origem, pasta_destino="DJOLidos"):
    """Move todos os arquivos .ret lidos para a pasta DJOLidos"""
    # Cria a pasta DJOLidos se não existir
    caminho_djo_lidos = os.path.join(pasta_origem, pasta_destino)
    os.makedirs(caminho_djo_lidos, exist_ok=True)
    
    # Lista todos os arquivos .ret na raiz
    arquivos_ret = [
        f for f in os.listdir(pasta_origem)
        if f.endswith(".ret") and os.path.isfile(os.path.join(pasta_origem, f))
    ]
    
    if arquivos_ret:
        for arquivo in arquivos_ret:
            caminho_origem = os.path.join(pasta_origem, arquivo)
            caminho_destino = os.path.join(caminho_djo_lidos, arquivo)
            
            try:
                shutil.move(caminho_origem, caminho_destino)
                logging.info(f">>> Arquivo {arquivo} movido para DJOLidos")
            except Exception as e:
                logging.error(f">>> Erro ao mover {arquivo}: {str(e)}")
        
        logging.info(f">>> {len(arquivos_ret)} arquivo(s) movido(s) para DJOLidos")
    else:
        logging.info(">>> Nenhum arquivo .ret encontrado para mover")

def copiar_maior_arquivo(pasta_downloads, pasta_maior, pasta_destino, extensoes=None, timeout=30):
    if extensoes is None:
        extensoes = [".ret"]

    arquivos_ret_hoje = [
        os.path.join(pasta_destino, f)
        for f in os.listdir(pasta_destino)
        if f.endswith(".ret") and
        os.path.isfile(os.path.join(pasta_destino, f)) and
        datetime.fromtimestamp(os.path.getmtime(os.path.join(pasta_destino, f))).date() == datetime.today().date() and
        not padrao_duplicata.search(f)
    ]

    if arquivos_ret_hoje:
        # selecionar o maior arquivo
        maior_arquivo = max(arquivos_ret_hoje, key=lambda f: os.path.getsize(f))
        
        # copiar para a pasta_maior
        shutil.copy2(maior_arquivo, os.path.join(pasta_maior, os.path.basename(maior_arquivo)))
        logging.info(f">>> Maior arquivo de hoje ({os.path.basename(maior_arquivo)}) copiado para: {pasta_maior}")
    else:
        logging.info(">>> Nenhum arquivo encontrado para hoje.")
