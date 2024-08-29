from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Начать регистрацию")]],
                           resize_keyboard=True,
                           input_field_placeholder='Нажми на кнопку')

phone_number = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Отправить номер",
                                                             request_contact=True)]],
                                   resize_keyboard=True,
                                   )
confirm_kb = ReplyKeyboardMarkup(keyboard=[[
    KeyboardButton(text="Да"),
    KeyboardButton(text="Нет")]],
    resize_keyboard=True)

edit_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Имя")],
        [KeyboardButton(text="Фамилия")],
        [KeyboardButton(text="Детский сад")],
        [KeyboardButton(text="Номер телефона")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
