import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch

from telegram.ext import ConversationHandler
from telegram import User, Message

import src.handlers.conversations as conv_module  # ajusta el path si lo necesitas
from src.handlers.conversations import (
    nuevo_usuario_entry,
    enter_pwd,
    cancel,
    ConvState,
)

@pytest.fixture
def fake_update():
    """Crea un objeto `update` con mocks de usuario y mensaje."""
    user = User(id=123, first_name="Test", is_bot=False, username="testuser")
    message = AsyncMock(spec=Message)
    message.text = "dummy"
    # reply_text debe ser async
    message.reply_text = AsyncMock()
    update = Mock()
    update.effective_user = user
    update.message = message
    return update

@pytest.fixture
def fake_context():
    """Crea un contexto vacío con user_data dict."""
    ctx = Mock()
    ctx.user_data = {}
    return ctx

@pytest.mark.asyncio
@patch("src.handlers.conversations.check_user", return_value=True)
async def test_nuevo_usuario_entry_user_exists(mock_check, fake_update, fake_context):
    # Cuando el usuario ya existe, debe terminar la conversación y enviar aviso
    result = await nuevo_usuario_entry(fake_update, fake_context)

    fake_update.message.reply_text.assert_awaited_once_with(
        "⚠️ Uy, ya estabas registrado. Usa /start para continuar."
    )
    assert result == ConversationHandler.END

@pytest.mark.asyncio
@patch("src.handlers.conversations.check_user", return_value=False)
async def test_nuevo_usuario_entry_new_user(mock_check, fake_update, fake_context):
    # Cuando no existe, pide la contraseña y devuelve el estado NEW_USER_PWD
    result = await nuevo_usuario_entry(fake_update, fake_context)

    fake_update.message.reply_text.assert_awaited_once_with(
        "👮‍♀️ Por favor introduce la contraseña \n\n"
        "Utiliza /cancel para finalizar.",
    )
    assert result == ConvState.NEW_USER_PWD

@pytest.mark.asyncio
@patch("src.handlers.conversations.add_user", return_value=True)
async def test_enter_pwd_success(mock_add, fake_update, fake_context):
    # Simula usuario que introduce la contraseña correcta
    fake_update.message.text = "correct_pwd"
    result = await enter_pwd(fake_update, fake_context)

    mock_add.assert_called_once_with(123, "correct_pwd")
    fake_update.message.reply_text.assert_awaited_once_with(
        f"✅ Bienveni@ Test! Usa el comando /start para empezar :)"
    )
    assert result == ConversationHandler.END

@pytest.mark.asyncio
@patch("src.handlers.conversations.add_user", return_value=False)
async def test_enter_pwd_failure(mock_add, fake_update, fake_context):
    # Simula usuario que introduce contraseña incorrecta
    fake_update.message.text = "wrong_pwd"
    result = await enter_pwd(fake_update, fake_context)

    mock_add.assert_called_once_with(123, "wrong_pwd")
    fake_update.message.reply_text.assert_awaited_once_with(
        "🙅 Ups! La contraseña no es correcta. Intentalo de nuevo"
    )
    assert result == ConvState.NEW_USER_PWD

@pytest.mark.asyncio
async def test_cancel_clears_data_and_ends(fake_update, fake_context):
    # Pon algo en user_data para verificar que se limpia
    fake_context.user_data["foo"] = "bar"
    result = await cancel(fake_update, fake_context)

    fake_update.message.reply_text.assert_awaited_once_with(
        "👋 Hasta luego %s!", fake_update.effective_user.first_name
    )
    assert fake_context.user_data == {}
    assert result == ConversationHandler.END
