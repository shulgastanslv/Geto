from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_panel = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Старт')],
        [KeyboardButton(text='Мне грустно, я хочу тепла')],
        [KeyboardButton(text='Я очень зла, хочу выговориться')],
        [KeyboardButton(text='Я хочу поговорить с тобой')],
        [KeyboardButton(text='Перезагрузить')],
        [KeyboardButton(text='Кто ты?')]
    ],
    resize_keyboard=True
)

admin_panel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Старт')],
    [KeyboardButton(text='Запланировать сообщение')],
    [KeyboardButton(text='Удалить запланированное сообщение')],
    [KeyboardButton(text='Показать все запланированные сообщения')],
    [KeyboardButton(text='Кто ты?')],
    ], 
    resize_keyboard=True
)