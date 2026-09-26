import logging
import os
usuario = os.getlogin()
import winreg
import re

def get_chrome_version():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Google\Chrome\BLBeacon"
        )
        version, _ = winreg.QueryValueEx(key, "version")
        winreg.CloseKey(key)

        match = re.match(r"(\d+)\.", version)
        if match:
            return match.group(1)  # ex: "142"

        return None

    except FileNotFoundError:
        return None


def get_chromedriver_major_versions():
    diretorio_chromedriver = f'C:\\Users\\{usuario}\\.wdm\\drivers\\chromedriver\\win64'

    if not os.path.exists(diretorio_chromedriver):
        return []

    versoes = [
        pasta.split('.')[0]
        for pasta in os.listdir(diretorio_chromedriver)
        if os.path.isdir(os.path.join(diretorio_chromedriver, pasta))
    ]

    return sorted(set(versoes), key=int)


def check_version_compatibility():
    chrome_v = get_chrome_version()
    driver_v = get_chromedriver_major_versions()

    if chrome_v and chrome_v in driver_v:
        msg = f"Versoes compativeis (Chrome {chrome_v})."
        print(f"✅ {msg}")
        logging.info(msg)
        return

    msg = (
        f"Chrome={chrome_v}, drivers em cache={driver_v}. "
        "O undetected-chromedriver vai baixar/usar a versao certa."
    )
    print(f"⚠ {msg}")
    logging.warning(msg)
