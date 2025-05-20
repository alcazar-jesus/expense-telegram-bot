import logging
from enum import IntEnum, auto

from src.utils.category_utils import load_categories, load_category_markup
from src.utils.user_utils import check_user 

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

logger = logging.getLogger("expense_bot.handlers.conversations")


class ConvState(IntEnum):
    """Gestiona los estados de la conversación"""
    SELECT_TYPE = auto()
    INCOME_ENTRY = auto()
    SPENDING_ENTRY = auto()
    ENTER_EXPENSE = auto()


# start_entry
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Esta es la función que gestionará el comando de inicio del bot /start.
    Lo primero que hará será recuperar la información del usuario (el id y el first_name) y mirar 
    si está registrado dentro de los usuarios permitidos. 

    De ser el caso empezará la conversación (Entrará en el estado principal de la ConversationHandler),
    si no está registrado le responderá con un "tienes que registrarte, usa el comando /registrar")

    Args:
        update (Update): 
        context (ContextTypes.DEFAULT_TYPE): 

    Returns:
        int: Estado de la conversación
    """
    # Nos traemos la info del usuario que se está comunicando
    user = update.effective_user

    logging.info(f"El usuario {user.id} está intentando acceder al bot")
    # Lo primero que comprobamos es si es un usuario registrado:
    if check_user(user.id):
        
        logging.info(f"El usuario {user.id} está registrado")
        # Generamos un botón para seleccionar una acción
        keyboard = [
        [InlineKeyboardButton("💸 Gasto", callback_data=str(ConvState.SPENDING_ENTRY))],
        [InlineKeyboardButton("💰 Ingreso", callback_data=str(ConvState.INCOME_ENTRY))],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    
        await update.message.reply_text(
            f'👋 Hola {user.first_name}! Te voy a gestionar los gastos, ¿Qué quieres añadir?', reply_markup=reply_markup
        )
        return ConvState.SELECT_TYPE
    
    else:
        await update.message.reply_text(
            f"❌ Hola {user.first_name}! Parece que no estás entre los usuarios registrados. Por favor usa /nuevo_usuario para darte de alta :)"
        )
        logger.warning(f"Usuario no registrado {user.id} - {user.first_name} intentó usar /start.")
        
        return ConversationHandler.END
    
# Estado de SELECT_TYPE
async def enter_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """gestiona el estado de SELECT_TYPE, vamos a pedir ingresar un gasto o un ingreso.

    Args:
        update (Update): _description_
        context (ContextTypes.DEFAULT_TYPE): _description_

    Returns:
        int: _description_
    """
    
    expense_type = update.callback_query.data
    user = update.effective_user
    
    context.user_data["tipo"] = expense_type
    
    if expense_type == str(ConvState.SPENDING_ENTRY):
        
        logging.info(f"El usuario {user.id} quiere añadir un gasto")
        context.user_data["tipo"] = "gasto"
        markup = load_category_markup(context.user_data["tipo"])
        
        await update.callback_query.edit_message_text(
            "Uyy cómo se va el dinero...💸 ¿Sobre qué es el gasto?",
            reply_markup=markup
            )
        
    elif expense_type == str(ConvState.INCOME_ENTRY):
        
        logging.info(f"El usuario {user.id} quiere añadir un ingreso")
        context.user_data["tipo"] = "ingreso"
        markup = load_category_markup(context.user_data["tipo"])
        
        await update.callback_query.edit_message_text(
            "Dineritooo 🤑 ¿De donde viene el ingreso?",
            reply_markup=markup
            )
        
    return ConvState.ENTER_EXPENSE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END

enter_expense = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ConvState.SELECT_TYPE: [CallbackQueryHandler(enter_expense, pattern=f"^{str(ConvState.INCOME_ENTRY)}$|^{str(ConvState.SPENDING_ENTRY)}$")],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
    
)

