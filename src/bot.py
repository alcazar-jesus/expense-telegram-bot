import sys

from pathlib import Path
import logging.config
import logging

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.settings import BASE_DIR, TOKEN
from src.handlers.router import register_all_handlers

from telegram.ext import ApplicationBuilder


# Definimos el logging para tener claro los logs y eso del bot:
log_cfg_path = BASE_DIR / "config" / "logging.conf"
logging.config.fileConfig(log_cfg_path, disable_existing_loggers=False)

# A partir de aquí puedo definir distintos loggers (objetos que permiten registrar
# mensajes y eventos durante la ejecución de una app, el logger se encarga de gestionarlos,
# los mensajes se envían a un handler que puede ser un archivo, la consola, etc.)
logger = logging.getLogger("expense_bot")

def main() -> None:
    """
    Función principal de la ejecución del bot
    """

    logger.info("Iniciando el Bot...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Aquí añadimos los distintos handlers ...


    logger.info("Bot iniciado, esperando los mensajes...")

    register_all_handlers(application)
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()