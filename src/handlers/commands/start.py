import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from src.utils.user_utils import check_user, load_users, add_user


logger = logging.getLogger("expense_bot.handlers.commands")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Esta es la función que gestionará el comando de inicio del bot /start.
    Lo primero que hará será recuperar la información del usuario (el id y el first_name) y mirar 
    si está registrado dentro de los usuarios permitidos. 

    De ser el caso empezará la conversación (Entrará en el estado principal de la ConversationHandler),
    si no está registrado le responderá con un "tienes que registrarte, usa el comando /registrar")
    """

    user = update.effective_user

    # Implementar la lógica de cargar los usuarios y ver si el usuario dado pertenece al grupo de usuarios.
    if check_user(user.id):
        # El usuario está registrado correctamente
        await update.message.reply_text(
            f'Hola {user.first_name}! Te voy a gestionar los gastos, ¿Qué quieres hacer?'
        )
    else:
        await update.message.reply_text(
            f"❌ Hola {user.first_name}! Parece que no estás entre los usuarios registrados. Por favor usa /nuevo_usuario para darte de alta :)"
        )

        logger.warning(f"Usuario no registrado {user.id} - {user.first_name} intentó usar /start.")



start_handler = CommandHandler("start", start_command)


