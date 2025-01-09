from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio


api = ""
bot = Bot(token = api)
dp = Dispatcher(bot, storage= MemoryStorage())

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


def get_inline_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text="Рассчитать норму калорий", callback_data="calories"),
        InlineKeyboardButton(text="Формулы расчёта", callback_data="formulas")
    )
    return keyboard

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью.",
                         reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
                         .add("Рассчитать", "Информация"))

@dp.message_handler(text = "Рассчитать")
async def set_age(message, state):
    await message.answer("Вывберите опцию:", reply_markup=get_inline_menu())

@dp.callback_query_handler(text="formulas")
async def get_formulas(call):
    formula = "10 × вес (кг) + 6,25 × рост (см) − 5 × возраст (г) − 161"
    await call.message.answer(f"Формула Миффлина-Сан Жеора для женщин:\n{formula}")
    await call.answer()

@dp.callback_query_handler(text="calories")
async def set_age(call, state):
    await call.message.answer("Введите свой возраст:")
    await UserState.age.set()
    await call.answer()

@dp.message_handler(state= UserState.age)
async def set_growth(message, state):
    await state.update_data(age= message.text)
    await message.answer("Введите свой рост:")
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer("Введите свой вес:")
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=int(message.text))
    data = await state.get_data()
    try:
        age = int(data['age'])
        growth = int(data['growth'])
        weight = int(data['weight'])

        calories = 10 * weight + 6.25 * growth - 5 * age - 161

        await message.reply(f"Ваша норма калорий: {calories:.2f} ккал в день.")
    except ValueError:
        await message.reply("Пожалуйста, введите корректные числовые значения.")

    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)