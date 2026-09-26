import logging
import os
import smtplib
from email.mime.text import MIMEText
import socket
import datetime
from dotenv import load_dotenv

load_dotenv()

# ---------- CONFIGURAÇÃO ----------
GMAIL_USER = os.getenv("EMAIL_NAO_RESPONDA")
GMAIL_PASSWORD = os.getenv("SENHA_EMAIL_NAO_RESPONDA")
DESTINATARIOS = os.getenv("DESTINATARIOS")

# Converte string para lista
lista_destinatarios = [email.strip() for email in DESTINATARIOS.split(";")]

# ---------- FUNÇÃO BASE ----------
def enviar_email(html_content, assunto):
    """Função base para envio de e-mail via SMTP Gmail."""
    print(f"Tentando enviar e-mail: {assunto}")
    msg = MIMEText(html_content, 'html', 'utf-8')
    msg['From'] = GMAIL_USER
    msg['To'] = ", ".join(lista_destinatarios)
    msg['Subject'] = assunto
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, lista_destinatarios, msg.as_string())
        print("E-mail enviado com sucesso!")
        return True
    except smtplib.SMTPAuthenticationError:
        print("Erro de autenticação SMTP. Verifique usuário e senha ou use senha de app.")
        logging.error(f"❌ Erro de autenticação SMTP. Verifique usuário e senha ou use senha de app.")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        logging.error(f"❌ Erro ao enviar e-mail: {e}")
    finally:
        if 'server' in locals():
            server.quit()
    return False

# ---------- FUNÇÃO PARA SUCESSO ----------
def enviar_email_sucesso():
    """Envia e-mail informando que o Bot do DJO executou com sucesso."""
    assunto = f"[Bot DJO] Executado com Sucesso - {socket.gethostname()} - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    
    html_template = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color:#f4f4f4; padding:20px;">
        <div style="max-width:600px; margin:auto; background:#fff; padding:20px; border-radius:8px; box-shadow:0 4px 8px rgba(0,0,0,0.1);">
            <h2 style="color:green; text-align:center;">✔ Bot do DJO executou com sucesso!</h2>
            <p>Olá,</p>
            <p>O Bot do DJO/BB concluiu o processamento com sucesso.</p>
            <p>Todos os arquivos foram processados e salvos no destino configurado.</p>
            <p>Atenciosamente,<br>Equipe de TI - CTEC</p>
        </div>
    </body>
    </html>
    """
    
    return enviar_email(html_template, assunto)

# ---------- FUNÇÃO PARA ERRO ----------
def enviar_email_erro(mensagem_erro):
    """Envia e-mail informando que houve erro no Bot do DJO."""
    assunto = f"[Bot DJO] Erro durante execução depois de 3 tentativas - {socket.gethostname()} - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    
    html_template = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color:#f4f4f4; padding:20px;">
        <div style="max-width:600px; margin:auto; background:#fff; padding:20px; border-radius:8px; box-shadow:0 4px 8px rgba(0,0,0,0.1);">
            <h2 style="color:red; text-align:center;">❌ Erro no Bot do DJO!</h2>
            <p>Olá,</p>
            <p>O Bot do DJO/BB encontrou um erro durante a execução:</p>
            <div style="border-left: 4px solid red; padding-left:10px; background:#ffe6e6; margin:10px 0;">
                <pre>{mensagem_erro}</pre>
            </div>
            <p>Por favor, verifique o log e tome as devidas providências.</p>
            <p>Atenciosamente,<br>Equipe de TI - CTEC</p>
        </div>
    </body>
    </html>
    """
    
    return enviar_email(html_template, assunto)
