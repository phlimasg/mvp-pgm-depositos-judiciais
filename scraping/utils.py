import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

def get_clickable_element(wait: WebDriverWait, by, value, retries=3):
    for tentativa in range(1, retries + 1):
        try:
            el = wait.until(EC.element_to_be_clickable((by, value)))
            return el
        except Exception as e:
            print(f"Tentativa {tentativa}/{retries} falhou para '{value}': {e}")
            time.sleep(1)
    raise Exception(f"Elemento {value} não encontrado após {retries} tentativas")

def get_element(wait: WebDriverWait, by, value, retries=3):
    for _ in range(retries):
        try:
            return wait.until(EC.presence_of_element_located((by, value)))
        except StaleElementReferenceException:
            time.sleep(1)
    raise Exception(f"Elemento {value} não encontrado após {retries} tentativas")

def get_elements(wait: WebDriverWait, by, value, retries=3):
    for _ in range(retries):
        try:
            return wait.until(EC.presence_of_all_elements_located((by, value)))
        except StaleElementReferenceException:
            time.sleep(1)
    raise Exception(f"Elementos {value} não encontrados após {retries} tentativas")
