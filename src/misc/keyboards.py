from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_panel = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Мне грустно, я хочу тепла')],
        [KeyboardButton(text='Я очень зла, хочу выговориться')],
        [KeyboardButton(text='Я хочу поговорить с тобой')],
        [KeyboardButton(text='Перезагрузить')]
    ],
    resize_keyboard=True
)

admin_panel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Запланировать сообщение')],
    [KeyboardButton(text='Удалить запланированное сообщение')],
    [KeyboardButton(text='Показать все запланированные сообщения')],
    ], 
    resize_keyboard=True
)