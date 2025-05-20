import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

env_path = BASE_DIR / "config" / ".env"
load_dotenv(dotenv_path=env_path)


TOKEN = os.getenv('API_TOKEN')
DATA_PATH = BASE_DIR / "data"
DATA_FILE_PATH = BASE_DIR / "data" / "gastos.csv"
REGISTER_PWD = os.getenv('REGISTER_PWD')


if __name__ == '__main__':

    print(TOKEN)
    print(BASE_DIR)
    print(DATA_PATH)
