import pytest
import asyncio
import sys

from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import src.handlers.conversations.enter_expense as ee
from src.handlers.conversations.enter_expense import (
    start,
    enter_import,
    select_category,
    enter_description,
    enter_description_from_trip,
    enter_who,
    enter_confirm,
    enter_save,
    cancel,
    ConvState,
)

class FakeUser:
    def __init__(self, id, first_name="TestUser"):
        self.id = id
        self.first_name = first_name

class FakeMessage:
    def __init__(self, text=None):
        self.text = text
        self.replies = []
    async def reply_text(self, text, reply_markup=None):
        self.replies.append((text, reply_markup))
        return

class FakeCallbackQuery:
    def __init__(self, data, message=None):
        self.data = data
        self.message = message or FakeMessage()
        self.edits = []
        self.from_user = None
    async def edit_message_text(self, text, reply_markup=None):
        self.edits.append((text, reply_markup))
        return

class FakeUpdate:
    def __init__(self, user, message=None, callback_query=None):
        self.effective_user = user
        self.message = message
        self.callback_query = callback_query

class FakeContext:
    def __init__(self):
        self.user_data = {}

@pytest.fixture(autouse=True)
def patch_utils(monkeypatch):
    # Patch external dependencies
    monkeypatch.setattr(ee, 'check_user', lambda user_id: user_id == 1)
    monkeypatch.setattr(ee, 'load_categories', lambda tipo: ['CatA', 'Viajes'] if tipo == 'gasto' else [])
    monkeypatch.setattr(ee, 'load_category_markup', lambda tipo: f"Markup({tipo})")
    monkeypatch.setattr(ee, 'get_last_trip', lambda path: None)
    monkeypatch.setattr(ee, 'save_expense', lambda obj, path: setattr(obj, 'saved', True))
    # Patch random choices to fixed
    monkeypatch.setattr(ee.random, 'choice', lambda x: x[0])
    # Patch constants
    monkeypatch.setattr(ee, 'EMOJIS_GASTOS', ['G'] )
    monkeypatch.setattr(ee, 'CUNADO_CHISTES_GASTOS', ['CJ_G'])
    monkeypatch.setattr(ee, 'FRASES_PEDIR_GASTO', ['PG'])
    monkeypatch.setattr(ee, 'EMOJIS_INGRESOS', ['I'])
    monkeypatch.setattr(ee, 'CUNADO_CHISTES_INGRESO', ['CJ_I'])
    monkeypatch.setattr(ee, 'FRASES_PEDIR_INGRESO', ['PI'])
    yield

@pytest.mark.asyncio
async def test_unauthorized_start():
    user = FakeUser(id=2)
    message = FakeMessage()
    update = FakeUpdate(user=user, message=message)
    context = FakeContext()
    state = await start(update, context)
    assert state == ee.ConversationHandler.END
    assert "no estás entre los usuarios registrados" in message.replies[0][0]

@pytest.mark.asyncio
async def test_authorized_start():
    user = FakeUser(id=1, first_name="Alice")
    message = FakeMessage()
    update = FakeUpdate(user=user, message=message)
    context = FakeContext()
    state = await start(update, context)
    assert state == ConvState.ENTER_EXPENSE
    assert isinstance(context.user_data.get('expense_obj'), ee.Expense)
    assert "Hola Alice" in message.replies[0][0]

@pytest.mark.asyncio
async def test_enter_import_and_select_type():
    user = FakeUser(id=1)
    # simulate pressing gasto button
    cq = FakeCallbackQuery(data=str(ConvState.SPENDING_ENTRY))
    cq.from_user = user
    update = FakeUpdate(user=user, callback_query=cq)
    context = FakeContext()
    context.user_data['expense_obj'] = ee.Expense(user.id)
    state = await enter_import(update, context)
    assert state == ConvState.SELECT_TYPE
    assert context.user_data['expense_obj'].tipo == 'gasto'

@pytest.mark.asyncio
async def test_select_category_invalid_and_valid():
    user = FakeUser(id=1)
    # invalid amount
    message = FakeMessage(text="abc")
    update = FakeUpdate(user=user, message=message)
    context = FakeContext()
    context.user_data['expense_obj'] = ee.Expense(user.id)
    state = await select_category(update, context)
    assert state == ConvState.SELECT_TYPE
    assert "importe de abc es incorrecto" in message.replies[0][0]
    # valid amount
    message = FakeMessage(text="123")
    update = FakeUpdate(user=user, message=message)
    context = FakeContext()
    context.user_data['expense_obj'] = ee.Expense(user.id)
    state = await select_category(update, context)
    assert state == ConvState.ENTER_DESCRIPTION
    assert "concepto" in message.replies[0][0]
    assert context.user_data['expense_obj'].importe == 123

