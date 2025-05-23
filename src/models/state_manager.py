from copy import deepcopy
from telegram import Update, CallbackQuery, Message
from telegram.ext import ContextTypes, ConversationHandler

class StateManager:
    """
    Administrador de estados y snapshot de datos en python-telegram-bot v20+.
    Maneja push/pop de estados, snapshots de user_data, y responde correctamente a Message o CallbackQuery.
    También almacena datos de entrada originales (callback_query.data o message.text) para facilitar reentrada.


    Returns:
        _type_: _description_
    """
    HISTORY_KEY = "_state_history"
    LAST_INPUT_KEY = "_last_input_data"
    LAST_INPUT_UPDATE = "_last_input_update"
    BACK_COMMAND = ""
    FIRST_BACK = True
    
    def __init__(self):
        pass

    def _extract_input_data(self, update: Update) -> str | None:
        """
        Extrae input data del update (callback_query o message).
        
        En un futuro se podría implementar para más
        """
        if update.callback_query:
            return update.callback_query.data
        elif update.message:
            return update.message.text
        return None

    def get_input_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
        """
        Obtiene el input_data relevante para el handler: ya sea callback.data, message.text o reentry.
        La función getattr() se usa para obtener el valor de un atributo de un objeto, utilizando
        el nombre del atributo como una cadena de texto
        """
        if getattr(update.message, "text", None) == self.BACK_COMMAND:
            return context.user_data.get(self.LAST_INPUT_KEY)
        return (
            # getattr(update, "reentry_data", None)
            getattr(update.callback_query, "data", None)
            or getattr(update.message, "text", None)
        )
    
    def _extract_input_update(self, update: Update) -> str | None:
        """
        Extrae input data del update (callback_query o message).
        
        En un futuro se podría implementar para más
        """
        if update.callback_query:
            return update.callback_query
        elif update.message:
            return update.message
        return None
    
    def get_input_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
        
        if getattr(update.message, "text", None) == self.BACK_COMMAND:
            return context.user_data.get(self.LAST_INPUT_UPDATE)
        return update
        
    def push(self, update: Update, context: ContextTypes.DEFAULT_TYPE, state: int, handler_func):
        """
        Guarda en la pila el conjunto (state, handler_func, snapshot de user_data, input_data).
        Debe llamarse justo antes de cambiar de estado, tras leer input y guardar datos.
        """
        input_data = self._extract_input_data(update)
        input_update = self._extract_input_update(update)
        snapshot = {k: deepcopy(v) for k, v in context.user_data.items() if k != self.HISTORY_KEY} # Hace un snapshot de context.user_data para recuperarlos
        history = context.user_data.setdefault(self.HISTORY_KEY, [])
        history.append((state, handler_func, snapshot, input_data, input_update)) # En "_state_history" guarda el estado junto con el snapshot y otras cosas

    def pop(self, context: ContextTypes.DEFAULT_TYPE):
        """
        Extrae el último estado, handler, snapshot e input_data; restaura user_data.
        Devuelve (state, handler, input_data), o (None, None, None) si no hay historial.
        """
        history = context.user_data.get(self.HISTORY_KEY, [])
        if not history:
            return None, None, None

        _ = history.pop()
        if not history:
            return None, None, None
        state, handler, snapshot, input_data, input_update = history.pop() # Vuelvo dos estados para atrás
        context.user_data.clear()
        context.user_data.update(snapshot)
        context.user_data[self.LAST_INPUT_KEY] = input_data  # útil para handlers que dependen del input
        
        context.user_data[self.LAST_INPUT_UPDATE] = input_update  # útil para handlers que dependen del input
        return state, handler, input_data

    async def back(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Manejador para /back: recupera el estado anterior, notifica al usuario y llama al handler.
        Además, inyecta el input_data restaurado en el objeto update como reentry_data.
        """
        if self.FIRST_BACK:
            self.BACK_COMMAND = self._extract_input_data(update)
            self.FIRST_BACK = False
        
        state, handler, input_data = self.pop(context)
        if not handler:
            await self._send(update, "No hay estado anterior.\n👋Hasta luego.\n\nPara empezar la conversación usa /start o /nuevo_gasto")
            return ConversationHandler.END

        await self._send(update, "Volviendo al estado anterior...")

        # Inyectar input_data como atributo temporal al update
        # setattr(update, "reentry_data", input_data)

        return await handler(update, context)

    async def update_send_message(self, update, context, text, reply_markup = None):
        """
        Función para mandar el mensaje desde el state manager, en función del update que sea
        """
        
        if update.callback_query:
            await update.callback_query.answer()
            return await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
        elif update.message:
            return await update.message.reply_text(text, reply_markup=reply_markup)
        else:
            print('nada')
    
    async def _send(self, update: Update, text: str):
        """
        Envía o edita mensaje según el tipo de update.
        """
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(text)
        elif update.message:
            await update.message.reply_text(text)
        else:
            pass
    
    def clear_manager(context, self):
        context.user_data.clear()
        self.BACK_COMMAND = ""
        self.FIRST_BACK = True