import csv
import pandas as pd

from pathlib import Path
from src.settings import BASE_DIR, DATA_FILE_PATH
from src.models.expense import Expense


def save_expense(expense: Expense, path: Path = DATA_FILE_PATH) -> None:
    """
    Función que guarda el gasto dado por el objeto expense al csv
    """
    # Comprobamos que el path existe:
    first = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True) # si no existe lo creamos
    with open(path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        print(first)
        if first:
            writer.writerow(["user","fecha","importe","tipo","concepto","descripcion","quien","viaje","anualizable"])

        writer.writerow(expense.to_csv_row())

def get_last_trip(path: Path = DATA_FILE_PATH) -> str:
    """_summary_

    Args:
        path (Path, optional): _description_. Defaults to DATA_FILE_PATH.

    Returns:
        str: _description_
    """
    df = pd.read_csv(path, sep=';')
    if df.empty:
        return None
    return df['viaje'].iloc[-1]
