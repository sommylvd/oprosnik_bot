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
    "Очень сложно": "very_hard",
    "Сложно": "hard",
    "Средне": "medium",
    "Легко": "easy",
    "Другое": "other_difficulty"
}

PERSONNEL_DETAILS_BUTTONS = {
    "Очень дефицит": "very_shortage",
    "Дефицит": "shortage",
    "Средне": "medium",
    "Достаточно": "sufficient",
    "Другое": "other_personnel"
}

COMPATIBILITY_DETAILS_BUTTONS = {
    "Критично": "critical",
    "Серьезно": "serious",
    "Умеренно": "moderate",
    "Не актуально": "not_relevant",
}

COSTS_DETAILS_BUTTONS = {
    "Стоимость отечественного ПО": "software_cost",
    "Миграция данных": "data_migration",
    "Обучение персонала": "training",
    "Доработка ПО под нужды предприятия": "customization",
    "Аппаратное обновление": "hardware_upgrade",
    "Простои производства": "downtime",
    "Другое": "other_costs"
}

SUPPORT_DETAILS_BUTTONS = {
    "Очень беспокоит": "very_concerned",
    "Беспокоит": "concerned",
    "Удовлетворительно": "satisfactory",
    "Не беспокоит": "not_concerned",
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