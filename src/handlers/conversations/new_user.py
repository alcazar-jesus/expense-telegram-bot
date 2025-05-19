import logging
from enum import IntEnum, auto
# IntEnum es una clase que crea enumeraciones cuyos valores son enteros, lo que significa que pueden ser utilizados en cálculos 
# y comparaciones como números enteros. auto, por otro lado, es una función que se usa para asignar automáticamente valores a 
# los miembros de una enumeración en orden creciente, comenzando en 1.

from src.utils.user_utils import check_user, add_user

from telegram import Update
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CommandHandler, 
    MessageHandler,
    filters
)

logger = logging.getLogger("expense_bot.handlers.commands")

class ConvState(IntEnum):
    NEW_USER_PWD = auto()


# Entry point del nuevo usuario:
async def nuevo_usuario_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Función que gestiona el registro de un nuevo usuario mediante el comando de /nuevo_usuario.

    Si el usuario está registrado, no tiene sentido que ejecute este comando, por lo que le responderá con un mensaje de
    "ya estás registrado, no te puedes volver a registrar". Si no está registrado, se registrará al usuario siempre y cuando
    ponga bien la contraseña.
    """

    user = update.effective_user

    if check_user(user.id):
        await update.message.reply_text(
            "⚠️ Uy, ya estabas registrado. Usa /start para continuar."
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "👮‍♀️ Por favor introduce la contraseña \n\n"
            "Utiliza /cancel para finalizar.",
        )
        return ConvState.NEW_USER_PWD
    
# Estado de NEW_USER_PWD
async def enter_pwd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Gestiona el estado de ver si la contraseña ha sido correcta o no 
    """

    user = update.effective_user
    user_pwd = update.message.text

    if add_user(user.id, user_pwd):

        logger.info("Usuario registrado con éxito: %s, %s", user.id, user.first_name)
        await update.message.reply_text(
            f"✅ Bienveni@ {user.first_name}! Ya puedes continuar :)"
        )

        return ConversationHandler.END
    else:
        logging.warning("Contraseña incorrecta de: %s %s", user.id, user.first_name)

        await update.message.reply_text(
            f"🙅 Ups! La contraseña no es correcta. Intentalo de nuevo"
        )
        return ConvState.NEW_USER_PWD


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Cancels and ends the conversation."""

    user = update.effective_user
    logging.info("User %s canceled the conversation.", user.first_name)

    await update.message.reply_text(
        "👋 Hasta luego %s!", user.first_name
    )
    context.user_data.clear()
    return ConversationHandler.END


conv_nuevo_usuario_handler = ConversationHandler(

        entry_points=[CommandHandler("nuevo_usuario", nuevo_usuario_entry)],
        states={
            ConvState.NEW_USER_PWD: [MessageHandler(~filters.COMMAND, enter_pwd)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,

    )
