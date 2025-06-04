from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..utils import create_inline_keyboard

# Button definitions for different survey stages
IMPLEMENTATION_STAGE_BUTTONS = {
    "Планируем": "planning",
    "Пилотный проект": "pilot",
    "Активно внедряем": "active",
    "Уже перешли": "completed",
    "Пока не планируем": "not_planning"
}

PAIN_POINTS_BUTTONS = {
    "Функционал": "functionality",
    "Интеграция": "integration",
    "Кадры": "personnel",
    "Совместимость": "compatibility",
    "Затраты": "costs",
    "Техническая поддержка": "support"
}

FUNCTIONALITY_DETAILS_BUTTONS = {}  # No buttons, user inputs text

INTEGRATION_DETAILS_BUTTONS = {
    "очень сложно": "very_hard",
    "сложно": "hard",
    "средне": "medium",
    "легко": "easy",
    "не знаю": "dont_know",
    "другое": "other_difficulty"
}

PERSONNEL_DETAILS_BUTTONS = {
    "очень дефицит": "very_shortage",
    "дефицит": "shortage",
    "средне": "medium",
    "достаточно": "sufficient",
    "не знаю": "dont_know",
    "другое": "other_personnel"
}

COMPATIBILITY_DETAILS_BUTTONS = {
    "критично": "critical",
    "серьезно": "serious",
    "умеренно": "moderate",
    "не актуально": "not_relevant",
    "не знаю": "dont_know"
}

COSTS_DETAILS_BUTTONS = {
    "стоимость отечественного ПО": "software_cost",
    "миграция данных": "data_migration",
    "обучение персонала": "training",
    "доработка ПО под нужды предприятия": "customization",
    "аппаратное обновление": "hardware_upgrade",
    "простои производства": "downtime",
    "другое": "other_costs"
}

SUPPORT_DETAILS_BUTTONS = {
    "очень беспокоит": "very_concerned",
    "беспокоит": "concerned",
    "удовлетворительно": "satisfactory",
    "не беспокоит": "not_concerned",
    "не знаю": "dont_know"
}

MAIN_BARRIER_BUTTONS = {
    "Недостаток функционала": "lack_func",
    "Сложность интеграции": "complex_int",
    "Отсутствие специалистов": "no_specs",
    "Высокая стоимость": "high_cost",
    "Риски для производства": "prod_risks",
    "Нестабильность вендора": "vendor_inst"
}

DIRECT_REPLACEMENT_BUTTONS = {
    "Критично важно": "critical",
    "Важно": "important",
    "Желательно": "desirable",
    "Не важно": "not_important",
    "Можно": "possible",
    "Другое": "other_repl"
}

PILOT_TESTING_BUTTONS = {
    "Операционные системы (Astra Linux, РЕД ОС)": "os",
    "MES-системы (управление производством)": "mes",
    "Инженерное ПО (САПР, PLM)": "eng",
    "АСУ ТП (SCADA, HMI)": "asu",
    "ERP-системы": "erp",
    "Промышленный IoT и аналитика": "iot",
    "Кибербезопасность АСУ ТП": "cyber",
    "СУБД (Postgres Pro и др.)": "db",
    "Интеграционные платформы": "int",
    "BI-инструменты": "bi",
    "Другое": "other"
}

YES_NO_DEPENDS_BUTTONS = {
    "Да": "yes",
    "Нет": "no",
    "Зависит от решения": "depends"
}

YES_NO_BUTTONS = {
    "Да": "yes",
    "Нет": "no"
}