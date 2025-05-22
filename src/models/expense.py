from datetime import date, datetime
from dataclasses import dataclass, field
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
    _fecha: date = field(default=datetime.today().strftime('%d/%m/%Y'), init=False)
    _importe: float = None
    _tipo: str = ''
    _categoria: str = ''
    _descripcion: str = ''
    _quien: str = ''
    _viaje: Optional[str] = ''
    _anualizable: Optional[bool] = False    # Para futuro incluir esto también, indicador de si el gasto o el ingreso es anualizable 
                                            # (es decir, para el computo este gasto se debería anualizar, por ejemplo si son 120€, serían 12€ al mes).

    @property
    def fecha(self) -> float:
        return self._fecha
    @fecha.setter
    def fecha(self, value: str) -> date:
        try:
            value = datetime.strptime(value, '%d/%m/%Y')
        except ValueError:
            try:
                value = datetime.strptime(value, '%d/%m/%y')
            except ValueError as e:
                raise ValueError("La fecha tiene que ser en formato dd/mm/YYYY o en formato dd/mm/YY: {e}")
        self._fecha = value.strftime('%d/%m/%Y')  
    
    @property
    def importe(self) -> float:
        return self._importe
    
    @importe.setter
    def importe(self, value: str) -> float:
        try:
            value = float(value.replace(',', '.'))
        except Exception as e:
            raise ValueError(f"Tiene que ser un valor numérico: {e}")
        
        if value is None:
            raise ValueError("El importe no puede quedar vacío")
        elif value < 0:
            raise ValueError("El importe no puede ser negativo")
        self._importe = value  
    
    @property
    def tipo(self) -> str:
        return self._tipo
    
    @tipo.setter
    def tipo(self, value: str) -> str:
        if value is None:
            raise ValueError("El tipo no puede quedar vacío")
        self._tipo = value  
    
    @property
    def categoria(self) -> str:
        return self._categoria
    
    @categoria.setter
    def categoria(self, value: str) -> str:
        if value is None:
            raise ValueError("El concepto no puede quedar vacío")
        self._categoria = value  
        
    @property
    def descripcion(self) -> str:
        return self._descripcion
    
    @descripcion.setter
    def descripcion(self, value: str) -> str:
        if value is None:
            raise ValueError("La descripcion no puede quedar vacía")
        self._descripcion = value  
        
    @property
    def quien(self) -> str:
        return self._quien
    
    @quien.setter
    def quien(self, value: str) -> str:
        if value is None:
            raise ValueError("El quien no puede quedar vacío")
        self._quien = value  
        
    @property
    def viaje(self) -> str:
        return self._viaje
    
    @viaje.setter
    def viaje(self, value: str) -> str:
        self._viaje = value 
        
    @property
    def anualizable(self) -> str:
        return self._anualizable
    
    @anualizable.setter
    def anualizable(self, value: str) -> str:
        if value is None:
            raise ValueError("El quien no puede quedar vacío")
        self._anualizable = value 
        
    def __str__(self):
        return f"📅Fecha: {self.fecha}\n💰Importe: {self.importe}\n✒️Tipo: {self.tipo}\n📚Categoria: {self.categoria}\n📃Descripción: {self.descripcion}\n👣Con quién: {self.quien}\n✈️Nombre del viaje: {self.viaje or '-'}\n📊¿Es anualizable? {self.anualizable or '-'}"
    
    def to_csv_row(self) -> List[str]:
        return [str(self.user), self.fecha, str(self.importe), self.tipo, 
                self.categoria, self.descripcion, self.quien, 
                self.viaje or "", str(self.anualizable)]
    
    # Método de serialización para temas de deepcopy, que no de error
    def serialize(self) -> dict:
        return {
            "user": self.user,
            "_fecha": self._fecha,
            "_importe": self._importe,
            "_tipo": self._tipo,
            "_categoria": self._categoria,
            "_descripcion": self._descripcion,
            "_quien": self._quien,
            "_viaje": self._viaje,
            "_anualizable": self._anualizable,
        }

    @classmethod
    def deserialize(cls, data: dict) -> "Expense":
        obj = cls(user=data["user"])
        obj._fecha = data["_fecha"]
        obj._importe = data["_importe"]
        obj._tipo = data["_tipo"]
        obj._categoria = data["_categoria"]
        obj._descripcion = data["_descripcion"]
        obj._quien = data["_quien"]
        obj._viaje = data["_viaje"]
        obj._anualizable = data["_anualizable"]
        return obj

    # La función de guardar podría estar aquí como método de la clase (para poder hacer expense.save()),
    # pero entonces la clase ya no sería solo el modelo de datos sino que también se encargaría del I/O
    # y el formateo del csv. Además si mañana quiero migrar a SQLlite o a JSON tendría que modificar el 
    # modelo de datos (la clase Expense) en lugar de únicamente el módulo que se encarga de gestionarlo.
    # En la clase solo va a estar el modelo de datos y la lógica de validación/serialización.
    # Por tanto, la lógica de de I/O o de añadir más métodos como list_expense(), find_by_date(), ...
    # de eso se encargará la función externa en csv_utils.py o una clase más amplia llamada ExpenseRepository
    # que se podría encargar de estas lógicas (posible mejora a futuro).