@pytest.mark.asyncio
async def test_enter_description_non_trip():
    user = FakeUser(id=1)
    cq = FakeCallbackQuery(data='CatA')
    cq.from_user = user
    update = FakeUpdate(user=user, callback_query=cq)
    context = FakeContext()
    context.user_data['expense_obj'] = ee.Expense(user.id)
    state = await enter_description(update, context)
    assert state == ConvState.ENTER_WHO
    assert context.user_data['expense_obj'].categoria == 'CatA'

@pytest.mark.asyncio
async def test_enter_description_trip_no_last():
    # monkeypatch get_last_trip to return None already
    user = FakeUser(id=1)
    cq = FakeCallbackQuery(data='Viajes')
    cq.from_user = user
    update = FakeUpdate(user=user, callback_query=cq)
    context = FakeContext()
    context.user_data['expense_obj'] = ee.Expense(user.id)
    state = await enter_description(update, context)
    assert state == ConvState.ENTER_TRIP
    assert "Introduce el viaje" in cq.edits[0][0]

@pytest.mark.asyncio
async def test_enter_description_from_trip_message():
    user = FakeUser(id=1)
    message = FakeMessage(text="Trip1")
    update = FakeUpdate(user=user, message=message)
    context = FakeContext()
    context.user_data['expense_obj'] = ee.Expense(user.id)
    state = await enter_description_from_trip(update, context)
    assert state == ConvState.ENTER_WHO
    assert context.user_data['expense_obj'].viaje == "Trip1"

@pytest.mark.asyncio
async def test_enter_who_and_confirm_flow_expense():
    user = FakeUser(id=1)
    message = FakeMessage(text="Lunch")
    update = FakeUpdate(user=user, message=message)
    context = FakeContext()
    eo = ee.Expense(user.id)
    eo.tipo = 'gasto'
    context.user_data['expense_obj'] = eo
    state = await enter_who(update, context)
    assert state == ConvState.CONFIRM
    assert context.user_data['expense_obj'].descripcion == "Lunch"

@pytest.mark.asyncio
async def test_enter_who_flow_income():
    user = FakeUser(id=1)
    message = FakeMessage(text="Salary")
    update = FakeUpdate(user=user, message=message)
    context = FakeContext()
    eo = ee.Expense(user.id)
    eo.tipo = 'ingreso'
    context.user_data['expense_obj'] = eo
    state = await enter_who(update, context)
    assert state == ConvState.SAVE
    assert context.user_data['expense_obj'].quien == "Jesús"

@pytest.mark.asyncio
async def test_enter_confirm_and_save_yes():
    user = FakeUser(id=1)
    # confirm
    cq = FakeCallbackQuery(data='Who1')
    cq.from_user = user
    update = FakeUpdate(user=user, callback_query=cq)
    context = FakeContext()
    eo = ee.Expense(user.id)
    context.user_data['expense_obj'] = eo
    state = await enter_confirm(update, context)
    assert state == ConvState.SAVE
    assert context.user_data['expense_obj'].quien == 'Who1'
    # save with yes
    cq2 = FakeCallbackQuery(data=str(ConvState.YES))
    cq2.from_user = user
    update2 = FakeUpdate(user=user, callback_query=cq2)
    context2 = FakeContext()
    eo2 = ee.Expense(user.id)
    context2.user_data['expense_obj'] = eo2
    state2 = await enter_save(update2, context2)
    assert state2 == ee.ConversationHandler.END
    assert getattr(eo2, 'saved', False) is True

@pytest.mark.asyncio
async def test_enter_save_no_and_cancel():
    user = FakeUser(id=1)
    cq = FakeCallbackQuery(data=str(ConvState.NO))
    cq.from_user = user
    update = FakeUpdate(user=user, callback_query=cq)
    context = FakeContext()
    eo = ee.Expense(user.id)
    context.user_data['expense_obj'] = eo
    state = await enter_save(update, context)
    assert state == ee.ConversationHandler.END

    # cancel
    user = FakeUser(id=1, first_name="Bob")
    message = FakeMessage()
    update2 = FakeUpdate(user=user, message=message)
    context2 = FakeContext()
    context2.user_data['x'] = 123
    state2 = await cancel(update2, context2)
    assert state2 == ee.ConversationHandler.END
    assert context2.user_data == {}
