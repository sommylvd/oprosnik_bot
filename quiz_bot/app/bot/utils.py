from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def create_inline_keyboard(buttons_dict, columns=2, include_back=False, back_state=None, 
                         paginate=False, current_page=0, total_pages=0):
    keyboard = []
    
    if paginate:
        # Добавляем только одну кнопку для текущей страницы
        items = list(buttons_dict.items())
        text, callback_data = items[current_page]
        keyboard.append([InlineKeyboardButton(text=text, callback_data=callback_data)])
        
        # Добавляем кнопки пагинации
        pagination_buttons = []
        if current_page > 0:
            pagination_buttons.append(InlineKeyboardButton(text="<", callback_data="prev_page"))
        if current_page < total_pages - 1:
            pagination_buttons.append(InlineKeyboardButton(text=">", callback_data="next_page"))
        if pagination_buttons:
            keyboard.append(pagination_buttons)
    else:
        # Стандартное создание клавиатуры (как было)
        row = []
        for i, (text, callback_data) in enumerate(buttons_dict.items()):
            row.append(InlineKeyboardButton(text=text, callback_data=callback_data))
            if (i + 1) % columns == 0 or i == len(buttons_dict) - 1:
                keyboard.append(row)
                row = []
    
    if include_back and back_state:
        keyboard.append([InlineKeyboardButton(text="Назад", callback_data=f"back_{back_state}")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)