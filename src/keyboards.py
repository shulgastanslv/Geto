from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_panel = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='старт')],
        [KeyboardButton(text='мне грустно, я хочу тепла')],
        [KeyboardButton(text='я очень зла, хочу выговориться')],
        [KeyboardButton(text='я хочу поговорить с тобой')],
        [KeyboardButton(text='перезагрузить')],
        [KeyboardButton(text='обновить')],
        [KeyboardButton(text='помощь')]
    ],
    resize_keyboard=True
)

admin_panel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='старт')],
    [KeyboardButton(text='запланировать сообщение')],
    [KeyboardButton(text='удалить запланированное сообщение')],
    [KeyboardButton(text='показать все запланированные сообщения')],
    [KeyboardButton(text='показать текущий контекст')],
    [KeyboardButton(text='обновить')],
    [KeyboardButton(text='помощь')],
    ], 
    resize_keyboard=True
)