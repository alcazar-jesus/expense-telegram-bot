

from telegram.ext import ApplicationBuilder

# importas comandos
# from handlers.commands.start import start_handler

# importas conversaciones
from handlers.conversations.new_user import conv_nuevo_usuario_handler
# from handlers.conversations.enter_expense import enter_expense
from handlers.conversations.new_enter_expense import conv_new_enter_expense
from handlers.error_handler import error_handler
from telegram.ext import CommandHandler

def register_all_handlers(application):
    # Comandos simples
    # application.add_handler(start_handler)


    # Flujos de conversación
    application.add_handler(conv_new_enter_expense)
    application.add_handler(conv_nuevo_usuario_handler)
    

    # ...and the error handler
    application.add_error_handler(error_handler)