from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State

import app.kb as kb
import sqlite3
from database.models import DATABASE_PATH

router = Router()


class Reg(StatesGroup):
    name = State()
    surname = State()
    number = State()
    garden = State()
    confirm = State()
    edit = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Ассалому алейкум! Вас приветствует бот PlayMe. Мы рады, что вы верите, что с помощью нашего "
                         "продукта сможете создать лучшее поколение."
                         "\n\n"
                         "——————————— "
                         "\n\n"
                         "Assalomu alaykum! Sizni PlayMe boti qutlaydi. Siz bizning mahsulotimiz yordamida eng yaxshi "
                         "avlodni   yaratishingizga ishonayotganingizdan mamnunmiz. ", reply_markup=kb.main)


@router.message(F.text == "Начать регистрацию")
async def reg(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    await message.answer("Пожалуйста, укажите свое имя: \n"
                         "Iltimos, ismingizni kiriting: ")


@router.message(Reg.name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.surname)
    await message.answer('Введите вашу фамилию: \n'
                         'Familiyangizni kiriting:')


@router.message(Reg.surname)
async def reg_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await state.set_state(Reg.garden)
    await message.answer('И напоследок, укажите название детского сада, где будет создаваться лучшее поколение:\n'
                         'Va oxirida, eng yaxshi avlod yaratiladigan bolalar bog‘chasining nomini kiriting:')


@router.message(Reg.garden)
async def reg_garden(message: Message, state: FSMContext):
    await state.update_data(garden=message.text)
    await state.set_state(Reg.number)
    await message.answer('Теперь поделитесь с нами своим контактным номером:\n'
                         'Endi biz bilan aloqa raqamingizni ulashing:', reply_markup=kb.phone_number)


@router.message(Reg.number)
async def reg_number(message: Message, state: FSMContext):
    if message.contact:
        await state.update_data(number=message.contact.phone_number)
    else:
        await message.answer("Пожалуйста, отправьте номер телефона через кнопку.\n"
                             "Iltimos, telefon raqamini tugma orqali yuboring.")
        return

    await show_confirm(message, state)


async def show_confirm(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        f"Проверьте правильность введенных данных:\n"
        f"Имя: {data['name']}\n"
        f"Фамилия: {data['surname']}\n"
        f"Детский сад: {data['garden']}\n"
        f"Номер телефона: {data['number']}\n\n"
        "Все верно?", reply_markup=kb.confirm_kb
    )
    await state.set_state(Reg.confirm)


@router.message(Reg.confirm)
async def confirm_data(message: Message, state: FSMContext):
    text = message.text.lower().strip()

    if text in ('да', 'ha'):
        await save_to_database(message, state)
        await message.answer("Спасибо за регистрацию!\n"
                             "Ro'yxatdan o'tganingiz uchun tashakkur")
        await state.clear()
    elif text in ('нет', 'yo`q'):
        await message.answer("Давайте изменим данные. Введите, что хотите изменить: Имя, Фамилия, Детский сад, "
                             "Номер телефона \n"
                             "Keling, ma'lumotlarni o'zgartiraylik. O'zgartirmoqchi bo'lgan narsangizni kiriting: "
                             "Ism, familiya, bolalar bog'chasi, telefon raqami", reply_markup=kb.edit_kb)
        await state.set_state(Reg.edit)
    else:
        await message.answer("Пожалуйста, ответьте 'да' или 'нет'.")


@router.message(Reg.edit)
async def edit_data(message: Message, state: FSMContext):
    field_map = {
        'Имя': Reg.name,
        'Фамилия': Reg.surname,
        'Детский сад': Reg.garden,
        'Номер телефона': Reg.number
    }
    if message.text in field_map:
        await state.set_state(field_map[message.text])
        await message.answer(f"Введите новое значение для {message.text}: \n"
                             f"Uchun yangi qiymatni kiriting {message.text}: ")
    else:
        await message.answer("Пожалуйста, выберите одно из предложенных полей.\n"
                             "Iltimos, tavsiya etilgan maydonlardan birini tanlang.")


async def save_to_database(message: Message, state: FSMContext):
    data = await state.get_data()

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (message.from_user.id,))
        existing_user = cursor.fetchone()

        if not existing_user:
            cursor.execute(
                "INSERT INTO users (telegram_id, name, surname, garden, phone_number) VALUES (?, ?, ?, ?, ?)",
                (message.from_user.id, data["name"], data["surname"], data["garden"], data["number"]),
            )
        else:
            cursor.execute(
                "UPDATE users SET name = ?, surname = ?, garden = ?, phone_number = ? WHERE telegram_id = ?",
                (data["name"], data["surname"], data["garden"], data["number"], message.from_user.id),
            )

        conn.commit()

    except sqlite3.Error as e:
        print("Error accessing database:", e)
    finally:
        if conn:
            conn.close()
