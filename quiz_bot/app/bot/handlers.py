from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
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
import re
from datetime import datetime
from app.bot.con_funcs.enterprise import create_enterprise, get_enterprises, update_enterprise
from app.bot.con_funcs.respondent import create_respondent
from app.bot.con_funcs.survey import create_survey
from app.bot.con_funcs.survey_answer import create_survey_answer
from app.bot.con_funcs.software_category import create_software_category, get_software_categories
from app.bot.con_funcs.question import create_question

router = Router()
user_responses = {}
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

# PAIN_POINTS_PAGES remains unchanged
PAIN_POINTS_PAGES = [
    {
        "label": "Функционал",
        "description": "(отсутствие нужного функционала для ваших систем/оборудования)",
        "callback_data": "functionality",
        "follow_up_state": SurveyStates.pain_points_functionality_details,
        "follow_up_message": "<b>Основные направления «болей» с которыми столкнулось ваше предприятие?</b>\n\nУкажите конкретные модули/процессы:"
    },
    {
        "label": "Интеграция",
        "description": "(уровень сложности интеграции ваших систем/оборудования с отечественным ПО)",
        "callback_data": "integration",
        "follow_up_state": SurveyStates.pain_points_integration_details,
        "follow_up_message": "<b>Основные направления «болей» с которыми столкнулось ваше предприятие?</b>\n\nУкажите уровень:",
        "follow_up_buttons": INTEGRATION_DETAILS_BUTTONS
    },
    {
        "label": "Кадры",
        "description": "(доступность специалистов с опытом работы в нужном отечественном ПО)",
        "callback_data": "personnel",
        "follow_up_state": SurveyStates.pain_points_personnel_details,
        "follow_up_message": "<b>Основные направления «болей» с которыми столкнулось ваше предприятие?</b>\n\nУкажите уровень:",
        "follow_up_buttons": PERSONNEL_DETAILS_BUTTONS
    },
    {
        "label": "Совместимость",
        "description": "(острота проблемы совместимости отечественного ПО с вашим имеющимся ПО)",
        "callback_data": "compatibility",
        "follow_up_state": SurveyStates.pain_points_compatibility_details,
        "follow_up_message": "<b>Основные направления «болей» с которыми столкнулось ваше предприятие?</b>\n\nУкажите уровень:",
        "follow_up_buttons": COMPATIBILITY_DETAILS_BUTTONS
    },
    {
        "label": "Затраты",
        "description": "(направления затрат, которые вызывают наибольшее беспокойство)",
        "callback_data": "costs",
        "follow_up_state": SurveyStates.pain_points_costs_details,
        "follow_up_message": "<b>Основные направления «болей» с которыми столкнулось ваше предприятие?</b>\n\nУкажите уровень:",
        "follow_up_buttons": COSTS_DETAILS_BUTTONS
    },
    {
        "label": "Техническая поддержка",
        "description": "(важность уровня и скорости тех. поддержки)",
        "callback_data": "support",
        "follow_up_state": SurveyStates.pain_points_support_details,
        "follow_up_message": "<b>Основные направления «болей» с которыми столкнулось ваше предприятие?</b>\n\nУкажите уровень:",
        "follow_up_buttons": SUPPORT_DETAILS_BUTTONS
    }
]

# Handlers before email remain unchanged
@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id] = {"state_history": []}
    consent_buttons = {"Согласен": "consent_agree", "Не согласен": "consent_disagree"}
    keyboard = create_inline_keyboard(consent_buttons, 2)
    await message.reply("Вы проходите опросник от АО «РНИЦ НСО» для сбора обратной связи. Согласны ли вы на обработку персональных данных вашей компании?", reply_markup=keyboard)
    await state.set_state(SurveyStates.consent)
    user_responses[user_id]["state_history"].append(SurveyStates.consent)

@router.callback_query(SurveyStates.consent, F.data == "consent_agree")
async def consent_agree(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["consent"] = True
    await callback.message.edit_text(
        "Введите полное название вашей компании или организации:",
        reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="consent")
    )
    user_responses[user_id]["last_message_id"] = callback.message.message_id
    await state.set_state(SurveyStates.company_name)
    user_responses[user_id]["state_history"].append(SurveyStates.company_name)

@router.callback_query(SurveyStates.consent, F.data == "consent_disagree")
async def consent_disagree(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Вы не дали согласие на обработку персональных данных. Опрос завершен.\n\n"
        "Для повторного прохождения опроса нажмите «Меню» и выберите команду /start.",
        reply_markup=None
    )
    await callback.answer()
    await state.clear()

@router.message(SurveyStates.company_name)
async def company_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    company_name = message.text.strip()
    if not company_name:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=user_responses[user_id]["last_message_id"],
                text="Пожалуйста, введите непустое название компании.",
                reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="consent")
            )
        except Exception as e:
            await message.answer(f"Ошибка при редактировании сообщения: {str(e)}")
        await message.delete()
        return

    user_responses[user_id]["company_name"] = company_name
    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text="Введите ИНН вашей компании:",
            reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="company_name")
        )
    except Exception as e:
        await message.answer(f"Ошибка при редактировании сообщения: {str(e)}")
        await message.delete()
        await state.clear()
        return

    await message.delete()
    await state.set_state(SurveyStates.company_inn)
    user_responses[user_id]["state_history"].append(SurveyStates.company_inn)

