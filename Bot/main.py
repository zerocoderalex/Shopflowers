import logging
import sqlite3
import os

from aiohttp import web
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
import asyncio
from dotenv import load_dotenv



load_dotenv()
TOKEN = os.environ.get("TOKEN")

# Инициализация диспетчера
dp = Dispatcher()

# Путь к базе данных
DB_PATH = "../Shopflowers/db.sqlite3"

# Получение статуса заказа
def get_order_status(order_key):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Выполняем запрос для получения информации о заказе
        cursor.execute("""
            SELECT o.status, o.delivery_time, o.delivery_address,
            GROUP_CONCAT(p.name || ' x ' || oi.quantity, ', ')
            AS items
            FROM shop_order o
            JOIN shop_orderitem oi ON o.id = oi.order_id
            JOIN shop_product p ON oi.product_id = p.id
            WHERE o.order_key = ?
        """, (order_key,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            return {"status": result[0], "delivery_time": result[1],
            "delivery_address" :result[2], "items": result[3]}
        return None
    except sqlite3.Error as e:
        conn.close()
        logging.error(f"Database error: {e}")
        return None

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Этот обработчик отвечает на команду /start
    """
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}!\n\n"
        "Отправь мне ключ заказа, чтобы я сообщил статус и содержимое."
    )


@dp.message()
async def order_status_handler(message: Message) -> None:
    """
    Обработчик сообщений: проверяет ключ заказа и возвращает статус и содержимое.
    """
    order_key = message.text.strip()
    order_data = get_order_status(order_key)

    if order_data:
        await message.answer(
            f"Статус заказа: {html.bold(order_data['status'])}\n"
            f"Содержимое заказа: {html.code(order_data['items'])}"
            f"Время доставки: {html.code(order_data['delivery_time'])}"
            f"Место доставки: {html.code(order_data['delivery_address'])}"
        )
    else:
        await message.answer(
            "Не удалось найти заказ с таким ключом. Проверьте ключ и попробуйте снова."
        )

# Запуск бота
async def main() -> None:
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())