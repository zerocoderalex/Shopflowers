import asyncio
import logging
import sqlite3
import os

from aiohttp import web
from aiogram import Bot, Dispatcher, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.environ.get("TOKEN")

API_HOST = "127.0.0.1"
API_PORT = 8002

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Инициализация диспетчера
dp = Dispatcher()

# Роутеры
router = Router()

# Путь к базе данных
DB_PATH = "../Shopflowers/db.sqlite3"


def get_user_and_order_status(order_key):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Выполняем запрос для получения информации о заказе
        cursor.execute("""
            SELECT u.telegram, o.order_key, o.status 
            FROM shop_user u
            JOIN shop_order o ON u.id = o.user_id
            WHERE o.id = ?
        """, (order_key,))
        result = cursor.fetchone()
        return result
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return None
    finally:
        conn.close()


# Получение телеграм_id
def set_user_telegram_id(order_key, telegram_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE shop_user 
            SET telegram = ?
            WHERE id = (
                SELECT user_id
                FROM shop_order
                WHERE order_key = ?
            )
        """, (telegram_id,order_key,))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"database error: {e}")
    finally:
        conn.close()


    # Получение статуса заказа
def get_order_status(order_key):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Выполняем запрос для получения информации о заказе
        cursor.execute("""
            SELECT o.status, o.delivery_time, o.delivery_address, p.image, 
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
            "delivery_address": result[2], "image": result[3], "items": result[4]}
        return None
    except sqlite3.Error as e:
        conn.close()
        logging.error(f"Database error: {e}")
        return None


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Этот обработчик отвечает на команду /start
    """
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}!\n\n"
        "Отправь мне ключ заказа, чтобы я сообщил статус и содержимое."
    )


@router.message()
async def order_status_handler(message: Message) -> None:
    """
    Обработчик сообщений: проверяет ключ заказа и возвращает статус и содержимое.
    """
    order_key = message.text.strip()
    set_user_telegram_id(order_key, message.from_user.id)
    order_data = get_order_status(order_key)

    if order_data:
        await message.answer(
            f"Статус заказа: {html.bold(order_data['status'])}\n"
            f"Содержимое заказа: {html.code(order_data['items'])}"
            f"Время доставки: {html.code(order_data['delivery_time'])}"
            f"Место доставки: {html.code(order_data['delivery_address'])}"
            f"Изображение: {html.code(order_data['image'])}"
        )
    else:
        await message.answer(
            "Не удалось найти заказ с таким ключом. Проверьте ключ и попробуйте снова."
        )


async def notify_user(telegram_id: int, order_key: str):
    """
    Уведомляет пользователя о смене статуса заказа.
    """
    try:
        status = get_order_status(order_key)['status']
        message = f"Статус вашего заказа {order_key} изменён на {status}."
        await bot.send_message(chat_id=telegram_id, text=message)
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")


async def handle_notification(request):
            """
            Обрабатывает входящий HTTP-запрос для уведомления пользователя.
            """
            data = await request.json()

            telegram_id = data.get("telegram_id")
            order_key = data.get("order_key")

            if not telegram_id or not order_key:
                return web.json_response({"error": "Invalid data"}, status=400)

            # Уведомляем пользователя
            await notify_user(telegram_id, order_key)

            return web.json_response({"success": True})



async def main():
    app = web.Application()
    dp.include_router(router)

    # Регистрируем API-эндпоинт
    # app.router.add_post("/notify", handle_notification)

    # Запускаем сервер
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, API_HOST, API_PORT)
    await site.start()

    print(f"API запущено на {API_HOST}:{API_PORT}")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())