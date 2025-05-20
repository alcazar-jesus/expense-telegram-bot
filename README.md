# Bot de Gastos

Bot de Telegram para registrar gastos e ingresos de forma sencilla y estructurada. Almacena los registros en un archivo CSV y gestiona usuarios en un JSON.

### Descripción

Este proyecto es un bot de Telegram escrito en Python. Permite al usuario guardar sus transacciones diarias (gastos e ingresos) especificando:

* **Fecha** (YYYY-MM-DD)
* **Importe**
* **Tipo** (`expense` o `income`)
* **Categoría** (predefinida, p. ej. Alimentación, Transporte, Viaje, etc.)
* **Descripción** (texto libre)
* **Con quién** (persona predefinida)
* **Viaje** (solo para categoría "Viaje")

Los registros se escriben en `data/records.csv`. La información de usuarios se guarda en `data/users.json`.

### Estructura del proyecto

```
expense-telegram-bot/
├── .git/                   # repositorio Git
├── .gitignore              # Ignorar venv, __pycache__, CSV de datos, etc.
├── README.md               # Documentación del proyecto
├── .python-version         # Versión de Python gestionada por pyenv (3.13.3)
├── requirements.txt        # Dependencias del proyecto
├── venv/                   # Entorno virtual creado con pyenv+venv
│
├── config/
│   ├── config.yaml         # Token de Telegram, rutas de archivos, categorías, etc.
│   └── logging.conf        # Configuración de logging
│
├── data/
│   └── expenses.csv        # CSV de datos (gestión: header si no existe)
│   └── users.json          # JSON con info de usuarios
│
├── src/
│   ├── bot.py              # Punto de entrada: arranca el updater y dispatcher
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── conversation.py # Lógica de estados y handlers de la conversación
│   │   └── commands.py     # Handlers de comandos (/start, /help, /reporte)
│   ├── models/
│   │   └── expense.py      # Clase Expense, validación de datos, serialización a CSV
│   ├── utils/
│   │   ├── csv_utils.py    # Funciones de lectura/escritura en CSV
│   │   ├── validators.py   # Validación de fechas, importes, categorías
│   │   └── formatter.py    # Formatea mensajes, fechas, etc.
│   └── settings.py         # Carga de config.yaml
│
└── tests/
    ├── test_models.py
    ├── test_utils.py
    └── test_handlers.py



```



* **requirements.txt**: Lista de dependencias instaladas en el entorno virtual. Se genera con `pip freeze > requirements.txt` y permite reproducir el entorno con `pip install -r requirements.txt`.

* **Handlers**: Cada paso de la conversación (pedir fecha, importe, tipo, etc.) se gestiona en un módulo separado dentro de `handlers/`. Esto facilita la mantenibilidad y escalabilidad del bot.


---
