import csv
import pandas as pd

from math import isnan
from datetime import datetime
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

def get_last_trip(path: Path = DATA_FILE_PATH, n: int = 1) -> str:
    """Se trae el último viaje dentro del último mes (por defecto)

    Args:
        path (Path, optional): Path al csv de gastos. Defaults to DATA_FILE_PATH.
        n (int, optional): Número de meses que se trae. Defaults to 1.

    Returns:
        str: El nombre del último viaje
    """
    df = pd.read_csv(path, sep=';')
    if df.empty:
        return None
    df = df[(datetime.today() - df['fecha']).dt.days < n*30]
    if df.empty or isnan(df['viaje'].iloc[-1]):
        return None
    return df['viaje'].iloc[-1]
