from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from models.db import add_user, get_user
from utils.ranks import get_rank

router = Router()

# Меню из кнопок внизу экрана.
# ВАЖНО: название кнопки должно быть В ТОЧНОСТИ таким же,
# как строка в F.text == "..." ниже. Иначе кнопка молчит.
menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Курс"), KeyboardButton(text="Конвертер")],
        [KeyboardButton(text="Новости"), KeyboardButton(text="Обучение")],
        [KeyboardButton(text="Топ"), KeyboardButton(text="Настройки")],
        [KeyboardButton(text="Помощь")],
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
        "Кнопки внизу экрана — быстрый доступ ко всем функциям. "
        "Напиши /help — покажу все команды.",
        reply_markup=menu_kb,
    )


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "<b>Что я умею</b> — жми кнопки внизу экрана:\n\n"
        "Курс — актуальный курс монеты\n"
        "Конвертер — перевести криптовалюту в рубли или доллары\n"
        "Новости — свежие новости о криптовалютах\n"
        "Обучение — карточки с основами криптовалют\n"
        "Топ — таблица лидеров\n"
        "Настройки — профиль и уведомления\n\n"
        "Для быстрого набора работают и команды: "
        "/price bitcoin — курс конкретной монеты, /cancel — отменить конвертацию.\n\n"
        "За активность ты получаешь <b>XP</b>, повышаешь уровень "
        "и получаешь новые звания!",
        reply_markup=menu_kb,
    )


# ==== Обработчики нажатий на кнопки меню ====
# Каждая кнопка запускает ту же функцию, что и одноимённая команда.

@router.message(F.text == "Курс")
async def btn_price(message: Message, state: FSMContext):
    await state.clear()
    from handlers.price import cmd_price
    await cmd_price(message)


@router.message(F.text == "Конвертер")
async def btn_convert(message: Message, state: FSMContext):
    await state.clear()
    from handlers.convert import cmd_convert
    await cmd_convert(message, state)


@router.message(F.text == "Новости")
async def btn_news(message: Message, state: FSMContext):
    await state.clear()
    from handlers.news import cmd_news
    await cmd_news(message)


@router.message(F.text == "Обучение")
async def btn_learn(message: Message, state: FSMContext):
    await state.clear()
    from handlers.learn import cmd_learn
    await cmd_learn(message)


@router.message(F.text == "Топ")
async def btn_top(message: Message, state: FSMContext):
    await state.clear()
    from handlers.rating import cmd_top
    await cmd_top(message)


@router.message(F.text == "Настройки")
async def btn_settings(message: Message, state: FSMContext):
    await state.clear()
    from handlers.settings import cmd_settings
    await cmd_settings(message)


@router.message(F.text == "Помощь")
async def btn_help(message: Message, state: FSMContext):
    await cmd_help(message, state)