@router.message(SurveyStates.company_inn)
async def company_inn(message: Message, state: FSMContext):
    user_id = message.from_user.id
    inn = message.text.strip()
    
    if inn and not re.match(r'^\d{10}$|^\d{12}$', inn):
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=user_responses[user_id]["last_message_id"],
                text="Пожалуйста, введите ИНН из 10 или 12 цифр.",
                reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="company_name")
            )
        except Exception as e:
            await message.answer(f"Ошибка при редактировании сообщения: {str(e)}")
        await message.delete()
        return
    
    previous_inn = user_responses.get(user_id, {}).get("company_inn")
    
    if inn == previous_inn:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=user_responses[user_id]["last_message_id"],
                text="Введите ваше ФИО (полностью):",
                reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="company_inn")
            )
        except Exception as e:
            await message.answer(f"Ошибка при редактировании сообщения: {str(e)}")
            await message.delete()
            await state.clear()
            return
        await message.delete()
        await state.set_state(SurveyStates.full_name)
        user_responses[user_id]["state_history"].append(SurveyStates.full_name)
        return
    
    enterprise_data = {
        'name': user_responses[user_id]["company_name"],
        'inn': inn if inn else "",
        'short_name': "none"
    }
    
    try:
        enterprises = await get_enterprises()
        existing_enterprise = next((e for e in enterprises if e.get("name") == user_responses[user_id]["company_name"]), None)
        
        if existing_enterprise:
            enterprise = await update_enterprise(existing_enterprise.get("id"), enterprise_data)
            if not enterprise:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=user_responses[user_id]["last_message_id"],
                    text="Ошибка: не удалось обновить предприятие."
                )
                await message.delete()
                await state.clear()
                return
            user_responses[user_id]["company_inn"] = inn
            user_responses[user_id]["enterprise_id"] = enterprise.get("id")
        else:
            enterprise = await create_enterprise(enterprise_data)
            user_responses[user_id]["company_inn"] = inn
            user_responses[user_id]["enterprise_id"] = enterprise.get("id") if enterprise else None
        
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text="Введите ваше ФИО (полностью):",
            reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="company_inn")
        )
        await message.delete()
        await state.set_state(SurveyStates.full_name)
        user_responses[user_id]["state_history"].append(SurveyStates.full_name)
    
    except Exception as e:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text=f"Ошибка при проверке компании: {str(e)}"
        )
        await message.delete()
        await state.clear()
        return

@router.message(SurveyStates.full_name)
async def full_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    full_name = message.text.strip()
    words = full_name.split()
    if len(words) != 3 or any(len(word) < 2 for word in words):
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=user_responses[user_id]["last_message_id"],
                text="Пожалуйста, введите ФИО полностью (фамилия, имя, отчество, каждое не короче 2 символов).",
                reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="company_inn")
            )
        except Exception as e:
            await message.answer(f"Ошибка при редактировании сообщения: {str(e)}")
        await message.delete()
        return

    user_responses[user_id]["full_name"] = full_name
    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text="Введите вашу должность:",
            reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="full_name")
        )
    except Exception as e:
        await message.answer(f"Ошибка при редактировании сообщения: {str(e)}")
        await message.delete()
        await state.clear()
        return

    await message.delete()
    await state.set_state(SurveyStates.position)
    user_responses[user_id]["state_history"].append(SurveyStates.position)

@router.message(SurveyStates.position)
async def position(message: Message, state: FSMContext):
    user_id = message.from_user.id
    position = message.text.strip()
    if len(position) < 3:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=user_responses[user_id]["last_message_id"],
                text="Пожалуйста, введите должность (не менее 3 символов).",
                reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="full_name")
            )
        except Exception as e:
            await message.answer(f"Ошибка при редактировании сообщения: {str(e)}")
        await message.delete()
        return

    user_responses[user_id]["position"] = position
    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text="Введите телефон для связи:",
            reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="position")
        )
    except Exception as e:
        await message.answer(f"Ошибка при редактировании сообщения: {str(e)}")
        await message.delete()
        await state.clear()
        return

    await message.delete()
    await state.set_state(SurveyStates.phone_number)
    user_responses[user_id]["state_history"].append(SurveyStates.phone_number)

@router.message(SurveyStates.phone_number)
async def phone_number(message: Message, state: FSMContext):
    user_id = message.from_user.id
    phone = message.text.strip()
    if not re.match(r'^(\+7|8)\d{10}$', phone):
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=user_responses[user_id]["last_message_id"],
                text="Пожалуйста, введите телефон в формате +7 или 8, за которыми следуют 10 цифр (например, +79991234567).",
                reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="position")
            )
        except Exception as e:
            await message.answer(f"Ошибка при редактировании сообщения: {str(e)}")
        await message.delete()
        return

    user_responses[user_id]["phone_number"] = encrypt_data(phone)
    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text="Введите email вашей компании для связи:",
            reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="phone_number")
        )
    except Exception as e:
        await message.answer(f"Ошибка при редактировании сообщения: {str(e)}")
        await message.delete()
        await state.clear()
        return

    await message.delete()
    await state.set_state(SurveyStates.email)
    user_responses[user_id]["state_history"].append(SurveyStates.email)


