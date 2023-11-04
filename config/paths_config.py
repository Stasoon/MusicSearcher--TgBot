from pathlib import Path


class PathsConfig:
    WORKDIR = Path(__file__).parent
    WEBDRIVER_PATH = WORKDIR / 'webdriver/chromedriver.exe'
    LOCALES_DIR = WORKDIR.parent/'locales'
    CSV_FOLDER = './db_exports'
