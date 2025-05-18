# Bot de Gastos

Bot de Telegram para registrar gastos e ingresos de forma sencilla y estructurada. Almacena los registros en un archivo CSV y gestiona usuarios en un JSON.

### Descripción

Este proyecto es un bot de Telegram escrito en Python sin componentes de IA. Permite al usuario guardar sus transacciones diarias (gastos e ingresos) especificando:

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
my-spend-bot/
├── data/                  # Datos de la aplicación
│   ├── records.csv        # CSV con los registros [IGNORADO POR GIT]
│   └── users.json         # JSON con info de usuarios [IGNORADO POR GIT]
├── logs/                  # Ficheros de registro (logging)
│   └── bot.log            # Archivo de log [IGNORADO POR GIT]
├── src/
│   └── spendbot/          # Código fuente
│       ├── __main__.py    # Punto de entrada: arranca el bot
│       ├── config.py      # Variables de entorno y rutas de ficheros
│       ├── storage.py     # Lectura/escritura en CSV/JSON
│       ├── models.py      # Definición de la clase Record
│       ├── handlers/      # Módulos de manejo de cada paso del diálogo
│       │   ├── start.py
│       │   ├── fecha.py
│       │   ├── importe.py
│       │   ├── tipo.py
│       │   ├── categoria.py
│       │   ├── viaje.py
│       │   ├── descripcion.py
│       │   ├── quien.py
│       │   └── confirmacion.py
│       └── utils.py       # Funciones auxiliares (validaciones, parseos)
├── .env                   # Variables de entorno (BOT_TOKEN) [IGNORADO POR GIT]
├── .gitignore             # Archivos y carpetas a ignorar por Git
├── requirements.txt       # Dependencias del proyecto
└── README.md              # Documentación del proyecto
```

### Conceptos clave

* **Entorno virtual (`venv`)**: Aísla las dependencias de tu proyecto para evitar conflictos con otros proyectos. Se crea con `python3 -m venv venv` y se activa con `source venv/bin/activate`.

* **requirements.txt**: Lista de dependencias instaladas en el entorno virtual. Se genera con `pip freeze > requirements.txt` y permite reproducir el entorno con `pip install -r requirements.txt`.

* **Archivo `.env`**: Contiene variables de entorno (p. ej. `BOT_TOKEN`) que no deben compartirse en el repositorio. Se carga al iniciar la aplicación mediante la librería `python-dotenv`.

* **Logging**: Registro de eventos de la aplicación (errores, acciones) en `logs/bot.log` usando el módulo estándar `logging` de Python.

* **Handlers**: Cada paso de la conversación (pedir fecha, importe, tipo, etc.) se gestiona en un módulo separado dentro de `handlers/`. Esto facilita la mantenibilidad y escalabilidad del bot.

* **CSV y JSON**: Formatos de almacenamiento de datos. Usamos CSV para los registros de transacciones y JSON para datos de usuarios.

---

Con este README ya tienes una visión general de la estructura y los componentes del proyecto. ¡Manos a la obra!
