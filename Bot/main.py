import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher, html, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
import asyncio
from dotenv import load_dotenv

import dbcontroller as db


load_dotenv()
API_HOST = "127.0.0.1"
API_PORT = 8002
TOKEN = os.environ.get("TOKEN")


bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Инициализация диспетчера
dp = Dispatcher()

# Роутеры
router = Router()

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
    db.set_user_telegram_id(order_key, message.from_user.id)
    order_data = db.get_order_status(order_key)

    if order_data:
        await message.answer(
            f"Статус заказа: {html.bold(order_data['status'])}\n"
            f"Содержимое заказа: {html.code(order_data['items'])}"
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
        status = db.get_order_status(order_key)['status']
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
    app.router.add_post("/notify", handle_notification)

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