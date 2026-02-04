import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from sqlalchemy import text
from src.database.db import AsyncSessionLocal
from src.services.llm_service import generate_sql_query


logger = logging.getLogger(__name__)

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я аналитический бот 🤖\n"
        "Спрашивай меня о видео, просмотрах и креаторах.\n\n"
        "Примеры:\n"
        "🔹 Сколько всего видео в базе?\n"
        "🔹 Сколько лайков у видео с id ...?\n"
        "🔹 Какой прирост просмотров был 28 ноября?"
    )

@router.message(F.text)
async def handle_analytics_query(message: Message):
    user_text = message.text
    user_id = message.from_user.id
    
    logger.info(f"User {user_id} request: {user_text}")

    status_msg = await message.answer("⏳ Думаю...")

    try:
        sql_query = await generate_sql_query(user_text)
        
        logger.info(f"Generated SQL for user {user_id}: {sql_query}")

        if sql_query == "SELECT -1":
            logger.warning(f"LLM failed to generate valid SQL for request: {user_text}")
            await status_msg.edit_text("Не удалось сгенерировать запрос к базе. Попробуйте переформулировать.")
            return

        async with AsyncSessionLocal() as session:
            result = await session.execute(text(sql_query))
            answer_number = result.scalar()
        
        if answer_number is None:
            logger.info(f"Query executed but returned None (treated as 0) for user {user_id}")
            await status_msg.edit_text("Ничего не нашлось (0).")
        else:
            logger.info(f"Success! Result: {answer_number}")
            formatted_answer = f"{answer_number:,.0f}".replace(",", " ")
            await status_msg.edit_text(formatted_answer)

    except Exception as e:
        logger.error(f"Critical error executing query for user {user_id}: {e}", exc_info=True)
        await status_msg.edit_text(f"Ошибка при выполнении запроса 😔\n(Я еще учусь)")