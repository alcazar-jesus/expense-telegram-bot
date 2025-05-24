import logging
import random
#from datetime import datetime
from enum import IntEnum, auto

from src.settings import DATA_FILE_PATH
from src.utils.category_utils import load_categories, load_category_markup, chunk_list
from src.utils.user_utils import check_user 
from src.utils.csv_utils import get_last_trip, save_expense
from src.models.expense import Expense
from src.models.state_manager import StateManager

from src.utils.constantes import *
from src.utils.helper_functions import validate_date

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
    MODIFY_DATE = auto()
    MODIFY_TYPE = auto()
    MODIFY_EXPENSE = auto()
    MODIFY_CATEGORY = auto()
    MODIFY_DESCR = auto()
    MODIFY_WHO = auto()
    MODIFY_TRIP = auto()
    MODIFY_ANN = auto()
    NESTED_STOP = auto()
    SAVE_MODIFY = auto()

LABELS_ConvState = {
    ConvState.INCOME_ENTRY: 'ingreso',
    ConvState.SPENDING_ENTRY: 'gasto',
}

MODIFICATIONS = {
    ConvState.MODIFY_DATE :"Fecha",
    ConvState.MODIFY_TYPE :"Tipo",
    ConvState.MODIFY_EXPENSE :"Importe",
    ConvState.MODIFY_CATEGORY :"Concepto",
    ConvState.MODIFY_DESCR :"Descripción",
    ConvState.MODIFY_WHO :"Quien",
    ConvState.MODIFY_TRIP :"Viaje",
    ConvState.MODIFY_ANN :"Anualizable"
    }


