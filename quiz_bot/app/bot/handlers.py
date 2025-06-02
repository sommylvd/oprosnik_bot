from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from .states import SurveyStates
from .utils import create_inline_keyboard

router = Router()

# In-memory storage for responses (to be replaced with DB later)
user_responses = {}

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id] = {}
    await message.reply("Добро пожаловать в опрос! Начинаем.")
    await message.reply("1. Введите полное название вашей компании или организации:")
    await state.set_state(SurveyStates.company_name)

@router.message(SurveyStates.company_name)
async def company_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id]["company_name"] = message.text
    await message.reply("2. Введите должность и контакты (телефон, email) для связи:")
    await state.set_state(SurveyStates.position_and_contacts)

@router.message(SurveyStates.position_and_contacts)
async def position_and_contacts(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id]["position_and_contacts"] = message.text
    buttons = {
        "Планируем": "planning",
        "Пилотный проект": "pilot",
        "Активно внедряем": "active",
        "Уже перешли": "completed",
        "Пока не планируем": "not_planning"
    }
    keyboard = create_inline_keyboard(buttons, 2)
    await message.reply(
        "3. На какой стадии перехода на отечественное ПО находится ваше предприятие?",
        reply_markup=keyboard
    )
    await state.set_state(SurveyStates.implementation_stage)

