import aiosqlite

DB_PATH = "bot.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users (
            telegram_id    INTEGER PRIMARY KEY,
            username       TEXT,
            xp             INTEGER DEFAULT 0,
            level          INTEGER DEFAULT 1,
            notifications  INTEGER DEFAULT 1)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS progress (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            game_type  TEXT,
            score      INTEGER,
            played_at  TEXT)""")
        await db.commit()


async def add_user(telegram_id: int, username: str | None) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)",
            (telegram_id, username),
        )
        await db.commit()


async def get_user(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,),
        )
        return await cursor.fetchone()


async def update_xp(telegram_id: int, amount: int) -> None:
    user = await get_user(telegram_id)
    if user is None:
        return
    new_xp = user["xp"] + amount
    new_level = new_xp // 100 + 1
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET xp = ?, level = ? WHERE telegram_id = ?",
            (new_xp, new_level, telegram_id),
        )
        await db.commit()


async def record_progress(user_id: int, game_type: str, score: int) -> None:
    """Записывает игровую активность в таблицу progress."""
    from datetime import datetime

    played_at = datetime.now().isoformat(timespec="seconds")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO progress (user_id, game_type, score, played_at) VALUES (?, ?, ?, ?)",
            (user_id, game_type, score, played_at),
        )
        await db.commit()


async def get_top(limit: int = 10):
    """Топ игроков по XP."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT telegram_id, username, xp, level FROM users ORDER BY xp DESC LIMIT ?",
            (limit,),
        )
        return await cursor.fetchall()


async def set_notifications(telegram_id: int, value: int) -> None:
    """Переключает уведомления: 1 — включены, 0 — выключены."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET notifications = ? WHERE telegram_id = ?",
            (value, telegram_id),
        )
        await db.commit()