state_manager = StateManager()

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
    
        await state_manager.update_send_message(update=update, context=context,
            text=f'👋 Hola {user.first_name}! Te voy a gestionar los gastos, ¿Qué quieres añadir?', reply_markup=reply_markup
        )
        
        state_manager.push(update, context, ConvState.START, start)
        
        return ConvState.ENTER_EXPENSE
    
    else:
        await state_manager.update_send_message(update=update, context=context,
            text=f"❌ Hola {user.first_name}! Parece que no estás entre los usuarios registrados. Por favor usa /nuevo_usuario para darte de alta :)"
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
    
    input_data = state_manager.get_input_data(update, context)
    print(input_data)
    expense_type = LABELS_ConvState[int(input_data)]
    context.user_data["expense_obj"].tipo = expense_type # He cambiado ConvState.SPENDING_ENTRY por su valor correspondiente

    
    user = update.effective_user
    
    logger.info(f"El usuario {user.id} quiere añadir un {expense_type}")

    # No cambia ya que si venimos de hacer back en el estado categoria también viene de un CallbackQuery
    if expense_type == LABELS_ConvState[int(ConvState.SPENDING_ENTRY)]:
        await state_manager.update_send_message(update=update, context=context,
                                                text=f"{random.choice(EMOJIS_GASTOS)} {random.choice(CUNADO_CHISTES_GASTOS)}\n\n{random.choice(FRASES_PEDIR_GASTO)}",
            )
        # await update.callback_query.answer()
        # await update.callback_query.edit_message_text(
        #     f"{random.choice(EMOJIS_GASTOS)} {random.choice(CUNADO_CHISTES_GASTOS)}\n\n{random.choice(FRASES_PEDIR_GASTO)}",
        #     )
        
    elif expense_type == LABELS_ConvState[int(ConvState.INCOME_ENTRY)]:
        await state_manager.update_send_message(update=update, context=context,
                                                text=f"{random.choice(EMOJIS_INGRESOS)} {random.choice(CUNADO_CHISTES_INGRESO)}\n\n{random.choice(FRASES_PEDIR_INGRESO)}",
            ) 
        # await update.callback_query.answer()
        # await update.callback_query.edit_message_text(
        #     f"{random.choice(EMOJIS_INGRESOS)} {random.choice(CUNADO_CHISTES_INGRESO)}\n\n{random.choice(FRASES_PEDIR_INGRESO)}",
        #     )    
        
    state_manager.push(update, context, ConvState.ENTER_EXPENSE, enter_import)    
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
    
    
    input_data = state_manager.get_input_data(update, context)
    print(input_data)
    importe = update.message.text
    
    user = update.effective_user
    try:
        context.user_data['expense_obj'].importe = importe
    except Exception as e:
        logger.error(f"El usuario {user.id} añade un {context.user_data['expense_obj'].tipo} incorrecto: {importe}. Error: {e}")
        
        await state_manager.update_send_message(update=update, context=context,
            text=f"Vaya, el importe de {importe} es incorrecto, asegurate de que no es negativo o que es un valor numérico!"
        )
        state_manager.push(update, context, ConvState.SELECT_TYPE, select_category)  
        return ConvState.SELECT_TYPE
    
    
    user = update.effective_user
    
    logger.info(f"El usuario {user.id} quiere añadir un {context.user_data['expense_obj'].tipo}: {importe}")
    
    
    # Función para generar el KeyboardMarkup
    markup = load_category_markup(context.user_data['expense_obj'].tipo)

    await state_manager.update_send_message(update=update, context=context,
            text=f"👀 Tomo nota! ¿Cuál es el concepto del {context.user_data['expense_obj'].tipo}?",
            reply_markup=markup
        )
    state_manager.push(update, context, ConvState.SELECT_TYPE, select_category)  
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
    

    
    cat = state_manager.get_input_data(update, context)

    user = update.effective_user
    
    context.user_data['expense_obj'].categoria = cat
    
    logger.info(f"El usuario {user.id} añade el gasto a la categoría {context.user_data['expense_obj'].categoria}")
    # Si la categoría es "Viajes" entonces se preguntará por el nombre/identificador del viaje, 
    # si no se pasará a preguntar por la descripción directamente
    if cat != 'Viajes':
        # Si es distinto de "Viajes", pedimos que nos diga la descripción y pasamos de estado
        
        await state_manager.update_send_message(update, context,
                f"🎯Introduce una breve descripción del {context.user_data['expense_obj'].tipo}:"
            )
        state_manager.push(update, context, ConvState.ENTER_DESCRIPTION, enter_description)  
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
            
            await state_manager.update_send_message(update, context,
                text=f"🛫Ole ole viajecito!! El viaje es {last_trip}?",
                reply_markup=markup
            )
            state_manager.push(update, context, ConvState.ENTER_DESCRIPTION, enter_description)
            return ConvState.ENTER_TRIP
            
        else:
            await state_manager.update_send_message(update, context,
                f"🛫Ole ole viajecito!! Introduce el viaje",
            )
            state_manager.push(update, context, ConvState.ENTER_DESCRIPTION, enter_description)
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
    
    if update.callback_query:
        # Viene del markup
        trip = state_manager.get_input_data(update, context)
        
        if trip == str(ConvState.YES):
            # En el paso anterior hemos guardado el viaje por lo que no hay que hacer nada (preguntar por la descripción)
            await state_manager.update_send_message(update, context,
                f"🎯Introduce una breve descripción del {context.user_data['expense_obj'].tipo}:"
            )
            state_manager.push(update, context, ConvState.ENTER_TRIP, enter_description_from_trip)
            return ConvState.ENTER_WHO
        else:
            # Preguntamos por el viaje:
            context.user_data['expense_obj'].viaje = None
            
            await state_manager.update_send_message(update, context,
                    f"🛫Vale, pues introduce el viaje:",
                )
            state_manager.push(update, context, ConvState.ENTER_TRIP, enter_description_from_trip)
            return ConvState.ENTER_TRIP
    else:
        # Viene de escribir el viaje
        context.user_data['expense_obj'].viaje = state_manager.get_input_data(update, context)
        
        await state_manager.update_send_message(update, context,
                f"🎯Introduce una breve descripción del {context.user_data['expense_obj'].tipo}:"
            )
        state_manager.push(update, context, ConvState.ENTER_TRIP, enter_description_from_trip)
        return ConvState.ENTER_WHO

async def enter_who(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    
    
    user = update.effective_user
    context.user_data['expense_obj'].descripcion = state_manager.get_input_data(update, context)
    
    logger.info(f"El usuario {user.id} añade la descripción al {context.user_data['expense_obj'].tipo}")
    
    if context.user_data['expense_obj'].tipo == 'gasto':
        markup = load_category_markup('quien')
        await state_manager.update_send_message(update, context, 
                    f"🧾Al toque, ¿con quién ha sido el gasto:",
                    markup
                )
        state_manager.push(update, context, ConvState.ENTER_WHO, enter_who)
        return ConvState.CONFIRM
    else:
        context.user_data['expense_obj'].quien = 'Jesús'
        
        markup = yes_no_button()
        await state_manager.update_send_message(update=update, context=context,
                    text=f"📜Está todo correcto?\n{str(context.user_data['expense_obj'])}",
                    reply_markup=markup
                )
        state_manager.push(update, context, ConvState.ENTER_WHO, enter_who)
        return ConvState.SAVE

async def enter_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    
    user = update.effective_user
    context.user_data['expense_obj'].quien = state_manager.get_input_data(update, context)
    
    markup = yes_no_button()
    
    await state_manager.update_send_message(update, context,
                    text=f"📜Está todo correcto?\n{str(context.user_data['expense_obj'])}",
                    reply_markup=markup
                )
    state_manager.push(update, context, ConvState.SAVE, enter_confirm)
    return ConvState.SAVE
    
async def enter_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    
    user = update.effective_user
    ind_save = state_manager.get_input_data(update, context)
    
    if ind_save == str(ConvState.YES):
        await state_manager.update_send_message(update, context,
                    f"🧠Genial! Guardamos el registro\nPara añadir otro registro usa el comando /nuevo_gasto.",
                )
        save_expense(context.user_data['expense_obj'], DATA_FILE_PATH)
        state_manager.clear_manager(context)
        return ConversationHandler.END
    
    else:
        
        
        buttons = [
        InlineKeyboardButton(cat, callback_data=f"{str(k)}")
        for k,cat in MODIFICATIONS.items()
        ]
        
        markup = InlineKeyboardMarkup(chunk_list(buttons, 2))
        await state_manager.update_send_message(update, context,
                    text=f"🥸¿Qué quieres modificar?",
                    reply_markup=markup
                )
        state_manager.push(update, context, ConvState.SAVE, enter_save)
        return ConvState.MODIFY

async def enter_modify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    ind_modify = state_manager.get_input_data(update, context)
    
    if ind_modify == str(ConvState.MODIFY_DATE):
        await state_manager.update_send_message(
            update, context,
            text=f"📆 Introduce la nueva fecha en formato DD/MM/YYYY o DD/MM/YY"
            )
        state_manager.push(update, context, ConvState.MODIFY, enter_modify)
        return ConvState.MODIFY_DATE
    elif ind_modify == str(ConvState.MODIFY_EXPENSE):
        await modify_expense(update, context)
    elif ind_modify == str(ConvState.MODIFY_TYPE):
        await modify_type(update, context)
    elif ind_modify == str(ConvState.MODIFY_CATEGORY):
        await modify_category(update, context)
    elif ind_modify == str(ConvState.MODIFY_DESCR):
        await modify_description(update, context)
    elif ind_modify == str(ConvState.MODIFY_WHO):
        await modify_who(update, context)
    elif ind_modify == str(ConvState.MODIFY_TRIP):
        await modify_trip(update, context)
    elif ind_modify == str(ConvState.MODIFY_ANN):
        await modify_annualizable(update, context)
    
    # await state_manager.update_send_message(update, context,
    #                 text=f"Ups de momento esta parte está en desarrollo. Modificar: {ind_modify}",
    #             )
    # state_manager.clear_manager(context)
    # return ConversationHandler.END

async def modify_again(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    buttons = [
        InlineKeyboardButton(cat, callback_data=f"{str(k)}")
        for k,cat in MODIFICATIONS.items()
    ]
        
    markup = InlineKeyboardMarkup(chunk_list(buttons, 2))
    await state_manager.update_send_message(update, context,
                    text=f"🥸¿Qué quieres modificar?",
                    reply_markup=markup
        )
    state_manager.push(update, context, ConvState.SAVE_MODIFY, modify_again)
    return ConvState.MODIFY


async def modify_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    str_modify = state_manager.get_input_data(update, context)
    
    if validate_date(str_modify):
        
        context.user_data['expense_obj'].fecha = str_modify

        markup = yes_no_button()
        state_manager.update_send_message(
            update, context,
            text=f"¿Quieres modificar algo más",
            reply_markup=markup)
        return ConvState.SAVE_MODIFY
    else:
        state_manager.update_send_message(
            update, context,
            text=f"📆 Introduce la nueva fecha en formato DD/MM/YYYY o DD/MM/YY")
        return ConvState.MODIFY_DATE
    
    
    

async def modify_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pass

async def modify_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pass

async def modify_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pass

async def modify_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pass

async def modify_trip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pass

async def modify_who(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pass

async def modify_annualizable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pass    
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Cancels and ends the conversation."""

    user = update.effective_user
    logging.info("User %s canceled the conversation.", user.first_name)

    await state_manager.update_send_message(update, context,
        f"👋 Hasta luego {user.first_name}!", 
    )
    context.user_data.clear() # Limpiamos los datos del usuario
    state_manager.clear_manager(context)
    return ConversationHandler.END
    

conv_modify = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(enter_modify, pattern="^"+"$|^".join([str(c) for c in MODIFICATIONS.keys()])+"$")
    ],
    states={
        ConvState.MODIFY: [CallbackQueryHandler(enter_modify, pattern="^"+"$|^".join([str(c) for c in MODIFICATIONS.keys()])+"$")],
        ConvState.MODIFY_DATE:[MessageHandler(filters.TEXT & ~filters.COMMAND, modify_date)],
        
        
        
        
        
        ConvState.SAVE_MODIFY:[
            CallbackQueryHandler(modify_again, pattern=f"^{ConvState.YES}$"),
            CallbackQueryHandler(modify_again, pattern=f"^{ConvState.NO}$")]
        
    },
    map_to_parent={
            # Return to top level menu
            ConversationHandler.END: ConvState.CONFIRM,
            # End conversation altogether
            ConvState.NESTED_STOP: ConversationHandler.END,
        },
)


conv_new_enter_expense = ConversationHandler(
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
        ],
        ConvState.MODIFY: [conv_modify]
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        CommandHandler("back", state_manager.back)],
    per_message=False 
    
)


