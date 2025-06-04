from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from .states import SurveyStates
from .utils import create_inline_keyboard
from .keyboards.inline import (
    IMPLEMENTATION_STAGE_BUTTONS,
    PAIN_POINTS_BUTTONS,
    FUNCTIONALITY_DETAILS_BUTTONS,
    INTEGRATION_DETAILS_BUTTONS,
    PERSONNEL_DETAILS_BUTTONS,
    COMPATIBILITY_DETAILS_BUTTONS,
    COSTS_DETAILS_BUTTONS,
    SUPPORT_DETAILS_BUTTONS,
    MAIN_BARRIER_BUTTONS,
    DIRECT_REPLACEMENT_BUTTONS,
    PILOT_TESTING_BUTTONS,
    YES_NO_DEPENDS_BUTTONS,
    YES_NO_BUTTONS
)
from cryptography.fernet import Fernet
import base64
import re

router = Router()

# In-memory storage for responses (to be replaced with DB later)
user_responses = {}

# Generate a Fernet key for encryption (in production, store this securely)
fernet_key = Fernet.generate_key()
cipher_suite = Fernet(fernet_key)

def encrypt_data(data: str) -> str:
    if not data:
        return ""
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(data: str) -> str:
    if not data:
        return ""
    return cipher_suite.decrypt(data.encode()).decode()

# Pain points pages with descriptions and follow-up states
PAIN_POINTS_PAGES = [
    {
        "label": "Функционал",
        "description": "(отсутствие нужного функционала для ваших систем/оборудования)",
        "callback_data": "functionality",
        "follow_up_state": SurveyStates.pain_points_functionality_details,
        "follow_up_message": "Укажите конкретные модули/процессы:"
    },
    {
        "label": "Интеграция",
        "description": "(уровень сложности интеграции ваших систем/оборудования с отечественным ПО)",
        "callback_data": "integration",
        "follow_up_state": SurveyStates.pain_points_integration_details,
        "follow_up_message": "Укажите уровень сложности:",
        "follow_up_buttons": INTEGRATION_DETAILS_BUTTONS
    },
    {
        "label": "Кадры",
        "description": "(доступность специалистов с опытом работы в нужном отечественном ПО)",
        "callback_data": "personnel",
        "follow_up_state": SurveyStates.pain_points_personnel_details,
        "follow_up_message": "Укажите:",
        "follow_up_buttons": PERSONNEL_DETAILS_BUTTONS
    },
    {
        "label": "Совместимость",
        "description": "(острота проблемы совместимости отечественного ПО с вашим имеющимся ПО)",
        "callback_data": "compatibility",
        "follow_up_state": SurveyStates.pain_points_compatibility_details,
        "follow_up_message": "Укажите:",
        "follow_up_buttons": COMPATIBILITY_DETAILS_BUTTONS
    },
    {
        "label": "Затраты",
        "description": "(направления затрат, которые вызывают наибольшее беспокойство)",
        "callback_data": "costs",
        "follow_up_state": SurveyStates.pain_points_costs_details,
        "follow_up_message": "Укажите:",
        "follow_up_buttons": COSTS_DETAILS_BUTTONS
    },
    {
        "label": "Техническая поддержка",
        "description": "(важность уровня и скорости тех. поддержки)",
        "callback_data": "support",
        "follow_up_state": SurveyStates.pain_points_support_details,
        "follow_up_message": "Укажите:",
        "follow_up_buttons": SUPPORT_DETAILS_BUTTONS
    }
]

ITEMS_PER_PAGE = 3