@router.callback_query(SurveyStates.implementation_stage)
async def implementation_stage(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["implementation_stage"] = callback.data
    buttons = {
        "Функционал": "functionality",
        "Интеграция": "integration",
        "Кадры": "personnel",
        "Совместимость": "compatibility",
        "Затраты": "costs",
        "Техническая поддержка": "support"
    }
    keyboard = create_inline_keyboard(buttons, 2)
    await callback.message.reply(
        "4. Основные направления «болей» с которыми столкнулось ваше предприятие?",
        reply_markup=keyboard
    )
    await callback.answer()
    await state.set_state(SurveyStates.pain_points)

@router.callback_query(SurveyStates.pain_points)
async def pain_points(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["pain_points"] = user_responses[user_id].get("pain_points", [])
    user_responses[user_id]["pain_points"].append(callback.data)

    if callback.data == "functionality":
        await callback.message.reply("Укажите конкретные модули/процессы:")
        await state.set_state(SurveyStates.pain_points_details)
    elif callback.data == "integration":
        buttons = {
            "очень сложно": "very_hard",
            "сложно": "hard",
            "средне": "medium",
            "легко": "easy",
            "не знаю": "dont_know",
            "другое": "other_difficulty"
        }
        keyboard = create_inline_keyboard(buttons, 2)
        await callback.message.reply("Укажите уровень сложности:", reply_markup=keyboard)
        await state.set_state(SurveyStates.pain_points_details)
    else:
        buttons = {
            "Недостаток функционала": "lack_functionality",
            "Сложность интеграции": "complex_integration",
            "Отсутствие специалистов": "no_specialists",
            "Высокая стоимость": "high_cost",
            "Риски для производства": "prod_risks",
            "Нестабильность вендора": "vendor_instability"
        }
        keyboard = create_inline_keyboard(buttons, 2)
        await callback.message.reply(
            "5. Что является главным барьером для перехода на отечественное ПО?",
            reply_markup=keyboard
        )
        await state.set_state(SurveyStates.main_barrier)
    await callback.answer()

@router.message(SurveyStates.pain_points_details)
@router.callback_query(SurveyStates.pain_points_details)
async def pain_points_details(update: Message | CallbackQuery, state: FSMContext):
    user_id = update.from_user.id if isinstance(update, Message) else update.from_user.id
    user_responses[user_id]["pain_points_details"] = update.text if isinstance(update, Message) else update.data
    buttons = {
        "Недостаток функционала": "lack_functionality",
        "Сложность интеграции": "complex_integration",
        "Отсутствие специалистов": "no_specialists",
        "Высокая стоимость": "high_cost",
        "Риски для производства": "prod_risks",
        "Нестабильность вендора": "vendor_instability"
    }
    keyboard = create_inline_keyboard(buttons, 2)
    msg = update if isinstance(update, Message) else update.message
    await msg.reply(
        "5. Что является главным барьером для перехода на отечественное ПО?",
        reply_markup=keyboard
    )
    if isinstance(update, CallbackQuery):
        await update.answer()
    await state.set_state(SurveyStates.main_barrier)

@router.callback_query(SurveyStates.main_barrier)
async def main_barrier(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["main_barrier"] = callback.data
    buttons = {
        "Критично важно": "critical",
        "Важно": "important",
        "Желательно": "desirable",
        "Не важно": "not_important",
        "Можно": "possible",
        "Другое": "other_replacement"
    }
    keyboard = create_inline_keyboard(buttons, 2)
    await callback.message.reply(
        "6. Насколько важна для вас возможность прямого замещения зарубежного ПО на отечественное ПО? (аналог «один в один»)",
        reply_markup=keyboard
    )
    await callback.answer()
    await state.set_state(SurveyStates.direct_replacement)

@router.callback_query(SurveyStates.direct_replacement)
async def direct_replacement(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["direct_replacement"] = callback.data
    if callback.data == "other_replacement":
        await callback.message.reply("Введите свой вариант:")
        await state.set_state(SurveyStates.direct_replacement_details)
    else:
        buttons = {
            "Да": "yes",
            "Нет": "no",
            "Зависит от решения": "depends"
        }
        keyboard = create_inline_keyboard(buttons, 2)
        await callback.message.reply(
            "7. Готовы ли вы выделить ресурсы (время специалистов, тестовый контур) для пилотного тестирования потенциальных российских решений?",
            reply_markup=keyboard
        )
        await state.set_state(SurveyStates.pilot_testing)
    await callback.answer()

@router.message(SurveyStates.direct_replacement_details)
async def direct_replacement_details(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id]["direct_replacement_details"] = message.text
    buttons = {
        "Да": "yes",
        "Нет": "no",
        "Зависит от решения": "depends"
    }
    keyboard = create_inline_keyboard(buttons, 2)
    await message.reply(
        "7. Готовы ли вы выделить ресурсы (время специалистов, тестовый контур) для пилотного тестирования потенциальных российских решений?",
        reply_markup=keyboard
    )
    await state.set_state(SurveyStates.pilot_testing)

@router.callback_query(SurveyStates.pilot_testing)
async def pilot_testing(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["pilot_testing"] = callback.data
    buttons = {
        "os": "Операционные системы (Astra Linux, РЕД ОС)",
        "mes": "MES-системы (управление производством)",
        "eng": "Инженерное ПО (САПР, PLM)",
        "asu": "АСУ ТП (SCADA, HMI)",
        "erp": "ERP-системы",
        "iot": "Промышленный IoT и аналитика",
        "cyber": "Кибербезопасность АСУ ТП",
        "db": "СУБД (Postgres Pro и др.)",
        "int": "Интеграционные платформы",
        "bi": "BI-инструменты",
        "other": "Другое"
    }
    keyboard = create_inline_keyboard(buttons, 2)
    await callback.message.reply(
        "8. Какие классы ПО вы бы хотели протестировать? (выберите или укажите текстом)",
        reply_markup=keyboard
    )
    await callback.answer()
    await state.set_state(SurveyStates.software_classes)

@router.callback_query(SurveyStates.software_classes)
async def software_classes(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["software_classes"] = callback.data
    if callback.data == "other":
        await callback.message.reply("Введите свой вариант:")
        await state.set_state(SurveyStates.software_classes_details)
    else:
        buttons = {
            "Да": "yes",
            "Нет": "no"
        }
        keyboard = create_inline_keyboard(buttons, 2)
        await callback.message.reply(
            "9. Интересно ли вам участие в мероприятии, где можно пообщаться напрямую с разработчиками российского ПО?",
            reply_markup=keyboard
        )
        await state.set_state(SurveyStates.event_interest)
    await callback.answer()

@router.message(SurveyStates.software_classes_details)
async def software_classes_details(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id]["software_classes_details"] = message.text
    buttons = {
        "Да": "yes",
        "Нет": "no"
    }
    keyboard = create_inline_keyboard(buttons, 2)
    await message.reply(
        "9. Интересно ли вам участие в мероприятии, где можно пообщаться напрямую с разработчиками российского ПО?",
        reply_markup=keyboard
    )
    await state.set_state(SurveyStates.event_interest)

@router.callback_query(SurveyStates.event_interest)
async def event_interest(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["event_interest"] = callback.data
    buttons = {
        "Да": "yes",
        "Нет": "no"
    }
    keyboard = create_inline_keyboard(buttons, 2)
    await callback.message.reply(
        "10. Хотели ли бы вы, чтобы вам помогли подобрать российское решение под ваш профиль?",
        reply_markup=keyboard
    )
    await callback.answer()
    await state.set_state(SurveyStates.solution_help)

@router.callback_query(SurveyStates.solution_help)
async def solution_help(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["solution_help"] = callback.data
    await callback.message.reply("Спасибо, что прошли наш опрос!")
    await callback.answer()
    await state.clear()
    # Here you can save user_responses[user_id] to a database in the future

@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await message.reply("Опрос отменен.")
    await state.clear()