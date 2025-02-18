import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

TOKEN = "7368964766:AAF-oceL5UfGT37FG2Sb1wipweOio8CoW0c" 
ADMIN_ID = 8079658819

bot = Bot(token=TOKEN)
dp = Dispatcher()

from aiogram.types import BotCommand

# Реєстрація меню команд
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустити бота 🚀")
    ]
    await bot.set_my_commands(commands)

# Стани для збору інформації
class OrderState(StatesGroup):
    name = State()   # ПІБ
    email = State()  # Email
    phone = State()  # Номер телефону

# Кнопка для надсилання номера
phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Надіслати номер", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Команда /start
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await message.answer("Для оформлення замовленя введіть свій ПІБ:")
    await state.set_state(OrderState.name)

# Отримуємо ПІБ
@dp.message(OrderState.name)
async def get_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    
    # Перевіряємо, чи є хоча б 2 слова
    if len(name.split()) < 2:
        await message.answer("⚠️ Введи повне ім'я (Прізвище Ім'я або Прізвище Ім'я По батькові).")
        return
    
    await state.update_data(name=name)
    await message.answer("Введіть свою електрону пошту (email)")
    await state.set_state(OrderState.email)

# Отримуємо Email
@dp.message(OrderState.email)
async def get_email(message: types.Message, state: FSMContext):
    email = message.text.strip()

    # Перевірка email
    if "@" not in email or "." not in email or " " in email:
        await message.answer("⚠️ Невірний формат email. Введи коректний email (наприклад, example@gmail.com).")
        return

    await state.update_data(email=email)
    await message.answer("Надішли свій номер телефону кнопкою нижче:", reply_markup=phone_kb)
    await state.set_state(OrderState.phone)

# Отримуємо номер телефону
@dp.message(OrderState.phone)
async def get_phone(message: types.Message, state: FSMContext):
    if not message.contact:
        await message.answer("⚠️ Натисни кнопку, щоб відправити номер телефону.")
        return

    phone = message.contact.phone_number
    data = await state.get_data()
    data['phone'] = phone

    # Збереження в JSON
    with open("orders.json", "a", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        file.write(",\n")

    await message.answer("✅ Замовлення прийнято! Дякуємо!", reply_markup=types.ReplyKeyboardRemove())
    
    # Відправка файлу адміну
    await bot.send_document(ADMIN_ID, FSInputFile("orders.json"))

    await state.clear()  # Очищення стану

# Запуск бота
async def main():
    await dp.start_polling(bot)

async def main():
    await set_bot_commands(bot)  # Додає кнопку в меню
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


