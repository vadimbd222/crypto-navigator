"""Обработчик /convert: конвертер валют через FSM."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from models.db import record_progress, update_xp
from services.coingecko import convert
from utils.http import ServiceError

router = Router()


class ConvertState(StatesGroup):
    """Состояния диалога конвертера."""

    amount = State()  # ждём сумму
    pair = State()    # ждём пару монет


@router.message(Command("convert"))
async def cmd_convert(message: Message, state: FSMContext):
    await state.set_state(ConvertState.amount)
    await message.answer(
        "<b>🧮 Конвертер валют</b>\n\n"
        "Шаг 1 из 2. Сколько конвертируем?\n"
        "Напиши число, например: <code>5</code> или <code>0.5</code>\n\n"
        "Отмена: /cancel"
    )


@router.message(ConvertState.amount, F.text, ~F.text.startswith("/"))
async def process_amount(message: Message, state: FSMContext):
    text = (message.text or "").replace(",", ".").strip()
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Это не число 😅 Напиши сумму цифрами, например: 5")
        return
    await state.update_data(amount=amount)
    await state.set_state(ConvertState.pair)
    await message.answer(
        "Шаг 2 из 2. Что на что конвертируем?\n"
        "Напиши пару через пробел, например:\n"
        "<code>btc usd</code> — биткоины в доллары\n"
        "<code>usd ton</code> — доллары в Toncoin\n\n"
        "Монеты: btc, eth, ton, sol, doge, ada\n"
        "Валюты: usd, eur, rub"
    )


@router.message(ConvertState.pair, F.text, ~F.text.startswith("/"))
async def process_pair(message: Message, state: FSMContext):
    parts = (message.text or "").lower().split()
    if len(parts) != 2:
        await message.answer("Нужны два слова через пробел, например: <code>btc usd</code>")
        return

    data = await state.get_data()
    amount = data.get("amount", 0)
    await state.clear()
    try:
        result, explanation = await convert(amount, parts[0], parts[1])
    except ValueError as exc:
        await message.answer(f"Не понял пару: {exc}")
        return
    except (ServiceError, LookupError):
        await message.answer("⚠️ Сервис курсов временно недоступен. Попробуй позже.")
        return

    await update_xp(message.from_user.id, 5)
    await record_progress(message.from_user.id, "convert", 1)
    await message.answer(f"🧮 <b>{explanation}</b>\n\n<i>+5 XP за операцию!</i>")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Ок, конвертация отменена. Что дальше?")