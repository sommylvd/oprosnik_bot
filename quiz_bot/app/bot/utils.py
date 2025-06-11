from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def create_inline_keyboard(buttons_dict, columns=2, include_back=False, back_state=None):
    keyboard = []
    row = []
    for i, (text, callback_data) in enumerate(buttons_dict.items()):
        row.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        if (i + 1) % columns == 0 or i == len(buttons_dict) - 1:
            keyboard.append(row)
            row = []
    
    if include_back and back_state:
        keyboard.append([InlineKeyboardButton(text="Назад", callback_data=f"back_{back_state}")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)