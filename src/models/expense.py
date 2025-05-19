from datetime import date
from dataclasses import dataclass
# IMporta el decorador dataclass, que permite crear clases de datos de forma más sencilla 
# generando automáticamente métodos como __init__, __repr__, __eq__, basados en atributos de la clase

from typing import Optional, List 
# La librería typing permite añadir anotaciones de tipo a variables, funciones y estructuras.
# esto mejora la legibilidad y la mantenibilidad del código, así como facilitar el uso de herramientas
# de análisis estadístico. 


@dataclass
class Expense:
    """
    Clase para guardar el registro de gastos.

    Tiene un método para convertir los datos en una lista para luego agregarla al csv
    """
    user: str
    fecha: date
    importe: float
    tipo: str
    concepto: str
    descripcion: str
    quien: str
    viaje: Optional[str] = None
    anualizable: Optional[bool] = False     # Para futuro incluir esto también, indicador de si el gasto o el ingreso es anualizable 
                                            # (es decir, para el computo este gasto se debería anualizar, por ejemplo si son 120€, serían 12€ al mes).

    def to_csv_row(self) -> List[str]:
        return [self.user, self.fecha, str(self.importe), self.tipo, 
                self.concepto, self.descripcion, self.quien, 
                self.viaje or "", self.anualizable]

    # La función de guardar podría estar aquí como método de la clase (para poder hacer expense.save()),
    # pero entonces la clase ya no sería solo el modelo de datos sino que también se encargaría del I/O
    # y el formateo del csv. Además si mañana quiero migrar a SQLlite o a JSON tendría que modificar el 
    # modelo de datos (la clase Expense) en lugar de únicamente el módulo que se encarga de gestionarlo.
    # En la clase solo va a estar el modelo de datos y la lógica de validación/serialización.
    # Por tanto, la lógica de de I/O o de añadir más métodos como list_expense(), find_by_date(), ...
    # de eso se encargará la función externa en csv_utils.py o una clase más amplia llamada ExpenseRepository
    # que se podría encargar de estas lógicas (posible mejora a futuro).

