from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from models.db import add_user, get_user
from utils.ranks import get_rank

router = Router()

# Меню из кнопок внизу экрана (сохраняется между сообщениями)
menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/price"), KeyboardButton(text="/convert")],
        [KeyboardButton(text="/news"), KeyboardButton(text="/learn")],
        [KeyboardButton(text="/top"), KeyboardButton(text="/settings")],
        [KeyboardButton(text="/help")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери кнопку или напиши команду",
)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()  # сбросим любой незавершённый диалог
    await add_user(message.from_user.id, message.from_user.username)
    user = await get_user(message.from_user.id)
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n\n"
        "Я — бот <b>«Крипто-навигатор»</b>.\n"
        "Помогу разобраться в мире криптовалют: покажу курсы монет, "
        "конвертирую валюты, расскажу свежие новости и обучу основам.\n\n"
        f"XP: <b>{user['xp']}</b> | Уровень: <b>{user['level']}</b> "
        f"— {get_rank(user['level'])}\n\n"
        "Напиши /help — покажу все команды.",
        reply_markup=menu_kb,
    )


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "<b>Список команд</b>\n\n"
        "/start — регистрация и приветствие\n"
        "/price — курс монеты (например: /price bitcoin)\n"
        "/convert — конвертер валют\n"
        "/news — свежие новости о криптовалютах\n"
        "/learn — обучающие карточки\n"
        "/top — таблица лидеров\n"
        "/settings — настройки и профиль\n"
        "/cancel — отменить конвертацию\n\n"
        "За активность ты получаешь <b>XP</b>, повышаешь уровень "
        "и получаешь новые звания!",
        reply_markup=menu_kb,
    )