@router.message(SurveyStates.email)
async def email(message: Message, state: FSMContext):
    user_id = message.from_user.id
    email_input = message.text.strip()
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email_input):
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=user_responses[user_id]["last_message_id"],
                text="Пожалуйста, введите корректный email (например, user@domain.com).",
                reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="phone_number")
            )
        except Exception as e:
            await message.answer(f"Ошибка при редактировании сообщения: {str(e)}")
        await message.delete()
        return
    
    user_responses[user_id]["email"] = encrypt_data(email_input)
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
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text=f"Ошибка при создании респондента: {str(e)}"
        )
        await message.delete()
        await state.clear()
        return

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
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text=f"Ошибка при создании опроса: {str(e)}"
        )
        await message.delete()
        await state.clear()
        return

    question_text = "1. На какой стадии перехода на отечественное ПО находится ваше предприятие?"
    try:
        question_data = {"text": question_text, "number": 1, "answer_type": "string"}
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text=f"Ошибка при работе с вопросами: {str(e)}"
        )
        await message.delete()
        await state.clear()
        return

    keyboard = create_inline_keyboard(IMPLEMENTATION_STAGE_BUTTONS, include_back=True, back_state="email")
    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text=f'<b>{question_text}</b>',
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    except Exception as e:
        await message.answer(f"Ошибка при редактировании сообщения: {str(e)}")
        await message.delete()
        await state.clear()
        return

    await message.delete()
    await state.set_state(SurveyStates.implementation_stage)
    user_responses[user_id]["state_history"].append(SurveyStates.implementation_stage)

