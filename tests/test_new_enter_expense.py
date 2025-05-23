import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import src.handlers.conversations.new_enter_expense as psm
from src.handlers.conversations.new_enter_expense import ConvState
from telegram.ext import ConversationHandler
from src.models.expense import Expense

# Helper classes to simulate Update and Context
class DummyUser:
    def __init__(self, id, first_name):
        self.id = id
        self.first_name = first_name

class DummyUpdate:
    def __init__(self, user, message_text=None, callback_data=None):
        self.effective_user = user
        self.message = MagicMock()
        if message_text is not None:
            self.message.text = message_text
        self.callback_query = None
        self._callback_data = callback_data
        if callback_data is not None:
            self.callback_query = MagicMock()
            self.callback_query.data = callback_data

class DummyContext:
    def __init__(self):
        self.user_data = {}
        self.bot_data = {}

@pytest.mark.asyncio
async def test_yes_no_button_structure():
    markup = psm.yes_no_button()
    # Should be InlineKeyboardMarkup with two buttons in one row
    assert hasattr(markup, 'inline_keyboard')
    assert len(markup.inline_keyboard) == 1
    row = markup.inline_keyboard[0]
    assert len(row) == 2
    assert row[0].text == "✅ Sí"
    assert row[0].callback_data == str(ConvState.YES)
    assert row[1].text == "❌ No"
    assert row[1].callback_data == str(ConvState.NO)

@pytest.mark.asyncio
async def test_start_registered(monkeypatch):
    user = DummyUser(123, 'TestUser')
    update = DummyUpdate(user)
    context = DummyContext()
    # Patch check_user to return True
    monkeypatch.setattr(psm, 'check_user', lambda uid: True)
    # Patch state_manager methods
    update_send = AsyncMock()
    psm.state_manager.update_send_message = update_send
    push = MagicMock()
    psm.state_manager.push = push
    # Run start
    state = await psm.start(update, context)
    # Assert context.user_data has expense_obj
    assert 'expense_obj' in context.user_data
    assert isinstance(context.user_data['expense_obj'], Expense)
    # Assert update_send_message called
    update_send.assert_called_once()
    # Assert state_manager.push called
    push.assert_called_once()
    # Should return ENTER_EXPENSE
    assert state == ConvState.ENTER_EXPENSE

@pytest.mark.asyncio
async def test_start_unregistered(monkeypatch):
    user = DummyUser(456, 'Anon')
    update = DummyUpdate(user)
    context = DummyContext()
    # Patch check_user to return False
    monkeypatch.setattr(psm, 'check_user', lambda uid: False)
    # Patch update_send_message
    update_send = AsyncMock()
    psm.state_manager.update_send_message = update_send
    # Run start
    state = await psm.start(update, context)
    # Assert update_send_message called with registration prompt
    update_send.assert_called_once()
    # Should end conversation
    assert state == ConversationHandler.END

@pytest.mark.asyncio
async def test_enter_save_yes(monkeypatch):
    user = DummyUser(789, 'Saver')
    # Simulate get_input_data returns YES
    monkeypatch.setattr(psm.state_manager, 'get_input_data', lambda upd, ctx: str(ConvState.YES))
    # Patch update_send_message
    update_send = AsyncMock()
    psm.state_manager.update_send_message = update_send
    # Patch save_expense and clear_manager
    saved = MagicMock()
    monkeypatch.setattr(psm, 'save_expense', saved)
    cleared = MagicMock()
    monkeypatch.setattr(psm.state_manager, 'clear_manager', cleared)
    context = DummyContext()
    # Ensure expense_obj present
    context.user_data['expense_obj'] = Expense(user.id)
    update = DummyUpdate(user, callback_data=str(ConvState.YES))
    # Call enter_save
    state = await psm.enter_save(update, context)
    # Assert save_expense called
    saved.assert_called_once_with(context.user_data['expense_obj'], psm.DATA_FILE_PATH)
    # Assert clear_manager called
    cleared.assert_called_once()
    assert state == ConversationHandler.END

@pytest.mark.asyncio
async def test_enter_save_no(monkeypatch):
    user = DummyUser(321, 'NoSaver')
    # Simulate get_input_data returns NO
    monkeypatch.setattr(psm.state_manager, 'get_input_data', lambda upd, ctx: str(ConvState.NO))
    update_send = AsyncMock()
    psm.state_manager.update_send_message = update_send
    saved = MagicMock()
    monkeypatch.setattr(psm, 'save_expense', saved)
    cleared = MagicMock()
    monkeypatch.setattr(psm.state_manager, 'clear_manager', cleared)
    context = DummyContext()
    context.user_data['expense_obj'] = Expense(user.id)
    update = DummyUpdate(user, callback_data=str(ConvState.NO))
    state = await psm.enter_save(update, context)
    # save_expense should not be called
    saved.assert_not_called()
    cleared.assert_called_once()
    assert state == ConversationHandler.END
