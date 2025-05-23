import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / 'src'))

import handlers.conversations.new_enter_expense as psm
from handlers.conversations.new_enter_expense import ConvState
from telegram.ext import ConversationHandler
from models.expense import Expense

# Tests for router and bot main
import pytest
from unittest.mock import MagicMock, patch
import handlers.router as router
import bot as bot

class DummyHandler:
    pass

class DummyApplication:
    def __init__(self):
        self.handlers = []
    def add_handler(self, handler):
        self.handlers.append(handler)


def test_register_all_handlers():
    app = DummyApplication()
    # Import the actual handlers from router
    expected_handlers = [router.enter_expense, router.conv_nuevo_usuario_handler]
    router.register_all_handlers(app)
    assert app.handlers == expected_handlers


def test_main_invokes_builder_and_run(monkeypatch):
    # Create dummy application
    dummy_app = DummyApplication()
    # Stub ApplicationBuilder
    class DummyBuilder:
        def __init__(self):
            self._token = None
        def token(self, token):
            self._token = token
            return self
        def build(self):
            return dummy_app
    monkeypatch.setattr(bot, 'ApplicationBuilder', DummyBuilder)
    # Stub register_all_handlers to record call
    called = {}
    def fake_register(app):
        called['app'] = app
    monkeypatch.setattr(router, 'register_all_handlers', fake_register)
    # Stub run_polling
    dummy_app.run_polling = MagicMock()
    # Stub TOKEN
    monkeypatch.setattr(bot, 'TOKEN', 'fake-token')
    # Run main
    bot.main()
    # Ensure register_all_handlers received dummy_app
    assert called.get('app') is dummy_app
    # Ensure run_polling was called with drop_pending_updates=True
    dummy_app.run_polling.assert_called_once_with(drop_pending_updates=True)