@router.callback_query(SurveyStates.implementation_stage, F.data.in_(IMPLEMENTATION_STAGE_BUTTONS.values()))
async def implementation_stage(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    selected_stage = next((k for k, v in IMPLEMENTATION_STAGE_BUTTONS.items() if v == callback.data), None)
    user_responses[user_id]["implementation_stage"] = selected_stage

    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": selected_stage}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return

    options = PAIN_POINTS_PAGES
    options_text = "\n".join([f"- {opt['label']} {opt['description']}" for opt in options])
    buttons = {"Добавить": "choose_pain_points", "Другое": "other"}
    keyboard = create_inline_keyboard(buttons, 2, include_back=True, back_state="implementation_stage")
    await callback.message.edit_text(
        f"<b>2. Основные направления «болей» с которыми столкнулось ваше предприятие?</b>\n\n{options_text}\n\n"
        "<b>Нажмите кнопку «Добавить», чтобы выбрать подходящий вариант. Если нужного варианта нет — используйте кнопку «Другое» и укажите свой вариант вручную.</b>",
        reply_markup=keyboard, parse_mode='HTML'
    )
    user_responses[user_id]["last_message_id"] = callback.message.message_id
    await callback.answer()
    await state.set_state(SurveyStates.pain_points_selection)
    user_responses[user_id]["state_history"].append(SurveyStates.pain_points_selection)

@router.callback_query(SurveyStates.pain_points_selection, F.data == "choose_pain_points")
async def pain_points_choose(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    buttons = {opt["label"]: opt["callback_data"] for opt in PAIN_POINTS_PAGES}
    keyboard = create_inline_keyboard(buttons, 1, include_back=True, back_state="pain_points_selection")
    await callback.message.edit_text("<b>Основные направления «болей» с которыми столкнулось ваше предприятие?</b>\nВыберите один из вариантов:", reply_markup=keyboard, parse_mode='HTML')
    user_responses[user_id]["last_message_id"] = callback.message.message_id
    await callback.answer()

@router.callback_query(SurveyStates.pain_points_selection, F.data == "other")
async def pain_points_other(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.message.edit_text(
        "<b>2. Введите основные направления «болей» с которыми столкнулось ваше предприятие</b>",
        reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="pain_points_selection"),
        parse_mode='HTML'
    )
    user_responses[user_id]["last_message_id"] = callback.message.message_id
    await callback.answer()
    await state.set_state(SurveyStates.pain_points_other)
    user_responses[user_id]["state_history"].append(SurveyStates.pain_points_other)

@router.message(SurveyStates.pain_points_other)
async def pain_points_other_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id]["pain_points"] = user_responses[user_id].get("pain_points", [])
    user_responses[user_id]["pain_points"].append("other")
    user_responses[user_id]["pain_points_details"] = message.text

    question_text = "2. Основные направления «болей» с которыми столкнулось ваше предприятие? (Другое)"
    try:
        question_data = {"text": question_text, "number": 2, "answer_type": "string"}
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        sent_message = await message.answer(f"Ошибка при работе с вопросами: {str(e)}")
        user_responses[user_id]["last_message_id"] = sent_message.message_id
        await message.delete()
        await state.clear()
        return

    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": f"other: {message.text}"}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        sent_message = await message.answer(f"Ошибка при сохранении ответа: {str(e)}")
        user_responses[user_id]["last_message_id"] = sent_message.message_id
        await message.delete()
        await state.clear()
        return

    options_text = "\n".join([f"- {key}" for key in MAIN_BARRIER_BUTTONS.keys()])
    keyboard = create_inline_keyboard(MAIN_BARRIER_BUTTONS, 1, include_back=True, back_state="pain_points_selection")
    sent_message = await message.answer(
        f"<b>3. Что является главным барьером для перехода на отечественное ПО?</b>\n\n{options_text}",
        reply_markup=keyboard, parse_mode='HTML'
    )
    user_responses[user_id]["last_message_id"] = sent_message.message_id
    await message.delete()
    await state.set_state(SurveyStates.main_barrier)
    user_responses[user_id]["state_history"].append(SurveyStates.main_barrier)

@router.callback_query(SurveyStates.pain_points_selection, ~F.data.startswith("back_"))
async def pain_points_selection(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    selected_option = callback.data
    user_responses[user_id]["pain_points"] = user_responses[user_id].get("pain_points", [])
    user_responses[user_id]["pain_points"].append(selected_option)

    page = next((p for p in PAIN_POINTS_PAGES if p["callback_data"] == selected_option), None)
    if page:
        question_text = f"2. Детали для {page['label']}: {page['description']}"
        try:
            question_data = {"text": question_text, "number": 2, "answer_type": "string"}
            question = await create_question(question_data)
            user_responses[user_id]["question_id"] = question.get("id")
        except Exception as e:
            await callback.message.edit_text(f"Ошибка при работе с вопросами: {str(e)}")
            await state.clear()
            return

        if "follow_up_buttons" in page:
            keyboard = create_inline_keyboard(
                page["follow_up_buttons"], 2, include_back=True, back_state="pain_points_selection"
            )
            await callback.message.edit_text(
                f"{page['follow_up_message']}",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            keyboard = create_inline_keyboard({}, 2, include_back=True, back_state="pain_points_selection")
            await callback.message.edit_text(
                f"{page['follow_up_message']}",
                reply_markup=keyboard,
                parse_mode='HTML'
            )

        user_responses[user_id]["last_message_id"] = callback.message.message_id

        # Добавляем текущее состояние выбора болей в историю,
        # чтобы корректно работала кнопка "Назад"
        user_responses[user_id]["state_history"].append(SurveyStates.pain_points_selection)

        await state.set_state(page["follow_up_state"])
        user_responses[user_id]["state_history"].append(page["follow_up_state"])

    await callback.answer()


@router.message(SurveyStates.pain_points_functionality_details)
async def pain_points_functionality_details(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id]["pain_points_details"] = message.text
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": message.text}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text=f"Ошибка при сохранении ответа: {str(e)}"
        )
        await message.delete()
        await state.clear()
        return

    options_text = "\n".join([f"- {key}" for key in MAIN_BARRIER_BUTTONS.keys()])
    keyboard = create_inline_keyboard(MAIN_BARRIER_BUTTONS, 1, include_back=True, back_state="pain_points_selection")
    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text=f"<b>3. Что является главным барьером для перехода на отечественное ПО?</b>\n\n{options_text}",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    except Exception as e:
        await message.answer(f"Ошибка при редактировании сообщения: {str(e)}")
        await message.delete()
        await state.clear()
        return

    await message.delete()
    await state.set_state(SurveyStates.main_barrier)
    user_responses[user_id]["state_history"].append(SurveyStates.main_barrier)

@router.callback_query(SurveyStates.pain_points_integration_details)
async def pain_points_integration_details(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["pain_points_details"] = callback.data
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return

    options_text = "\n".join([f"- {key}" for key in MAIN_BARRIER_BUTTONS.keys()])
    keyboard = create_inline_keyboard(MAIN_BARRIER_BUTTONS, 1, include_back=True, back_state="pain_points_selection")
    await callback.message.edit_text(
        f"<b>3. Что является главным барьером для перехода на отечественное ПО?</b>\n\n{options_text}",
        reply_markup=keyboard, parse_mode='HTML'
    )
    user_responses[user_id]["last_message_id"] = callback.message.message_id
    await callback.answer()
    await state.set_state(SurveyStates.main_barrier)
    user_responses[user_id]["state_history"].append(SurveyStates.main_barrier)

@router.callback_query(SurveyStates.pain_points_personnel_details)
async def pain_points_personnel_details(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["pain_points_details"] = callback.data
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return

    options_text = "\n".join([f"- {key}" for key in MAIN_BARRIER_BUTTONS.keys()])
    keyboard = create_inline_keyboard(MAIN_BARRIER_BUTTONS, 1, include_back=True, back_state="pain_points_selection")
    await callback.message.edit_text(
        f"<b>3. Что является главным барьером для перехода на отечественное ПО?</b>\n\n{options_text}",
        reply_markup=keyboard, parse_mode='HTML'
    )
    user_responses[user_id]["last_message_id"] = callback.message.message_id
    await callback.answer()
    await state.set_state(SurveyStates.main_barrier)
    user_responses[user_id]["state_history"].append(SurveyStates.main_barrier)

@router.callback_query(SurveyStates.pain_points_compatibility_details)
async def pain_points_compatibility_details(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["pain_points_details"] = callback.data
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return

    options_text = "\n".join([f"- {key}" for key in MAIN_BARRIER_BUTTONS.keys()])
    keyboard = create_inline_keyboard(MAIN_BARRIER_BUTTONS, 1, include_back=True, back_state="pain_points_selection")
    await callback.message.edit_text(
        f"<b>3. Что является главным барьером для перехода на отечественное ПО?</b>\n\n{options_text}",
        reply_markup=keyboard, parse_mode='HTML'
    )
    user_responses[user_id]["last_message_id"] = callback.message.message_id
    await callback.answer()
    await state.set_state(SurveyStates.main_barrier)
    user_responses[user_id]["state_history"].append(SurveyStates.main_barrier)

@router.callback_query(SurveyStates.pain_points_costs_details)
async def pain_points_costs_details(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["pain_points_details"] = callback.data
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return

    options_text = "\n".join([f"- {key}" for key in MAIN_BARRIER_BUTTONS.keys()])
    keyboard = create_inline_keyboard(MAIN_BARRIER_BUTTONS, 1, include_back=True, back_state="pain_points_selection")
    await callback.message.edit_text(
        f"<b>3. Что является главным барьером для перехода на отечественное ПО?</b>\n\n{options_text}",
        reply_markup=keyboard, parse_mode='HTML'
    )
    user_responses[user_id]["last_message_id"] = callback.message.message_id
    await callback.answer()
    await state.set_state(SurveyStates.main_barrier)
    user_responses[user_id]["state_history"].append(SurveyStates.main_barrier)

@router.callback_query(SurveyStates.pain_points_support_details)
async def pain_points_support_details(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["pain_points_details"] = callback.data
    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return

    options_text = "\n".join([f"- {key}" for key in MAIN_BARRIER_BUTTONS.keys()])
    keyboard = create_inline_keyboard(MAIN_BARRIER_BUTTONS, 1, include_back=True, back_state="pain_points_selection")
    await callback.message.edit_text(
        f"<b>3. Что является главным барьером для перехода на отечественное ПО?</b>\n\n{options_text}",
        reply_markup=keyboard, parse_mode='HTML'
    )
    user_responses[user_id]["last_message_id"] = callback.message.message_id
    await callback.answer()
    await state.set_state(SurveyStates.main_barrier)
    user_responses[user_id]["state_history"].append(SurveyStates.main_barrier)

@router.callback_query(SurveyStates.main_barrier, F.data.in_(MAIN_BARRIER_BUTTONS.values()), ~F.data.startswith("back_"))
async def main_barrier(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["main_barrier"] = callback.data
    question_text = "3. Что является главным барьером для перехода на отечественное ПО?"
    try:
        question_data = {"text": question_text, "number": 3, "answer_type": "string"}
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return

    await callback.message.edit_text(
        "<b>4. Насколько важна для вас возможность прямого замещения зарубежного ПО на отечественное ПО?</b>",
        reply_markup=create_inline_keyboard(DIRECT_REPLACEMENT_BUTTONS, 2, include_back=True, back_state="main_barrier"),
        parse_mode='HTML'
    )
    user_responses[user_id]["last_message_id"] = callback.message.message_id
    await callback.answer()
    await state.set_state(SurveyStates.direct_replacement)
    user_responses[user_id]["state_history"].append(SurveyStates.direct_replacement)

@router.callback_query(SurveyStates.direct_replacement, F.data.in_(DIRECT_REPLACEMENT_BUTTONS.values()))
async def direct_replacement(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["direct_replacement"] = callback.data
    question_text = "4. Насколько важна для вас возможность прямого замещения зарубежного ПО на отечественное ПО?"
    try:
        question_data = {"text": question_text, "number": 4, "answer_type": "string"}
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return

    if callback.data == "other_repl":
        await callback.message.edit_text(
            "<b>4. Введите насколько важна для вас возможность прямого замещения зарубежного ПО на отечественное ПО</b>",
            reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="direct_replacement"),
            parse_mode='HTML'
        )
        user_responses[user_id]["last_message_id"] = callback.message.message_id
        await state.set_state(SurveyStates.direct_replacement_details)
        user_responses[user_id]["state_history"].append(SurveyStates.direct_replacement_details)
    else:
        await callback.message.edit_text(
            "<b>5. Готовы ли вы выделить ресурсы (время специалистов, тестовый контур) для пилотного тестирования потенциальных российских решений?</b>",
            reply_markup=create_inline_keyboard(YES_NO_DEPENDS_BUTTONS, 2, include_back=True, back_state="direct_replacement"),
            parse_mode='HTML'
        )
        user_responses[user_id]["last_message_id"] = callback.message.message_id
        await state.set_state(SurveyStates.pilot_testing)
        user_responses[user_id]["state_history"].append(SurveyStates.pilot_testing)
    await callback.answer()

@router.message(SurveyStates.direct_replacement_details)
async def direct_replacement_details(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id]["direct_replacement_details"] = message.text
    question_text = "4. Насколько важна для вас возможность прямого замещения зарубежного ПО на отечественное ПО? (Другое)"
    try:
        question_data = {"text": question_text, "number": 4, "answer_type": "string"}
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text=f"Ошибка при работе с вопросами: {str(e)}"
        )
        await message.delete()
        await state.clear()
        return

    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": f"other: {message.text}"}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text=f"Ошибка при сохранении ответа: {str(e)}"
        )
        await message.delete()
        await state.clear()
        return

    keyboard = create_inline_keyboard(YES_NO_DEPENDS_BUTTONS, 2, include_back=True, back_state="direct_replacement")
    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text="<b>5. Готовы ли вы выделить ресурсы (время специалистов, тестовый контур) для пилотного тестирования потенциальных российских решений?</b>",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    except Exception as e:
        await message.answer(f"Ошибка при редактировании сообщения: {str(e)}")
        await message.delete()
        await state.clear()
        return

    await message.delete()  # Удаляем сообщение пользователя
    await state.set_state(SurveyStates.pilot_testing)
    user_responses[user_id]["state_history"].append(SurveyStates.pilot_testing)

@router.callback_query(SurveyStates.pilot_testing, F.data.in_(YES_NO_DEPENDS_BUTTONS.values()))
async def pilot_testing(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["pilot_testing"] = callback.data
    question_text = "5. Готовы ли вы выделить ресурсы (время специалистов, тестовый контур) для пилотного тестирования потенциальных российских решений?"
    try:
        question_data = {"text": question_text, "number": 5, "answer_type": "string"}
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return

    options_text = "\n".join([f"- {key}" for key in PILOT_TESTING_BUTTONS.keys()])
    buttons = {"Добавить": "choose_software_classes", "Другое": "other"}
    keyboard = create_inline_keyboard(buttons, 2, include_back=True, back_state="pilot_testing")
    await callback.message.edit_text(
        f"<b>6. Какие классы ПО вы бы хотели протестировать?</b>\n\n{options_text}\n\n"
        "<b>Нажмите кнопку «Добавить», чтобы выбрать подходящий вариант. Если нужного варианта нет — используйте кнопку «Другое» и укажите свой вариант вручную.</b>",
        reply_markup=keyboard, parse_mode='HTML'
    )
    user_responses[user_id]["last_message_id"] = callback.message.message_id
    await callback.answer()
    await state.set_state(SurveyStates.software_classes)
    user_responses[user_id]["state_history"].append(SurveyStates.software_classes)

@router.callback_query(SurveyStates.software_classes, F.data == "choose_software_classes")
async def software_classes_choose(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    buttons = PILOT_TESTING_BUTTONS
    keyboard = create_inline_keyboard(buttons, 1, include_back=True, back_state="software_classes")
    await callback.message.edit_text(
        "<b>6. Какие классы ПО вы бы хотели протестировать?</b>\nВыберите один из вариантов:",
        reply_markup=keyboard, parse_mode='HTML'
    )
    user_responses[user_id]["last_message_id"] = callback.message.message_id
    await callback.answer()

@router.callback_query(SurveyStates.software_classes, F.data.in_(PILOT_TESTING_BUTTONS.values()))
async def software_classes(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["software_classes"] = callback.data
    
    question_text = "6. Какие классы ПО вы бы хотели протестировать?"
    try:
        question_data = {"text": question_text, "number": 6, "answer_type": "string"}
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    if callback.data != "other":
        try:
            existing_categories = await get_software_categories()
            category_exists = any(cat["name"].lower() == callback.data.lower() for cat in existing_categories)
            
            if not category_exists:
                software_category_data = {"name": callback.data, "description": "test"}
                software_category = await create_software_category(software_category_data)
                user_responses[user_id]["software_category_id"] = software_category.get("id") if software_category else None
            else:
                existing_category = next(cat for cat in existing_categories if cat["name"].lower() == callback.data.lower())
                user_responses[user_id]["software_category_id"] = existing_category.get("id")
            
            survey_answer_data = {
                "survey_id": user_responses[user_id]["survey_id"],
                "question_id": user_responses[user_id]["question_id"],
                "answer": {"value": callback.data}
            }
            await create_survey_answer(survey_answer_data)
            
            await callback.message.edit_text(
                "<b>7. Интересно ли вам участие в мероприятии, где можно пообщаться напрямую с разработчиками российского ПО?</b>",
                reply_markup=create_inline_keyboard(YES_NO_BUTTONS, 2, include_back=True, back_state="software_classes"),
                parse_mode='HTML'
            )
            user_responses[user_id]["last_message_id"] = callback.message.message_id
            await state.set_state(SurveyStates.event_interest)
            user_responses[user_id]["state_history"].append(SurveyStates.event_interest)
        except Exception as e:
            await callback.message.edit_text(f"Ошибка при обработке категории ПО: {str(e)}")
            await state.clear()
            return
    else:
        await callback.message.edit_text(
            "<b>Введите какие классы ПО вы бы хотели протестировать</b>",
            reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="software_classes"),
            parse_mode='HTML'
        )
        user_responses[user_id]["last_message_id"] = callback.message.message_id
        await state.set_state(SurveyStates.software_classes_details)
        user_responses[user_id]["state_history"].append(SurveyStates.software_classes_details)
    await callback.answer()

@router.message(SurveyStates.software_classes_details)
async def software_classes_details(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_responses[user_id]["software_classes"] = message.text
    question_text = "6. Какие классы ПО вы бы хотели протестировать? (Другое)"
    try:
        question_data = {"text": question_text, "number": 6, "answer_type": "string"}
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text=f"Ошибка при работе с вопросами: {str(e)}"
        )
        await message.delete()
        await state.clear()
        return

    software_category_data = {"name": message.text, "description": message.text}
    try:
        software_category = await create_software_category(software_category_data)
        user_responses[user_id]["software_category_id"] = software_category.get("id") if software_category else None
    except Exception as e:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text=f"Ошибка при создании категории ПО: {str(e)}"
        )
        await message.delete()
        await state.clear()
        return

    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": f"other: {message.text}"}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text=f"Ошибка при сохранении ответа: {str(e)}"
        )
        await message.delete()
        await state.clear()
        return

    keyboard = create_inline_keyboard(YES_NO_BUTTONS, 2, include_back=True, back_state="software_classes")
    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_responses[user_id]["last_message_id"],
            text="<b>7. Интересно ли вам участие в мероприятии, где можно пообщаться напрямую с разработчиками российского ПО?</b>",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    except Exception as e:
        await message.answer(f"Ошибка при редактировании сообщения: {str(e)}")
        await message.delete()
        await state.clear()
        return

    await message.delete()  # Удаляем сообщение пользователя
    await state.set_state(SurveyStates.event_interest)
    user_responses[user_id]["state_history"].append(SurveyStates.event_interest)

@router.callback_query(SurveyStates.event_interest, F.data.in_(YES_NO_BUTTONS.values()))
async def event_interest(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["event_interest"] = callback.data
    question_text = "7. Интересно ли вам участие в мероприятии, где можно пообщаться напрямую с разработчиками российского ПО?"
    try:
        question_data = {"text": question_text, "number": 7, "answer_type": "string"}
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return

    await callback.message.edit_text(
        "<b>8. Хотели бы вы, чтобы вам помогли подобрать российское решение под ваш профиль?</b>",
        reply_markup=create_inline_keyboard(YES_NO_BUTTONS, 2, include_back=True, back_state="event_interest"),
        parse_mode='HTML'
    )
    user_responses[user_id]["last_message_id"] = callback.message.message_id
    await callback.answer()
    await state.set_state(SurveyStates.solution_help)
    user_responses[user_id]["state_history"].append(SurveyStates.solution_help)

@router.callback_query(SurveyStates.solution_help, F.data.in_(YES_NO_BUTTONS.values()))
async def solution_help(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_responses[user_id]["solution_help"] = callback.data
    question_text = "8. Хотели бы вы, чтобы вам помогли подобрать российское решение под ваш профиль?"
    try:
        question_data = {"text": question_text, "number": 8, "answer_type": "string"}
        question = await create_question(question_data)
        user_responses[user_id]["question_id"] = question.get("id")
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при работе с вопросами: {str(e)}")
        await state.clear()
        return

    survey_answer_data = {
        "survey_id": user_responses[user_id]["survey_id"],
        "question_id": user_responses[user_id]["question_id"],
        "answer": {"value": callback.data}
    }
    try:
        await create_survey_answer(survey_answer_data)
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при сохранении ответа: {str(e)}")
        await state.clear()
        return

    await callback.message.edit_text("Спасибо, что прошли наш опрос!", reply_markup=None)
    user_responses[user_id]["last_message_id"] = callback.message.message_id
    await callback.answer()
    await state.clear()

@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    sent_message = await message.answer("Опрос отменен.")
    user_responses[message.from_user.id]["last_message_id"] = sent_message.message_id
    await message.delete()
    await state.clear()

@router.callback_query(F.data.startswith("back_"))
async def go_back(callback: CallbackQuery, state: FSMContext):
    back_state_key = callback.data.split("_", 1)[1]
    user_id = callback.from_user.id

    try:
        previous_state = getattr(SurveyStates, back_state_key)
    except AttributeError:
        await callback.message.edit_text("Некорректное состояние для возврата.")
        return

    await state.set_state(previous_state)

    if previous_state == SurveyStates.company_name:
        await callback.message.edit_text("Введите полное название вашей компании или организации:", reply_markup=None)

    elif previous_state == SurveyStates.company_inn:
        await callback.message.edit_text(
            "Введите ИНН вашей компании:",
            reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="company_name")
        )

    elif previous_state == SurveyStates.full_name:
        await callback.message.edit_text(
            "Введите ваше ФИО (полностью):",
            reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="company_inn")
        )

    elif previous_state == SurveyStates.position:
        await callback.message.edit_text(
            "Введите вашу должность:",
            reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="full_name")
        )

    elif previous_state == SurveyStates.phone_number:
        await callback.message.edit_text(
            "Введите телефон для связи:",
            reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="position")
        )

    elif previous_state == SurveyStates.email:
        await callback.message.edit_text(
            "Введите email вашей компании для связи:",
            reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="phone_number")
        )

    elif previous_state == SurveyStates.implementation_stage:
        question_text = "1. На какой стадии перехода на отечественное ПО находится ваше предприятие?"
        keyboard = create_inline_keyboard(IMPLEMENTATION_STAGE_BUTTONS, include_back=False)
        await callback.message.edit_text(f'<b>{question_text}</b>', reply_markup=keyboard, parse_mode='HTML')
    elif previous_state in {
        SurveyStates.pain_points_functionality_details,
        SurveyStates.pain_points_integration_details,
        SurveyStates.pain_points_personnel_details,
        SurveyStates.pain_points_compatibility_details,
        SurveyStates.pain_points_costs_details,
        SurveyStates.pain_points_support_details
    }:
        options = PAIN_POINTS_PAGES
        options_text = "\n".join([f"- {opt['label']} {opt['description']}" for opt in options])
        buttons = {"Добавить": "choose_pain_points", "Другое": "other"}
        keyboard = create_inline_keyboard(buttons, 2, include_back=True, back_state="pain_points_selection")  # ← фикс тут
        await callback.message.edit_text(
            f"<b>2. Основные направления «болей» с которыми столкнулось ваше предприятие?</b>\n\n{options_text}\n\n"
            "<b>Нажмите кнопку «Добавить», чтобы выбрать подходящий вариант. Если нужного варианта нет — используйте кнопку «Другое» и укажите свой вариант вручную.</b>",
            reply_markup=keyboard, parse_mode='HTML'
        )

    elif previous_state == SurveyStates.pain_points_selection:
        options = PAIN_POINTS_PAGES
        options_text = "\n".join([f"- {opt['label']} {opt['description']}" for opt in options])
        buttons = {"Добавить": "choose_pain_points", "Другое": "other"}
        keyboard = create_inline_keyboard(buttons, 2, include_back=True, back_state="implementation_stage")
        await callback.message.edit_text(
            f"<b>2. Основные направления «болей» с которыми столкнулось ваше предприятие?</b>\n\n{options_text}\n\n"
            "<b>Нажмите кнопку «Добавить», чтобы выбрать подходящий вариант. Если нужного варианта нет — используйте кнопку «Другое» и укажите свой вариант вручную.</b>",
            reply_markup=keyboard, parse_mode='HTML'
        )

    elif previous_state == SurveyStates.pain_points_other:
        await callback.message.edit_text(
            "<b>2. Введите основные направления «болей» с которыми столкнулось ваше предприятие</b>",
            reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="pain_points_selection"),
            parse_mode='HTML'
        )

    elif previous_state == SurveyStates.main_barrier:
        options_text = "\n".join([f"- {key}" for key in MAIN_BARRIER_BUTTONS.keys()])
        keyboard = create_inline_keyboard(MAIN_BARRIER_BUTTONS, 1, include_back=True, back_state="pain_points_selection")
        await callback.message.edit_text(
            f"<b>3. Что является главным барьером для перехода на отечественное ПО?</b>\n\n{options_text}",
            reply_markup=keyboard, parse_mode='HTML'
        )

    elif previous_state == SurveyStates.direct_replacement:
        await callback.message.edit_text(
            "<b>4. Насколько важна для вас возможность прямого замещения зарубежного ПО на отечественное ПО?</b>",
            reply_markup=create_inline_keyboard(DIRECT_REPLACEMENT_BUTTONS, 2, include_back=True, back_state="main_barrier"),
            parse_mode='HTML'
        )

    elif previous_state == SurveyStates.direct_replacement_details:
        await callback.message.edit_text(
            "<b>4. Введите насколько важна для вас возможность прямого замещения зарубежного ПО на отечественное ПО</b>",
            reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="direct_replacement"),
            parse_mode='HTML'
        )

    elif previous_state == SurveyStates.pilot_testing:
        await callback.message.edit_text(
            "<b>5. Готовы ли вы выделить ресурсы (время специалистов, тестовый контур) для пилотного тестирования потенциальных российских решений?</b>",
            reply_markup=create_inline_keyboard(YES_NO_DEPENDS_BUTTONS, 2, include_back=True, back_state="direct_replacement"),
            parse_mode='HTML'
        )

    elif previous_state == SurveyStates.software_classes:
        options_text = "\n".join([f"- {key}" for key in PILOT_TESTING_BUTTONS.keys()])
        buttons = {"Добавить": "choose_software_classes", "Другое": "other"}
        keyboard = create_inline_keyboard(buttons, 2, include_back=True, back_state="pilot_testing")
        await callback.message.edit_text(
            f"<b>6. Какие классы ПО вы бы хотели протестировать?</b>\n\n{options_text}\n\n"
            f"<b>Нажмите кнопку «Добавить», чтобы выбрать подходящий вариант. Если нужного варианта нет — используйте кнопку «Другое» и укажите свой вариант вручную.</b>",
            reply_markup=keyboard, parse_mode='HTML'
        )

    elif previous_state == SurveyStates.software_classes_details:
        await callback.message.edit_text(
            "<b>Введите какие классы ПО вы бы хотели протестировать</b>",
            reply_markup=create_inline_keyboard({}, 2, include_back=True, back_state="software_classes"),
            parse_mode='HTML'
        )

    elif previous_state == SurveyStates.event_interest:
        await callback.message.edit_text(
            "<b>7. Интересно ли вам участие в мероприятии, где можно пообщаться напрямую с разработчиками российского ПО?</b>",
            reply_markup=create_inline_keyboard(YES_NO_BUTTONS, 2, include_back=True, back_state="software_classes"),
            parse_mode='HTML'
        )

    elif previous_state == SurveyStates.solution_help:
        await callback.message.edit_text(
            "<b>8. Хотели бы вы, чтобы вам помогли подобрать российское решение под ваш профиль?</b>",
            reply_markup=create_inline_keyboard(YES_NO_BUTTONS, 2, include_back=True, back_state="event_interest"),
            parse_mode='HTML'
        )

    else:
        await callback.message.edit_text("Неизвестное состояние, возврат невозможен.")
        return

    user_responses[user_id]["last_message_id"] = callback.message.message_id
    await callback.answer()
