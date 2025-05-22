import logging
import random
from datetime import datetime
from enum import Enum, IntEnum, auto

from src.settings import DATA_FILE_PATH
from src.utils.category_utils import load_categories, load_category_markup
from src.utils.user_utils import check_user 
from src.utils.csv_utils import get_last_trip, save_expense
from src.models.expense import Expense
from src.utils.constantes import *

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
    START = auto()
    SELECT_TYPE = auto()
    INCOME_ENTRY = auto()
    SPENDING_ENTRY = auto()
    ENTER_EXPENSE = auto()
    ENTER_DESCRIPTION = auto()
    ENTER_WHO = auto()
    ENTER_TRIP = auto()
    CONFIRM = auto()
    MODIFY = auto()
    SAVE = auto()
    ENTER_DATE = auto()
    YES = auto()
    NO = auto()

LABELS_ConvState = {
    ConvState.INCOME_ENTRY: 'ingreso',
    ConvState.SPENDING_ENTRY: 'gasto',
}

def yes_no_button():
    return InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✅ Sí", callback_data=str(ConvState.YES)),
                        InlineKeyboardButton("❌ No", callback_data=str(ConvState.NO))
                    ]
                ]
            )
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
    
    # Lo primero que hago es registrar el estado en el que está, para ello hay una lista que lleva este registro
    # la cabeza de la lista es el estado actual. Si vuelvo a un estado anterior la cabeza de la lista se mueve 
    # un registro a la izquierda y se borra el estado en el que estaba, es decir, se hacer un drop del estado anterior.
    context.user_data['states'] = [ConvState.START]
    
    
    # Nos traemos la info del usuario que se está comunicando
    user = update.effective_user

    logger.info(f"El usuario {user.id} está intentando acceder al bot")
    # Lo primero que comprobamos es si es un usuario registrado:
    if check_user(user.id):
        
        logger.info(f"El usuario {user.id} está registrado")
        
        context.user_data["expense_obj"] = Expense(user.id)
        
        # Generamos un botón para seleccionar una acción
        keyboard = [
        [InlineKeyboardButton("💸 Gasto", callback_data=str(ConvState.SPENDING_ENTRY))],
        [InlineKeyboardButton("💰 Ingreso", callback_data=str(ConvState.INCOME_ENTRY))],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    
        await update.message.reply_text(
            f'👋 Hola {user.first_name}! Te voy a gestionar los gastos, ¿Qué quieres añadir?', reply_markup=reply_markup
        )
        return ConvState.ENTER_EXPENSE
    
    else:
        await update.message.reply_text(
            f"❌ Hola {user.first_name}! Parece que no estás entre los usuarios registrados. Por favor usa /nuevo_usuario para darte de alta :)"
        )
        logger.warning(f"Usuario no registrado {user.id} - {user.first_name} intentó usar /start.")
        
        return ConversationHandler.END

async def enter_import(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gestiona la entrada del importe, primero recupera el tipo, que
        el usuario ha introducido en el paso anterior y luego manda el mensaje para guardar el 
        importe

    Args:
        update (Update): _description_
        contextContextTypes (_type_): _description_

    Returns:
        int: _description_
    """
    # Actualizo la lista de estados:
    context.user_data['states'].append(ConvState.ENTER_EXPENSE)
    
    
    expense_type = LABELS_ConvState[int(update.callback_query.data)]
    user = update.effective_user
    
    context.user_data["expense_obj"].tipo = expense_type # He cambiado ConvState.SPENDING_ENTRY por su valor correspondiente
    
    logger.info(f"El usuario {user.id} quiere añadir un {expense_type}")

    if expense_type == LABELS_ConvState[int(ConvState.SPENDING_ENTRY)]:
        await update.callback_query.edit_message_text(
            f"{random.choice(EMOJIS_GASTOS)} {random.choice(CUNADO_CHISTES_GASTOS)}\n\n{random.choice(FRASES_PEDIR_GASTO)}",
            )
        
    elif expense_type == LABELS_ConvState[int(ConvState.INCOME_ENTRY)]:
        await update.callback_query.edit_message_text(
            f"{random.choice(EMOJIS_INGRESOS)} {random.choice(CUNADO_CHISTES_INGRESO)}\n\n{random.choice(FRASES_PEDIR_INGRESO)}",
            )    
    return ConvState.SELECT_TYPE

# Estado de SELECT_TYPE
async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gestiona la entrada de la categoría, primero recupera el importe, que
        el usuario ha introducido en el paso anterior y luego manda el mensaje para guardar la 
        categoría

    Args:
        update (Update): _description_
        context (ContextTypes.DEFAULT_TYPE): _description_

    Returns:
        int: _description_
    """
    
    # Actualizo el estado:
    context.user_data['states'].append(ConvState.SELECT_TYPE)
    
    importe = update.message.text
    user = update.effective_user
    try:
        context.user_data['expense_obj'].importe = importe
    except Exception as e:
        logger.error(f"El usuario {user.id} añade un {context.user_data['expense_obj'].tipo} incorrecto: {importe}. Error: {e}")
        
        await update.message.reply_text(
            f"Vaya, el importe de {importe} es incorrecto, asegurate de que no es negativo o que es un valor numérico!"
        )
        return ConvState.SELECT_TYPE
     
    logger.info(f"El usuario {user.id} quiere añadir un {context.user_data['expense_obj'].tipo}: {importe}")
    
    
    # Función para generar el KeyboardMarkup
    markup = load_category_markup(context.user_data['expense_obj'].tipo)
    
    await update.message.reply_text(
            f"👀 Tomo nota! ¿Cuál es el concepto del {context.user_data['expense_obj'].tipo}?",
            reply_markup=markup
        )
    return ConvState.ENTER_DESCRIPTION

async def enter_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gestionamos el ingreso de la categoría y lanzamos para preguntar sobre la descricpión
    en caso de ser de la categoría Viajes entonces se preguntará por el nombre/Identificador del viaje

    Args:
        update (Update): _description_
        context (ContextTypes.DEFAULT_TYPE): _description_

    Returns:
        int: Estado
    """
    
    # Actualizo el estado:
    context.user_data['states'].append(ConvState.ENTER_DESCRIPTION)
    
    cat = update.callback_query.data
    print(cat)
    user = update.effective_user
    
    context.user_data['expense_obj'].categoria = cat
    
    logger.info(f"El usuario {user.id} añade el gasto a la categoría {context.user_data['expense_obj'].categoria}")
    # Si la categoría es "Viajes" entonces se preguntará por el nombre/identificador del viaje, 
    # si no se pasará a preguntar por la descripción directamente
    if cat != 'Viajes':
        # Si es distinto de "Viajes", pedimos que nos diga la descripción y pasamos de estado
        await update.callback_query.edit_message_text(
                f"🎯Introduce una breve descripción del {context.user_data['expense_obj'].tipo}:"
            )
        return ConvState.ENTER_WHO
    else:
        # Obtenemos el último viaje y preguntamos por si es ese el viaje sobre el que es el gasto,
        # en caso de que sea lo anotamos y pasamos al siguiente caso.
        # Si la respuesta es no, apuntamos el nuevo viaje.
        last_trip = get_last_trip(DATA_FILE_PATH)
        if last_trip:
            # Si hay un último viaje (en los últimos días) preguntamos si es de este viaje, si no pues apuntamos uno nuevo
            # Queda la parte de ver los x días.
            
            # Creamo un botón de Sí/No.
            markup = yes_no_button()
            
            context.user_data['expense_obj'].viaje = last_trip
            
            await update.callback_query.edit_message_text(
                f"🛫Ole ole viajecito!! El viaje es {last_trip}?",
                reply_markup=markup
            )
            return ConvState.ENTER_TRIP
            
        else:
            await update.callback_query.edit_message_text(
                f"🛫Ole ole viajecito!! Introduce el viaje",
            )
            return ConvState.ENTER_TRIP
            
async def enter_description_from_trip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Estamos gestionando el nombre del viaje, lo primero que hace ha sido recuperar el último viaje y pregunta por si es ese el viaje,
    de ser que sí (respondido en el paso anterior) en esta función se registra y se pregunta por la descripción. De ser que no, se
    pregunta por el nombre del viaje y se vuelve a este caso. Si no había un viaje previo que tomar, en el paso previo se había preguntado 
    por el nombre del viaje por lo que en este paso se pregunta por la descripción.

    Args:
        update (Update): _description_
        context (ContextTypes.DEFAULT_TYPE): _description_

    Returns:
        int: _description_
    """
    # Actualizo el estado:
    context.user_data['states'].append(ConvState.ENTER_TRIP)
    
    if update.callback_query:
        # Viene del markup
        trip = update.callback_query.data
        
        if trip == str(ConvState.YES):
            # En el paso anterior hemos guardado el viaje por lo que no hay que hacer nada (preguntar por la descripción)
            await update.callback_query.edit_message_text(
                f"🎯Introduce una breve descripción del {context.user_data['expense_obj'].tipo}:"
            )
            return ConvState.ENTER_WHO
        else:
            # Preguntamos por el viaje:
            context.user_data['expense_obj'].viaje = None
            
            await update.callback_query.edit_message_text(
                    f"🛫Vale, pues introduce el viaje:",
                )
            return ConvState.ENTER_TRIP
    else:
        # Viene de escribir el viaje
        context.user_data['expense_obj'].viaje = update.message.text
        
        await update.message.reply_text(
                f"🎯Introduce una breve descripción del {context.user_data['expense_obj'].tipo}:"
            )
        return ConvState.ENTER_WHO

async def enter_who(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    
    # Actualizo el estado:
    context.user_data['states'].append(ConvState.ENTER_WHO)
    
    user = update.effective_user
    context.user_data['expense_obj'].descripcion = update.message.text
    
    logger.info(f"El usuario {user.id} añade la descripción al {context.user_data['expense_obj'].tipo}")
    
    if context.user_data['expense_obj'].tipo == 'gasto':
        markup = load_category_markup('quien')
        await update.message.reply_text(
                    f"🧾Al toque, ¿con quién ha sido el gasto:",
                    reply_markup=markup
                )
        return ConvState.CONFIRM
    else:
        context.user_data['expense_obj'].quien = 'Jesús'
        
        markup = yes_no_button()
        await update.message.reply_text(
                    f"📜Está todo correcto?\n{str(context.user_data['expense_obj'])}",
                    reply_markup=markup
                )
        return ConvState.SAVE

async def enter_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    # Actualizo el estado:
    context.user_data['states'].append(ConvState.CONFIRM)
    
    user = update.effective_user
    context.user_data['expense_obj'].quien = update.callback_query.data
    
    markup = yes_no_button()
    await update.callback_query.edit_message_text(
                    f"📜Está todo correcto?\n{str(context.user_data['expense_obj'])}",
                    reply_markup=markup
                )
    return ConvState.SAVE
    
async def enter_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    
    # Actualizo el estado:
    context.user_data['states'].append(ConvState.SAVE)
    
    user = update.effective_user
    ind_save = update.callback_query.data
    
    if ind_save == str(ConvState.YES):
        await update.callback_query.edit_message_text(
                    f"🧠Genial! Guardamos el registro\nPara añadir otro registro usa el comando /nuevo_gasto.",
                )
        save_expense(context.user_data['expense_obj'], DATA_FILE_PATH)
        
        return ConversationHandler.END
    
    else:
        await update.callback_query.edit_message_text(
                    f"⛔Ups de momento no se puede modificar nada, está en desarrollo :(\nPara añadir otro registro usa el comando /nuevo_gasto.",
                )
        return ConversationHandler.END
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Cancels and ends the conversation."""

    user = update.effective_user
    logging.info("User %s canceled the conversation.", user.first_name)

    await update.message.reply_text(
        f"👋 Hasta luego {user.first_name}!", 
    )
    context.user_data.clear() # Limpiamos los datos del usuario
    return ConversationHandler.END

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """La función va a llevar un control de los estados en los que se encuentra el bot y va a llevarte al paso anterior

    Args:
        update (Update): _description_
        context (ContextTypes.DEFAULT_TYPE): _description_

    Returns:
        int: _description_
    """
    
    # Recupero el estado actual y el estado previo, después borro el estado actual y me voy al estado previo:
    if context.user_data(['states']):
        actual_state = context.user_data(['states']).pop() # Antes del cancel
        previus_state = context.user_data(['states'])[-1]
    
    else:
        # No puedes hacer cancel si la conversación no ha empezado
        pass
    
    
    
    

enter_expense = ConversationHandler(
    entry_points=[
        CommandHandler("start", start),
        CommandHandler("nuevo_gasto", start)],
    states={
        ConvState.ENTER_EXPENSE: [
            CallbackQueryHandler(enter_import, pattern=f"^{str(ConvState.INCOME_ENTRY)}$|^{str(ConvState.SPENDING_ENTRY)}$"),
                                ],
        ConvState.SELECT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_category)],
        ConvState.ENTER_DESCRIPTION: [
            CallbackQueryHandler(enter_description, pattern="^"+"$|^".join([c for c in load_categories('gasto')])+"$"),
            CallbackQueryHandler(enter_description, pattern="^"+"$|^".join([c for c in load_categories('ingreso')])+"$"),
                            ],
        ConvState.ENTER_TRIP: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, enter_description_from_trip),
            CallbackQueryHandler(enter_description_from_trip, pattern=f"^{ConvState.YES}$|^{ConvState.NO}$")
                               ],
        ConvState.ENTER_WHO:[
            MessageHandler(filters.TEXT & ~filters.COMMAND, enter_who)
        ],
        ConvState.CONFIRM:[
            CallbackQueryHandler(enter_confirm, pattern="^"+"$|^".join([c for c in load_categories('quien')])+"$")
            
        ],
        ConvState.SAVE:[
            CallbackQueryHandler(enter_save, pattern=f"^{ConvState.YES}$|^{ConvState.NO}$")
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=False 
    
)
