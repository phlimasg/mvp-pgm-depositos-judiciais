import os
import time
import traceback
import logging
import undetected_chromedriver as uc
import chromedriver_autoinstaller
from mail import enviar_email_erro, enviar_email_sucesso
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from upload_api import enviar_arquivos_para_api
from utils import get_clickable_element, get_element
from downloads import copiar_maior_arquivo, mover_arquivos_lidos
from djo190 import selecionar_linhas_djo190
from version_verifier import check_version_compatibility

load_dotenv()

# Logs no console + arquivo em PASTA_DESTINO
_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
_handlers = [logging.StreamHandler()]
log_dir = os.getenv("PASTA_DESTINO", ".")
log_file = os.path.join(log_dir, "bot_djo.log")
try:
    os.makedirs(log_dir, exist_ok=True)
    _handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
except OSError as e:
    raise PermissionError(
        f"Sem permissão para gravar log em PASTA_DESTINO ({log_file}): {e}"
    ) from e

logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT, handlers=_handlers)

def executar_bot():
    """Executa uma vez o fluxo principal do bot"""
    perfil_chrome = os.path.join(os.getenv("PASTA_DESTINO", "."), "chrome_profile")
    os.makedirs(perfil_chrome, exist_ok=True)

    service = ChromeService(ChromeDriverManager().install())
    options = uc.ChromeOptions()
    check_version_compatibility()

    # Usa o perfil persistente
    options.add_argument(f"--user-data-dir={perfil_chrome}")

    # NÃO desabilitar extensions/plugins: o login PJ do BB depende do
    # módulo local (WebSocket em 127.0.0.1:31989/30900) e dos scripts
    # ApjCoreUtils/GcsSdk. Com --disable-extensions o Chrome normal
    # autentica, mas o Chromedriver cai no erro A999-999.
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")

    prefs = {
        "profile.default_content_setting_values.notifications": 1,
        "profile.default_content_setting_values.geolocation": 1,
        "profile.default_content_setting_values.media_stream_mic": 1,
        "profile.default_content_setting_values.media_stream_camera": 1,
    }
    options.add_experimental_option("prefs", prefs)

    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-permission-request-popups")
    options.add_argument("--autoplay-policy=user-gesture-required")

    try:
        version = chromedriver_autoinstaller.get_chrome_version().split(".")[0]
        version = int(version)
    except Exception:
        version = None

    usuario_api = os.getenv("API_USERNAME")
    senha_api = os.getenv("API_PASSWORD_PROD")  
    url_api = os.getenv("URL_API_PROD")  

    chave_j = os.getenv("CHAVE_J")
    senha = os.getenv("SENHA")
    pasta_downloads = os.getenv("PASTA_DOWNLOADS")
    pasta_maior = os.getenv("PASTA_MAIOR")
    pasta_destino = os.getenv("PASTA_DESTINO")

    # Cria apenas uma vez
    if version:
        driver = uc.Chrome(service=service, version_main=version, options=options)
    else:
        driver = uc.Chrome(service=service, options=options)

    wait = WebDriverWait(driver, 120)

    try:
        url = "https://autoatendimento2.bb.com.br/apf-apj-acesso/"
        driver.get(url)
        time.sleep(3)
        
        # Tenta fechar qualquer popup/alert que apareça
        try:
            alert = WebDriverWait(driver, 2).until(lambda d: d.switch_to.alert)
            alert.accept()
        except:
            pass
        
        # Remove qualquer overlay ou popup via JavaScript
        try:
            driver.execute_script("""
                // Procura e remove overlays/modals de permissão
                let modals = document.querySelectorAll('[role="dialog"], .modal, .popup, [class*="permission"], [class*="popup"]');
                modals.forEach(modal => modal.remove());
                
                // Tenta clicar em botões que concedem permissão
                let buttons = document.querySelectorAll('button');
                buttons.forEach(btn => {
                    let text = btn.textContent.toLowerCase();
                    if (text.includes('permitir') || text.includes('allow') || text.includes('aceitar') || text.includes('accept')) {
                        btn.click();
                    }
                });
            """)
        except:
            pass

        # Espera até o campo existir
        get_element(wait, "id", "identificador")

        # Aguarda scripts do módulo local (ApjCoreUtils/GcsSdk). Sem eles o BB
        # devolve A999-999 mesmo com chave/senha corretas.
        sdk_ok = False
        for _ in range(30):
            sdk_ok = driver.execute_script(
                "return typeof ApjCoreUtils !== 'undefined' || typeof GcsSdk !== 'undefined';"
            )
            if sdk_ok:
                break
            time.sleep(1)
        if not sdk_ok:
            logging.warning(
                ">>> Scripts de segurança do BB (ApjCoreUtils/GcsSdk) não carregaram. "
                "Verifique o módulo local e se o Chrome normal está fechado."
            )

        # Login
        try:
            get_clickable_element(wait, "css selector", ".abrirListaSegmento-login-bb").click()
            get_clickable_element(wait, "xpath", "//li[@ng-click='acessoCorrentistaGoverno(true)']").click()
        except Exception:
            pass

        get_clickable_element(wait, "id", "identificador").send_keys(chave_j)
        get_clickable_element(wait, "id", "senhaChaveJ").send_keys(senha)

        try:
            checkbox = get_clickable_element(wait, "css selector", "input[type='checkbox']")
            if not checkbox.is_selected():
                checkbox.click()
        except Exception:
            pass

        get_clickable_element(wait, "id", "submit").click()

        logging.info(">>> Login realizado, aguardando redirecionamento...")

        time.sleep(10)

        # Detecta o modal A999-999 (falha do módulo/bridge local)
        try:
            page_text = driver.find_element("tag name", "body").text
            if "A999-999" in page_text or "erro desconhecido" in page_text.lower():
                raise RuntimeError(
                    "BB retornou A999-999 no login. Chrome normal autentica, mas o "
                    "Chromedriver não conectou ao módulo local (127.0.0.1:31989/30900). "
                    "Feche todas as janelas do Chrome, confirme o módulo de segurança "
                    "na bandeja e rode o bot de novo."
                )
        except RuntimeError:
            raise
        except Exception:
            pass

        url_atual = driver.current_url
        url_base = url_atual.split("/template")[0] + "/template"
        print(f">>> URL base após login: {url_base}")

        url_djo190 = url_base + "/~2FtransferenciaArquivos~2FTARetorno-1.bb"

        # Seleção e cópia do arquivo
        selecionar_linhas_djo190(driver, wait, pasta_destino, pasta_downloads, url_atual, url_djo190)
        copiar_maior_arquivo(pasta_downloads, pasta_maior, pasta_destino)

        enviar_arquivos_para_api(pasta_destino, url_api, usuario_api, senha_api)

        logging.info(">>> Processo concluído com sucesso!")
        
        # Move os arquivos .ret lidos para a pasta DJOLidos
        mover_arquivos_lidos(pasta_destino)
        
        enviar_email_sucesso()

    finally:
        driver.quit()

# ======= LOOP DE TENTATIVAS =======
if __name__ == "__main__":
    print(">>> Iniciando bot_djo...")
    MAX_TENTATIVAS = 3
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            logging.info(f">>> Iniciando tentativa {tentativa}/{MAX_TENTATIVAS}")
            executar_bot()
            break  # se deu certo, sai do loop
        except Exception:
            erro = traceback.format_exc()
            logging.error(f">>> Erro na tentativa {tentativa}: {erro}")
            print(erro)

            if tentativa == MAX_TENTATIVAS:
                print(">>> Todas as tentativas falharam.")
                enviar_email_erro(erro)
            else:
                print(f">>> Tentativa {tentativa} falhou, tentando novamente em 10s...")
                time.sleep(10)
