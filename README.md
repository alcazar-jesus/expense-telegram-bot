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
├── .git/                       # repositorio Git
├── .gitignore                  # Ignorar venv, __pycache__, CSV de datos, etc.
├── README.md                   # Documentación del proyecto
├── .python-version             # Versión de Python gestionada por pyenv (3.13.3)
├── requirements.txt            # Dependencias del proyecto
├── venv/                       # Entorno virtual creado con pyenv+venv
│
├── config/
│   ├── .env                    # Token de Telegram, contraseña para nuevos usuarios
│   └── logging.conf            # Configuración de logging
│
├── data/
│   └── expenses.csv            # CSV de datos (gestión: header si no existe)
│   └── users.json              # JSON con info de usuarios
│
├── src/
│   ├── bot.py                  # Punto de entrada: arranca el updater y dispatcher
│   ├── handlers/
│   │   ├── commands/           # Carpeta para guardar todos los códigos que gestionan comandos
|   |   |   ├── start.py  
|   |   |   └── new_category.py 
|   |   ├── conversations/      # Carpeta para guardar todos los códigos que gestionan conversaciones
│   │   |   ├── new_user.py 
│   │   |   ├──  enter_expense.py    
|   |   |   └── new_category.py 
|   |   └── router.py           # Código que añade todos los handlers a la app
|   |
│   ├── models/
│   │   └── expense.py          # Clase Expense, validación de datos, serialización a CSV
│   ├── utils/
│   │   ├── category_utils.py   # Funciones de lectura/escritura en CSV
│   │   ├── csv_utils.py        # Validación de fechas, importes, categorías
│   │   └── user_utils.py       # Formatea mensajes, fechas, etc.
│   └── settings.py             # Carga de config.yaml
│
└── tests/
    ├── test_models.py
    ├── test_utils.py
    └── test_handlers.py


```

---

# TO DO LIST

- [x] Estructura del proyecto montada
- [x] Inicialización del bot
- [x] Gestión de usuarios v1
- [ ] Conversación para añadir un gasto
    - [x] Añadir gasto/ingreso
    - [x] Solo ir al estado de introducior nombre de viaje si es categoría viaje
    - [ ] Poder hacer modificaciones
        - [ ] Poder modificar fecha
        - [ ] Modificar categoría (y en el momento añadir una nueva categoría)
    - [x] Confirmación del gasto
    - [ ] Añadir nuevas categorías
    - [x] Lógica de viajes (si la categoría es viajes por defecto tomar el último viaje)
    - [x] Tomar el último viaje de los últimos dos meses.
    - [ ] Después de gasto: "Ouch ese gasto duele, es 2 veces mayor que la media" (si el gasto es muy grande)
    - [x] Chistes de cuñado.
    - [x] Arreglar problema del guardado (no lo pone en nueva linea)
    - [ ] Opción de ir al paso anterior.
- [ ] Añadir test unitarios


### Características futuras

- [ ] Ver estadísticas de gastos
- [ ] Listar últimos gastos
- [ ] Poder eliminar algún gasto que esté mal 
    - [ ] Eliminar el último gasto
    - [ ] Eliminar un gasto en específico
    - [ ] Poder modificar un gasto
- [ ] Migrar a SQL las tablas
- [ ] Añandir "gastos" de inversiones
    - [ ] Nueva categoría que sea "Inversión"
    - [ ] Calcular rentabilidades de las inversiones
    - [ ] Hacer seguimiento de las inversiones
- [ ] Hacer predicción de gastos según mis gastos actuales
    - [ ] Capacidad de enviar notificaciones si estoy gastando más de lo habitual
    - [ ] Enviar notificaciones si he gastado poco un mes
    - [ ] Enviar notificación si no he apuntado algún gasto este mes (los ingresos, algún gasto recurrente, etc.)
- [ ] Poder subir gastos "de golpe".
    - [ ] Subir un csv y que apunte los gastos que no estén ya apuntados
    - [ ] Poder pasar un enlace a un google sheet y que lea los gastos de ahí


#### Características muy futuras
 
- [ ] Capacidad de entender lenguaje natural
    - [ ] Que me mande a una conversación u a otra según lo que le diga ("añadir gasto", "ver estadísticas", ....), pero lo que le diga es lenguaje natural, no cosas predefinidas.
- [ ] Poder subir foto de recibo y que registre automáticamente el gasto


---
* **requirements.txt**: Lista de dependencias instaladas en el entorno virtual. Se genera con `pip freeze > requirements.txt` y permite reproducir el entorno con `pip install -r requirements.txt`.

* **Handlers**: Cada paso de la conversación (pedir fecha, importe, tipo, etc.) se gestiona en un módulo separado dentro de `handlers/`. Esto facilita la mantenibilidad y escalabilidad del bot.


---

