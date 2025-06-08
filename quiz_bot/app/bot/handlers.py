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
from datetime import datetime
from app.bot.con_funcs.enterprise import create_enterprise
from app.bot.con_funcs.respondent import create_respondent
from app.bot.con_funcs.survey import create_survey
from app.bot.con_funcs.survey_answer import create_survey_answer
from app.bot.con_funcs.software_category import *
from app.bot.con_funcs.question import create_question, get_questions  # Добавили импорт

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
    nav_row = []
    if current_page > 0:
        nav_row.append(InlineKeyboardButton(text="<", callback_data=f"prev_{current_page}", disable=True if current_page == 0 else False))
    nav_row.append(InlineKeyboardButton(text="Выбрать", callback_data=f"choose_{current_page}", disable=True))
    if current_page < (len(PAIN_POINTS_PAGES) - 1) // ITEMS_PER_PAGE:
        nav_row.append(InlineKeyboardButton(text=">", callback_data=f"next_{current_page}", disable=True if current_page >= (len(PAIN_POINTS_PAGES) - 1) // ITEMS_PER_PAGE else False))
    buttons.append(nav_row)
    buttons.append([InlineKeyboardButton(text="Другое", callback_data="other", disable=True)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_page_options(current_page: int) -> list:
    start_idx = current_page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    return PAIN_POINTS_PAGES[start_idx:end_idx]

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id] = {}
    consent_buttons = {"Согласен": "consent_agree", "Не согласен": "consent_disagree"}
    keyboard = create_inline_keyboard(consent_buttons, 2)
    await message.reply("Вы проходите опросник от АО «РНИЦ НСО» для сбора обратной связи. Согласны ли вы на обработку персональных данных вашей компании?", reply_markup=keyboard)
    await state.set_state(SurveyStates.consent)

@router.callback_query(SurveyStates.consent, F.data == "consent_agree")
async def consent_agree(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["consent"] = True
    await callback.message.edit_text("Введите полное название вашей компании или организации:", reply_markup=None)
    await callback.answer()
    await state.set_state(SurveyStates.company_name)

@router.callback_query(SurveyStates.consent, F.data == "consent_disagree")
async def consent_disagree(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Вы не согласились на обработку персональных данных. Опрос завершен.", reply_markup=None)
    await callback.answer()
    await state.clear()

@router.message(SurveyStates.company_name)
async def company_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    company_name = message.text.strip()
    if not company_name:
        await message.reply("Пожалуйста, введите непустое название компании.")
        return
    user_responses[user_id]["company_name"] = company_name
    await message.reply("Введите ИНН вашей компании:")
    await state.set_state(SurveyStates.company_inn)

@router.callback_query(SurveyStates.company_name, F.data == "skip_company_name")
async def skip_company_name(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["company_name"] = None
    await callback.message.edit_text("Название компании обязательно. Пожалуйста, введите название компании.", reply_markup=None)
    await callback.answer()
    await state.set_state(SurveyStates.company_name)

@router.message(SurveyStates.company_inn)
async def company_inn(message: Message, state: FSMContext):
    user_id = message.from_user.id
    inn = message.text.strip()
    if inn and not re.match(r'^\d{10}$|^\d{12}$', inn):
        await message.reply("Пожалуйста, введите ИНН из 10 или 12 цифр.")
        return
    user_responses[user_id]["company_inn"] = inn if inn else None
    # Сохранение данных предприятия
    enterprise_data = {
        "name": user_responses[user_id]["company_name"],
        "inn": user_responses[user_id]["company_inn"] or "",
        "short_name": "none",
        "is_active": True
    }
    try:
        enterprise = await create_enterprise(enterprise_data)
        user_responses[user_id]["enterprise_id"] = enterprise.get("id") if enterprise else None
    except Exception as e:
        await message.reply(f"Ошибка при создании предприятия: {str(e)}")
        await state.clear()
        return
    await message.reply("Введите ваше ФИО (полностью):")
    await state.set_state(SurveyStates.full_name)

@router.callback_query(SurveyStates.company_inn, F.data == "skip_company_inn")
async def skip_company_inn(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["company_inn"] = None
    # Сохранение данных предприятия
    enterprise_data = {
        "name": user_responses[user_id]["company_name"],
        "inn": user_responses[user_id]["company_inn"] or "",
        "short_name": "none",
        "is_active": True
    }
    try:
        enterprise = await create_enterprise(enterprise_data)
        user_responses[user_id]["enterprise_id"] = enterprise.get("id") if enterprise else None
    except Exception as e:
        await callback.message.reply(f"Ошибка при создании предприятия: {str(e)}")
        await state.clear()
        return
    await callback.message.edit_text("Введите ваше ФИО (полностью):", reply_markup=None)
    await callback.answer()
    await state.set_state(SurveyStates.full_name)

@router.message(SurveyStates.full_name)
async def full_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id]["full_name"] = message.text
    await message.reply("Введите вашу должность:")
    await state.set_state(SurveyStates.position)

@router.callback_query(SurveyStates.full_name, F.data == "skip_full_name")
async def skip_full_name(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["full_name"] = None
    await callback.message.edit_text("Введите вашу должность:", reply_markup=None)
    await callback.answer()
    await state.set_state(SurveyStates.position)

@router.message(SurveyStates.position)
async def position(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id]["position"] = message.text
    await message.reply("Введите ваш рабочий телефон:")
    await state.set_state(SurveyStates.phone_number)

@router.callback_query(SurveyStates.position, F.data == "skip_position")
async def skip_position(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["position"] = None
    await callback.message.edit_text("Введите ваш рабочий телефон:", reply_markup=None)
    await callback.answer()
    await state.set_state(SurveyStates.phone_number)

@router.message(SurveyStates.phone_number)
async def phone_number(message: Message, state: FSMContext):
    user_id = message.from_user.id
    phone = message.text.strip()
    if not re.match(r'^\+?\d+$', phone):
        await message.reply("Пожалуйста, введите рабочий телефон, содержащий только цифры (можно с ведущим +).")
        return
    user_responses[user_id]["phone_number"] = encrypt_data(phone)
    await message.reply("Введите ваш email:")
    await state.set_state(SurveyStates.email)

@router.callback_query(SurveyStates.phone_number, F.data == "skip_phone")
async def skip_phone(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["phone_number"] = None
    await callback.message.edit_text("Введите ваш email:", reply_markup=None)
    await callback.answer()
    await state.set_state(SurveyStates.email)

@router.message(SurveyStates.email)
async def email(message: Message, state: FSMContext):
    user_id = message.from_user.id
    email_input = message.text.strip()
    if '@' not in email_input:
        await message.reply("Пожалуйста, введите email, содержащий символ @.")
        return
    user_responses[user_id]["email"] = encrypt_data(email_input)
    # Сохранение данных респондента
    phone = decrypt_data(user_responses[user_id]["phone_number"]) if user_responses[user_id]["phone_number"] else None
    email = decrypt_data(user_responses[user_id]["email"]) if user_responses[user_id]["email"] else None
    respondent_data = {
        "full_name": user_responses[user_id]["full_name"],
        "position": user_responses[user_id]["position"],
        "phone": phone,
        "email": email,
        "enterprise_id": user_responses[user_id]["enterprise_id"]
    }
    try:
        respondent = await create_respondent(respondent_data)
        user_responses[user_id]["respondent_id"] = respondent.get("id") if respondent else None
    except Exception as e:
        await message.reply(f"Ошибка при создании респондента: {str(e)}")
        await state.clear()
        return

    # Создаем опрос после создания респондента
    survey_data = {
        "title": "Survey for user " + str(user_id),
        "respondent_id": user_responses[user_id]["respondent_id"],
        "started_at": datetime.utcnow().isoformat() + "Z",
        "ip_address": "unknown",
        "user_agent": "Telegram Bot"
    }
    try:
        survey = await create_survey(survey_data)
        user_responses[user_id]["survey_id"] = survey.get("id") if survey else None
    except Exception as e:
        await message.reply(f"Ошибка при создании опроса: {str(e)}")
        await state.clear()
        return

    # Создаем вопрос о стадии перехода
    question_text = "1. На какой стадии перехода на отечественное ПО находится ваше предприятие?"
    try:
        question_data = {"text": question_text, "number": 1, "answer_type": "string"}
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await message.reply(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    keyboard = create_inline_keyboard(IMPLEMENTATION_STAGE_BUTTONS, 2)
    await message.reply(
        question_text,
        reply_markup=keyboard
    )
    await state.set_state(SurveyStates.implementation_stage)

@router.callback_query(SurveyStates.email, F.data == "skip_email")
async def skip_email(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["email"] = None
    # Сохранение данных респондента
    phone = decrypt_data(user_responses[user_id]["phone_number"]) if user_responses[user_id]["phone_number"] else None
    respondent_data = {
        "full_name": user_responses[user_id]["full_name"],
        "position": user_responses[user_id]["position"],
        "phone": phone,
        "email": None,
        "enterprise_id": user_responses[user_id]["enterprise_id"]
    }
    try:
        respondent = await create_respondent(respondent_data)
        user_responses[user_id]["respondent_id"] = respondent.get("id") if respondent else None
    except Exception as e:
        await callback.message.reply(f"Ошибка при создании респондента: {str(e)}")
        await state.clear()
        return

    # Создаем опрос после создания респондента
    survey_data = {
        "title": "Survey for user " + str(user_id),
        "respondent_id": user_responses[user_id]["respondent_id"],
        "started_at": datetime.utcnow().isoformat() + "Z",
        "ip_address": "unknown",
        "user_agent": "Telegram Bot"
    }
    try:
        survey = await create_survey(survey_data)
        user_responses[user_id]["survey_id"] = survey.get("id") if survey else None
    except Exception as e:
        await callback.message.reply(f"Ошибка при создании опроса: {str(e)}")
        await state.clear()
        return

    # Создаем вопрос о стадии перехода
    question_text = "1. На какой стадии перехода на отечественное ПО находится ваше предприятие?"
    try:
        question_data = {"text": question_text, "number": 1, "answer_type": "string"}
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await callback.message.reply(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    keyboard = create_inline_keyboard(IMPLEMENTATION_STAGE_BUTTONS, 2)
    await callback.message.reply(
        question_text,
        reply_markup=keyboard
    )
    await callback.answer()
    await state.set_state(SurveyStates.implementation_stage)

@router.callback_query(SurveyStates.implementation_stage, F.data.in_(IMPLEMENTATION_STAGE_BUTTONS.values()))
async def implementation_stage(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    selected_stage = next((k for k, v in IMPLEMENTATION_STAGE_BUTTONS.items() if v == callback.data), None)
    user_responses[user_id]["implementation_stage"] = selected_stage

    # Сохранение ответа на опрос
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": selected_stage}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.reply(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return

    await state.update_data(current_page=0)
    current_page = 0
    options = get_page_options(current_page)
    options_text = "\n".join([f"{opt['label']} {opt['description']}" for opt in options])
    keyboard = create_pagination_keyboard(current_page)
    await callback.message.edit_text(
        f"4. Основные направления «болей» с которыми столкнулось ваше предприятие?\n\n{options_text}",
        reply_markup=keyboard
    )
    await callback.answer()
    await state.set_state(SurveyStates.pain_points_page)

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
    await callback.message.edit_text("Введите ваш вариант:", reply_markup=None)
    await callback.answer()
    await state.set_state(SurveyStates.pain_points_other)

@router.message(SurveyStates.pain_points_other)
async def pain_points_other_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id]["pain_points"] = user_responses[user_id].get("pain_points", [])
    user_responses[user_id]["pain_points"].append("other")
    user_responses[user_id]["pain_points_details"] = message.text

    # Создаем новый вопрос для "other"
    question_text = f"Другое направление 'болей': {message.text}"
    try:
        question_data = {"text": question_text, "number": 4, "answer_type": "string"}  # number=4 для вопроса 4
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await message.reply(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    # Сохранение ответа на вопрос 4 (other)
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": f"other: {message.text}"}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await message.reply(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return
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
    await callback.message.edit_text("Выберите один из вариантов:", reply_markup=keyboard)
    await callback.answer()
    await state.set_state(SurveyStates.pain_points_selection)

@router.callback_query(SurveyStates.pain_points_selection)
async def pain_points_selection(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    selected_option = callback.data
    user_responses[user_id]["pain_points"] = user_responses[user_id].get("pain_points", [])
    user_responses[user_id]["pain_points"].append(selected_option)
    page = next((p for p in PAIN_POINTS_PAGES if p["callback_data"] == selected_option), None)
    if page:
        # Создаем новый вопрос для выбранного направления
        question_text = f"Детали для {page['label']}: {page['description']}"
        question_number = 4  # Устанавливаем номер для вопроса 4
        try:
            question_data = {"text": question_text, "number": question_number, "answer_type": "string"}
            question = await create_question(question_data)
            user_responses[user_id]["question_id"] = question.get("id")
        except Exception as e:
            await callback.message.reply(f"Ошибка при работе с вопросами: {str(e)}")
            await state.clear()
            return

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
    # Сохранение ответа на вопрос 4 (functionality)
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": message.text}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await message.reply(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return
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
    # Сохранение ответа на вопрос 4 (integration)
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.reply(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return
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
    # Сохранение ответа на вопрос 4 (personnel)
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.reply(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return
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
    # Сохранение ответа на вопрос 4 (compatibility)
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.reply(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return
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
    # Сохранение ответа на вопрос 4 (costs)
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.reply(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return
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
    # Сохранение ответа на вопрос 4 (support)
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.reply(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return
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
    # Создаем новый вопрос для барьера
    question_text = "5. Что является главным барьером для перехода на отечественное ПО?"
    try:
        question_data = {"text": question_text, "number": 5, "answer_type": "string"}  # number=5 для вопроса 5
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await callback.message.reply(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    # Сохранение ответа на вопрос 5
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.reply(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return
    await callback.message.edit_text(
        "6. Насколько важна для вас возможность прямого замещения зарубежного ПО на отечественное ПО? (аналог «один в один»)",
        reply_markup=create_inline_keyboard(DIRECT_REPLACEMENT_BUTTONS, 2)
    )
    await callback.answer()
    await state.set_state(SurveyStates.direct_replacement)

@router.callback_query(SurveyStates.direct_replacement)
async def direct_replacement(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["direct_replacement"] = callback.data
    # Создаем новый вопрос для замещения
    question_text = "6. Насколько важна для вас возможность прямого замещения зарубежного ПО на отечественное ПО? (аналог «один в один»)"
    try:
        question_data = {"text": question_text, "number": 6, "answer_type": "string"}  # number=6 для вопроса 6
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await callback.message.reply(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    # Сохранение ответа на вопрос 6
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.reply(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return
    if callback.data == "other_repl":
        await callback.message.edit_text("Введите свой вариант:", reply_markup=None)
        await state.set_state(SurveyStates.direct_replacement_details)
    else:
        await callback.message.edit_text(
            "7. Готовы ли вы выделить ресурсы (время специалистов, тестовый контур) для пилотного тестирования потенциальных российских решений?",
            reply_markup=create_inline_keyboard(YES_NO_DEPENDS_BUTTONS, 2)
        )
        await state.set_state(SurveyStates.pilot_testing)
    await callback.answer()

@router.message(SurveyStates.direct_replacement_details)
async def direct_replacement_details(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id]["direct_replacement_details"] = message.text
    # Создаем новый вопрос для деталей замещения
    question_text = f"Детали замещения: {message.text}"
    try:
        question_data = {"text": question_text, "number": 6, "answer_type": "string"}  # number=6 для вопроса 6 (other)
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await message.reply(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    # Сохранение ответа на вопрос 6 (other)
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": f"other: {message.text}"}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await message.reply(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return
    await message.reply(
        "7. Готовы ли вы выделить ресурсы (время специалистов, тестовый контур) для пилотного тестирования потенциальных российских решений?",
        reply_markup=create_inline_keyboard(YES_NO_DEPENDS_BUTTONS, 2)
    )
    await state.set_state(SurveyStates.pilot_testing)

@router.callback_query(SurveyStates.pilot_testing)
async def pilot_testing(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["pilot_testing"] = callback.data
    # Создаем новый вопрос для тестирования
    question_text = "7. Готовы ли вы выделить ресурсы (время специалистов, тестовый контур) для пилотного тестирования потенциальных российских решений?"
    try:
        question_data = {"text": question_text, "number": 7, "answer_type": "string"}  # number=7 для вопроса 7
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await callback.message.reply(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    # Сохранение ответа на вопрос 7
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.reply(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return
    await callback.message.edit_text(
        "8. Какие классы ПО вы бы хотели протестировать? (выберите или укажите текстом)",
        reply_markup=create_inline_keyboard(PILOT_TESTING_BUTTONS, 2)
    )
    await callback.answer()
    await state.set_state(SurveyStates.software_classes)

@router.callback_query(SurveyStates.software_classes)
async def software_classes(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["software_classes"] = callback.data
    
    # Создаем новый вопрос для классов ПО
    question_text = "8. Какие классы ПО вы бы хотели протестировать? (выберите или укажите текстом)"
    try:
        question_data = {"text": question_text, "number": 8, "answer_type": "string"}  # number=8 для вопроса 8
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await callback.message.reply(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    if callback.data != "other":
        try:
            # Проверяем, существует ли уже такая категория ПО
            existing_categories = await get_software_categories()
            category_exists = any(cat["name"].lower() == callback.data.lower() for cat in existing_categories)
            
            if not category_exists:
                # Создаем новую категорию ПО только если она не существует
                software_category_data = {"name": callback.data, "description": "string"}
                software_category = await create_software_category(software_category_data)
                user_responses[user_id]["software_category_id"] = software_category.get("id") if software_category else None
            else:
                # Если категория существует, находим её ID
                existing_category = next(cat for cat in existing_categories if cat["name"].lower() == callback.data.lower())
                user_responses[user_id]["software_category_id"] = existing_category.get("id")
            
            # Сохранение ответа на вопрос 8
            survey_answer_data = {
                "survey_id": user_responses[user_id]["survey_id"],
                "question_id": user_responses[user_id]["question_id"],
                "answer": {"value": callback.data}
            }
            await create_survey_answer(survey_answer_data)
            
            await callback.message.edit_text(
                "9. Интересно ли вам участие в мероприятии, где можно пообщаться напрямую с разработчиками российского ПО?",
                reply_markup=create_inline_keyboard(YES_NO_BUTTONS, 2)
            )
            await state.set_state(SurveyStates.event_interest)
            
        except Exception as e:
            await callback.message.reply(f"Ошибка при обработке категории ПО: {str(e)}")
            await state.clear()
            return
    else:
        await callback.message.edit_text("Введите свой вариант:", reply_markup=None)
        await state.set_state(SurveyStates.software_classes_details)
    
    await callback.answer()

@router.message(SurveyStates.software_classes_details)
async def software_classes_details(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id]["software_classes_details"] = message.text
    # Создаем новый вопрос для деталей классов ПО
    question_text = f"Детали классов ПО: {message.text}"
    try:
        question_data = {"text": question_text, "number": 8, "answer_type": "string"}  # number=8 для вопроса 8 (other)
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await message.reply(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    # Сохранение категории ПО (пользовательский ввод)
    software_category_data = {"name": message.text, "description": message.text}
    software_category = await create_software_category(software_category_data)
    user_responses[user_id]["software_category_id"] = software_category.get("id") if software_category else None
    # Сохранение ответа на вопрос 8 (other)
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": f"other: {message.text}"}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await message.reply(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return
    await message.reply(
        "9. Интересно ли вам участие в мероприятии, где можно пообщаться напрямую с разработчиками российского ПО?",
        reply_markup=create_inline_keyboard(YES_NO_BUTTONS, 2)
    )
    await state.set_state(SurveyStates.event_interest)

@router.callback_query(SurveyStates.event_interest)
async def event_interest(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["event_interest"] = callback.data
    # Создаем новый вопрос для интереса к мероприятию
    question_text = "9. Интересно ли вам участие в мероприятии, где можно пообщаться напрямую с разработчиками российского ПО?"
    try:
        question_data = {"text": question_text, "number": 9, "answer_type": "string"}  # number=9 для вопроса 9
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await callback.message.reply(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    # Сохранение ответа на вопрос 9
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.reply(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return
    await callback.message.edit_text(
        "10. Хотели ли бы вы, чтобы вам помогли подобрать российское решение под ваш профиль?",
        reply_markup=create_inline_keyboard(YES_NO_BUTTONS, 2)
    )
    await callback.answer()
    await state.set_state(SurveyStates.solution_help)

@router.callback_query(SurveyStates.solution_help)
async def solution_help(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["solution_help"] = callback.data
    # Создаем новый вопрос для помощи с решением
    question_text = "10. Хотели ли бы вы, чтобы вам помогли подобрать российское решение под ваш профиль?"
    try:
        question_data = {"text": question_text, "number": 10, "answer_type": "string"}  # number=10 для вопроса 10
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await callback.message.reply(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    # Сохранение ответа на вопрос 10
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.reply(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return
    await callback.message.edit_text("Спасибо, что прошли наш опрос!", reply_markup=None)
    await callback.answer()
    await state.clear()

@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await message.reply("Опрос отменен.")
    await state.clear()