def create_pagination_keyboard(current_page: int) -> InlineKeyboardMarkup:
    buttons = []
    # Navigation buttons
    nav_row = []
    if current_page > 0:
        nav_row.append(InlineKeyboardButton(text="<", callback_data=f"prev_{current_page}"))
    nav_row.append(InlineKeyboardButton(text="Выбрать", callback_data=f"choose_{current_page}"))
    if current_page < (len(PAIN_POINTS_PAGES) - 1) // ITEMS_PER_PAGE:
        nav_row.append(InlineKeyboardButton(text=">", callback_data=f"next_{current_page}"))
    buttons.append(nav_row)
    # Other button
    buttons.append([InlineKeyboardButton(text="Другое", callback_data="other")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_page_options(current_page: int) -> list:
    start_idx = current_page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    return PAIN_POINTS_PAGES[start_idx:end_idx]

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
    skip_button = {"Пропустить": "skip_position"}
    keyboard = create_inline_keyboard(skip_button, 1)
    await message.reply("2.1. Введите вашу должность:", reply_markup=keyboard)
    await state.set_state(SurveyStates.position)

@router.message(SurveyStates.position)
async def position(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id]["position"] = message.text
    skip_button = {"Пропустить": "skip_phone"}
    keyboard = create_inline_keyboard(skip_button, 1)
    await message.reply("2.2. Введите ваш номер телефона:", reply_markup=keyboard)
    await state.set_state(SurveyStates.phone_number)

@router.callback_query(SurveyStates.position, F.data == "skip_position")
async def skip_position(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["position"] = None
    skip_button = {"Пропустить": "skip_phone"}
    keyboard = create_inline_keyboard(skip_button, 1)
    await callback.message.reply("2.2. Введите ваш номер телефона:", reply_markup=keyboard)
    await callback.answer()
    await state.set_state(SurveyStates.phone_number)

@router.message(SurveyStates.phone_number)
async def phone_number(message: Message, state: FSMContext):
    user_id = message.from_user.id
    phone = message.text.strip()
    # Allow digits and an optional leading +
    if not re.match(r'^\+?\d+$', phone):
        await message.reply("Пожалуйста, введите номер телефона, содержащий только цифры (можно с ведущим +).")
        return
    user_responses[user_id]["phone_number"] = encrypt_data(phone)
    skip_button = {"Пропустить": "skip_email"}
    keyboard = create_inline_keyboard(skip_button, 1)
    await message.reply("2.3. Введите ваш email:", reply_markup=keyboard)
    await state.set_state(SurveyStates.email)

@router.callback_query(SurveyStates.phone_number, F.data == "skip_phone")
async def skip_phone(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["phone_number"] = None
    skip_button = {"Пропустить": "skip_email"}
    keyboard = create_inline_keyboard(skip_button, 1)
    await callback.message.reply("2.3. Введите ваш email:", reply_markup=keyboard)
    await callback.answer()
    await state.set_state(SurveyStates.email)

@router.message(SurveyStates.email)
async def email(message: Message, state: FSMContext):
    user_id = message.from_user.id
    email_input = message.text.strip()
    # Check if email contains @
    if '@' not in email_input:
        await message.reply("Пожалуйста, введите email, содержащий символ @.")
        return
    user_responses[user_id]["email"] = encrypt_data(email_input)
    keyboard = create_inline_keyboard(IMPLEMENTATION_STAGE_BUTTONS, 2)
    await message.reply(
        "3. На какой стадии перехода на отечественное ПО находится ваше предприятие?",
        reply_markup=keyboard
    )
    await state.set_state(SurveyStates.implementation_stage)

@router.callback_query(SurveyStates.email, F.data == "skip_email")
async def skip_email(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["email"] = None
    keyboard = create_inline_keyboard(IMPLEMENTATION_STAGE_BUTTONS, 2)
    await callback.message.reply(
        "3. На какой стадии перехода на отечественное ПО находится ваше предприятие?",
        reply_markup=keyboard
    )
    await callback.answer()
    await state.set_state(SurveyStates.implementation_stage)

@router.callback_query(SurveyStates.implementation_stage)
async def implementation_stage(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["implementation_stage"] = callback.data
    await state.update_data(current_page=0)  # Initialize page
    current_page = 0
    options = get_page_options(current_page)
    options_text = "\n".join([f"{opt['label']} {opt['description']}" for opt in options])
    keyboard = create_pagination_keyboard(current_page)
    await callback.message.reply(
        f"4. Основные направления «болей» с которыми столкнулось ваше предприятие?\n\n{options_text}",
        reply_markup=keyboard
    )
    await callback.answer()
    await state.set_state(SurveyStates.pain_points_page)

@router.callback_query(SurveyStates.pain_points_page, F.data.startswith("prev_"))
async def pain_points_prev(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get("current_page", 0)
    new_page = current_page - 1
    await state.update_data(current_page=new_page)
    options = get_page_options(new_page)
    options_text = "\n".join([f"{opt['label']} {opt['description']}" for opt in options])
    keyboard = create_pagination_keyboard(new_page)
    await callback.message.edit_text(
        f"4. Основные направления «болей» с которыми столкнулось ваше предприятие?\n\n{options_text}",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(SurveyStates.pain_points_page, F.data.startswith("next_"))
async def pain_points_next(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get("current_page", 0)
    new_page = current_page + 1
    await state.update_data(current_page=new_page)
    options = get_page_options(new_page)
    options_text = "\n".join([f"{opt['label']} {opt['description']}" for opt in options])
    keyboard = create_pagination_keyboard(new_page)
    await callback.message.edit_text(
        f"4. Основные направления «болей» с которыми столкнулось ваше предприятие?\n\n{options_text}",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(SurveyStates.pain_points_page, F.data == "other")
async def pain_points_other(callback: CallbackQuery, state: FSMContext):
    await callback.message.reply("Введите ваш вариант:")
    await callback.answer()
    await state.set_state(SurveyStates.pain_points_other)

@router.message(SurveyStates.pain_points_other)
async def pain_points_other_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id]["pain_points"] = user_responses[user_id].get("pain_points", [])
    user_responses[user_id]["pain_points"].append("other")
    user_responses[user_id]["pain_points_details"] = message.text
    keyboard = create_inline_keyboard(MAIN_BARRIER_BUTTONS, 2)
    await message.reply(
        "5. Что является главным барьером для перехода на отечественное ПО?",
        reply_markup=keyboard
    )
    await state.set_state(SurveyStates.main_barrier)

@router.callback_query(SurveyStates.pain_points_page, F.data.startswith("choose_"))
async def pain_points_choose(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get("current_page", 0)
    options = get_page_options(current_page)
    buttons = {opt["label"]: opt["callback_data"] for opt in options}
    keyboard = create_inline_keyboard(buttons, 1)
    await callback.message.reply("Выберите один из вариантов:", reply_markup=keyboard)
    await callback.answer()
    await state.set_state(SurveyStates.pain_points_selection)

@router.callback_query(SurveyStates.pain_points_selection)
async def pain_points_selection(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    selected_option = callback.data
    user_responses[user_id]["pain_points"] = user_responses[user_id].get("pain_points", [])
    user_responses[user_id]["pain_points"].append(selected_option)

    # Find the selected page data
    page = next((p for p in PAIN_POINTS_PAGES if p["callback_data"] == selected_option), None)
    if page:
        if "follow_up_buttons" in page:
            keyboard = create_inline_keyboard(page["follow_up_buttons"], 2)
            await callback.message.reply(page["follow_up_message"], reply_markup=keyboard)
        else:
            await callback.message.reply(page["follow_up_message"])
        await state.set_state(page["follow_up_state"])
    await callback.answer()

@router.message(SurveyStates.pain_points_functionality_details)
async def pain_points_functionality_details(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id]["pain_points_details"] = message.text
    keyboard = create_inline_keyboard(MAIN_BARRIER_BUTTONS, 2)
    await message.reply(
        "5. Что является главным барьером для перехода на отечественное ПО?",
        reply_markup=keyboard
    )
    await state.set_state(SurveyStates.main_barrier)

@router.callback_query(SurveyStates.pain_points_integration_details)
async def pain_points_integration_details(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["pain_points_details"] = callback.data
    keyboard = create_inline_keyboard(MAIN_BARRIER_BUTTONS, 2)
    await callback.message.reply(
        "5. Что является главным барьером для перехода на отечественное ПО?",
        reply_markup=keyboard
    )
    await callback.answer()
    await state.set_state(SurveyStates.main_barrier)

@router.callback_query(SurveyStates.pain_points_personnel_details)
async def pain_points_personnel_details(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["pain_points_details"] = callback.data
    keyboard = create_inline_keyboard(MAIN_BARRIER_BUTTONS, 2)
    await callback.message.reply(
        "5. Что является главным барьером для перехода на отечественное ПО?",
        reply_markup=keyboard
    )
    await callback.answer()
    await state.set_state(SurveyStates.main_barrier)

@router.callback_query(SurveyStates.pain_points_compatibility_details)
async def pain_points_compatibility_details(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["pain_points_details"] = callback.data
    keyboard = create_inline_keyboard(MAIN_BARRIER_BUTTONS, 2)
    await callback.message.reply(
        "5. Что является главным барьером для перехода на отечественное ПО?",
        reply_markup=keyboard
    )
    await callback.answer()
    await state.set_state(SurveyStates.main_barrier)

@router.callback_query(SurveyStates.pain_points_costs_details)
async def pain_points_costs_details(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["pain_points_details"] = callback.data
    keyboard = create_inline_keyboard(MAIN_BARRIER_BUTTONS, 2)
    await callback.message.reply(
        "5. Что является главным барьером для перехода на отечественное ПО?",
        reply_markup=keyboard
    )
    await callback.answer()
    await state.set_state(SurveyStates.main_barrier)

@router.callback_query(SurveyStates.pain_points_support_details)
async def pain_points_support_details(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["pain_points_details"] = callback.data
    keyboard = create_inline_keyboard(MAIN_BARRIER_BUTTONS, 2)
    await callback.message.reply(
        "5. Что является главным барьером для перехода на отечественное ПО?",
        reply_markup=keyboard
    )
    await callback.answer()
    await state.set_state(SurveyStates.main_barrier)

@router.callback_query(SurveyStates.main_barrier)
async def main_barrier(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["main_barrier"] = callback.data
    keyboard = create_inline_keyboard(DIRECT_REPLACEMENT_BUTTONS, 2)
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
    if callback.data == "other_repl":
        await callback.message.reply("Введите свой вариант:")
        await state.set_state(SurveyStates.direct_replacement_details)
    else:
        keyboard = create_inline_keyboard(YES_NO_DEPENDS_BUTTONS, 2)
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
    keyboard = create_inline_keyboard(YES_NO_DEPENDS_BUTTONS, 2)
    await message.reply(
        "7. Готовы ли вы выделить ресурсы (время специалистов, тестовый контур) для пилотного тестирования потенциальных российских решений?",
        reply_markup=keyboard
    )
    await state.set_state(SurveyStates.pilot_testing)

@router.callback_query(SurveyStates.pilot_testing)
async def pilot_testing(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["pilot_testing"] = callback.data
    keyboard = create_inline_keyboard(PILOT_TESTING_BUTTONS, 2)
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
        keyboard = create_inline_keyboard(YES_NO_BUTTONS, 2)
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
    keyboard = create_inline_keyboard(YES_NO_BUTTONS, 2)
    await message.reply(
        "9. Интересно ли вам участие в мероприятии, где можно пообщаться напрямую с разработчиками российского ПО?",
        reply_markup=keyboard
    )
    await state.set_state(SurveyStates.event_interest)

@router.callback_query(SurveyStates.event_interest)
async def event_interest(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["event_interest"] = callback.data
    keyboard = create_inline_keyboard(YES_NO_BUTTONS, 2)
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

@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await message.reply("Опрос отменен.")
    await state.clear()