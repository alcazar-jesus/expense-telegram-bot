import sys
import json

from pathlib import Path 
from typing import List

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.settings import BASE_DIR, DATA_PATH

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

CATS_PATH = DATA_PATH / "categories.json"

def load_categories(ind_cat: str = 'gasto') -> list[str]:
    """
    Función para cargar las categorías de los gastos o ingresos. Lee el JSON de categorías de la ruta CATS_PATH.

    Args:
        tipo (:obj:`str`): Indicador para ver si se cargan las categorías de gasto (ind_cat = 'gasto')
        o si se cargan las categorías de ingreso (ind_cat = 'ingreso) o la categoría de quien (ind_cat = 'quien').
        Posibles valores: 'gasto', 'ingreso', 'quien', 'all' (all para cargar todas)

    Returns:
        :obj:`list[str]`: Devuelve una lista con las categorías
    """
    CATS_PATH.parent.mkdir(parents=True, exist_ok=True) # Crea el directorio si no estuviera creado, si no no hace nada
    if not CATS_PATH.exists():
        # Si no existe crea una lista vacía
        categorias_por_defecto = {
            "gasto": [],
            "ingreso": [],
            "quien":[]
        }
        with open(CATS_PATH, "w", encoding="utf-8") as f:
            json.dump(categorias_por_defecto, f, ensure_ascii=False, indent=2)
    with open(CATS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
        # Seleccionamos el tipo de categorías en función de ind_cat
        if ind_cat == 'all':
            return data
        return data.get(ind_cat, [])

def add_category(name: str, ind_cat: str = 'gasto') -> bool:
    """
    Añade una categoría nueva al tipo especificado (por defecto 'gasto').
    Devuelve True si se añadió, False si ya existía.

    Args:
        name (str): Nombre de la categoría a añadir.
        tipo (str): Tipo de categoría ('gasto', 'ingreso', etc.)

    Returns:
        bool: True si se añadió correctamente, False si ya existía.
    """

    # Cargamos todas las categorías, ya que así es más fácil hacer el append:
    data = load_categories(ind_cat='all')
    if name in data[ind_cat]:
        return False

    # Añadimos la categoría:
    data[ind_cat].append(name)
    with open(CATS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return True

def chunk_list(lst: List, n: int) -> List[List]:
    """Divide una lista en sublistas de longitud n."""
    return [lst[i:i + n] for i in range(0, len(lst), n)]

def load_category_markup(ind_cat: str = 'gasto') -> InlineKeyboardMarkup:
    categories = load_categories(ind_cat)
    buttons = [
        InlineKeyboardButton(cat, callback_data=f"{cat.upper()}")
        for cat in categories
    ]
    keyboard = chunk_list(buttons, 3)
    return InlineKeyboardMarkup(keyboard)



if __name__ == '__main__':
    print(load_categories())
    print(add_category('prueba'))

