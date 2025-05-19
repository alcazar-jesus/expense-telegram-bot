

from telegram.ext import ApplicationBuilder

# importas comandos
from handlers.commands.start import start_handler

# importas conversaciones
from handlers.conversations.new_user import conv_nuevo_usuario_handler


def register_all_handlers(application):
    # Comandos simples
    application.add_handler(start_handler)


    # Flujos de conversación
    application.add_handler(conv_nuevo_usuario_handler)