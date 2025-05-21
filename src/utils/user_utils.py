import json
from pathlib import Path

from src.settings import BASE_DIR, DATA_PATH, REGISTER_PWD


def load_users() -> list[int]: 
    """
    Función que carga la lista de usuaios del json de usuarios
    """
    users_file = DATA_PATH / "users.json"

    with open(users_file, "r") as f:
        return json.load(f)


def check_user(user_id: int) -> bool:
    """
    Función que checkea si un usuario está registrado o no,
    carga los usuarios y lo comprueba, implementación por no repetir todo el rato esta acción.
    """
    users = load_users()
    if user_id in users:
        return True 
    else:
        return False      

def add_user(user_id: int, in_pwd: str) -> bool:
    """
    Añade un nuevo usuario si la contraseña introducida coincide con la contraseña REGISTER_PWD
    """

    users_file = DATA_PATH / "users.json"

    if in_pwd != REGISTER_PWD:
        return False
    
    users = load_users()

    if user_id in users:
        return False
    
    users.append(user_id)

    with open(users_file, "w") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    
    return True

