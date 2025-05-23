import pytest
from unittest.mock import AsyncMock, MagicMock


import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.models.state_manager import StateManager


@pytest.fixture
def mock_update_message():
    update = MagicMock()
    update.message = MagicMock()
    update.callback_query = None
    update.message.text = "test"
    return update


@pytest.fixture
def mock_update_callback():
    update = MagicMock()
    update.callback_query = MagicMock()
    update.callback_query.data = "callback_data"
    update.message = None
    return update


@pytest.fixture
def mock_context():
    context = MagicMock()
    context.user_data = {}
    return context


def test_extract_input_data_message(mock_update_message):
    sm = StateManager()
    assert sm._extract_input_data(mock_update_message) == "test"


def test_extract_input_data_callback(mock_update_callback):
    sm = StateManager()
    assert sm._extract_input_data(mock_update_callback) == "callback_data"


def test_get_input_data_back_command(mock_update_message, mock_context):
    sm = StateManager()
    sm.BACK_COMMAND = "test"
    mock_context.user_data[sm.LAST_INPUT_KEY] = "last_input"
    assert sm.get_input_data(mock_update_message, mock_context) == "last_input"


def test_push_and_pop(mock_update_message, mock_context):
    sm = StateManager()
    mock_context.user_data['some_key'] = 'value'

    def handler():
        return "handled"

    sm.push(mock_update_message, mock_context, 1, handler)
    state, hnd, data = sm.pop(mock_context)
    assert state == 1
    assert hnd == handler
    assert data == "test"
    assert mock_context.user_data['some_key'] == 'value'


@pytest.mark.asyncio
async def test_back_with_no_history(mock_update_message, mock_context):
    sm = StateManager()
    mock_context.user_data = {}  # no history
    response = await sm.back(mock_update_message, mock_context)
    assert response == -1  # ConversationHandler.END


@pytest.mark.asyncio
async def test_update_send_message_callback():
    sm = StateManager()
    update = MagicMock()
    context = MagicMock()
    cb = AsyncMock()
    cb.edit_message_text = AsyncMock()
    cb.answer = AsyncMock()
    update.callback_query = cb
    update.message = None
    await sm.update_send_message(update, context, "Hola")
    cb.answer.assert_awaited()
    cb.edit_message_text.assert_awaited_with("Hola", reply_markup=None)


@pytest.mark.asyncio
async def test_update_send_message_text():
    sm = StateManager()
    update = MagicMock()
    context = MagicMock()
    msg = AsyncMock()
    msg.reply_text = AsyncMock()
    update.message = msg
    update.callback_query = None
    await sm.update_send_message(update, context, "Hola")
    msg.reply_text.assert_awaited_with("Hola", reply_markup=None)
