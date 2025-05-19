import yaml
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CONF_PATH = BASE_DIR / "config" / "config.yaml"


with open(CONF_PATH, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)


TOKEN = cfg["telegram_token"]
DATA_PATH = BASE_DIR / cfg["data_path"]
DATA_FILE_PATH = BASE_DIR / cfg['data_file_path']

if __name__ == '__main__':

    print(TOKEN)
    print(BASE_DIR)
    print(CONF_PATH)
    print(DATA_PATH)
