import asyncio
import logging
import sqlite3
import os
from collections import defaultdict
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import FSInputFile
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get("TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# Инициализация диспетчера
dp = Dispatcher()

# Путь к базе данных (скорректируй путь в зависимости от расположения)
DB_PATH = "../Shopflowers/db.sqlite3"

active_tasks = defaultdict(dict)


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
                    "delivery_address": result[2], "image": result[3],
                    "items": result[4]}
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

async def check_order_status_periodically(order_key, chat_id):
    old_status = None
    while True:
        order_data = get_order_status(order_key)
        if order_data:
            new_status = order_data['status']
            if new_status != old_status:
                await bot.send_message(
                    chat_id,
                    f"Статус заказа изменился: {html.bold(new_status)}\n"
                    f"Содержимое заказа: {html.code(order_data['items'])}\n"
                    f"Адрес доставки: {html.code(order_data['delivery_address'])}\n"
                    f"Время доставки: {html.code(order_data['delivery_time'])}"
                )
                old_status = new_status
                if new_status.lower() == ("completed"):
                    await bot.send_message(chat_id, "Заказ доставлен.")
                     # Удаляем задачу из активных
                    if chat_id in active_tasks and order_key in active_tasks[chat_id]:
                        del active_tasks[chat_id][order_key]
                    break  # Завершаем задачу
                elif new_status.lower() == ("cancealed"):
                    await bot.send_message(chat_id, "Заказ отменен.")
                     # Удаляем задачу из активных
                    if chat_id in active_tasks and order_key in active_tasks[chat_id]:
                        del active_tasks[chat_id][order_key]
                    break
            else:
                logging.info("Статус заказа не изменился.")
        else:
            await bot.send_message(chat_id, "Не удалось найти заказ с таким ключом.")
            # Удаляем задачу из активных
            if chat_id in active_tasks and order_key in active_tasks[chat_id]:
                del active_tasks[chat_id][order_key]
            return  # Завершаем задачу, если заказ не найден
        await asyncio.sleep(18)  # Ждем 30 мин перед следующей проверкой

@dp.message()
async def order_status_handler(message: Message, bot: Bot) -> None:
    """
    Обработчик сообщений: проверяет ключ заказа и возвращает статус и содержимое.
    """
    order_key = message.text.strip()
    order_data = get_order_status(order_key)
    if order_data:
        await message.answer(
            f"Статус : {html.bold(order_data['status'])}\n"
            f"Время доставки: {html.code(order_data['delivery_time'])}"
        )

        image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Shopflowers',
        'media', order_data['image'])

        if image_path and os.path.exists(image_path):
            photo = FSInputFile(image_path)
            await bot.send_photo(chat_id=message.chat.id, photo=photo)
        else:
            await message.answer("Изображение не найдено или путь некорректный.")
            # Проверяем, не была ли задача уже запущена для этого пользователя и ключа
        if message.chat.id in active_tasks and order_key in active_tasks[message.chat.id]:
            await message.answer("Задача для этого заказа уже запущена.")
            return
        else:
            # Если вложенного словаря для message.chat.id нет, создаем его
            if message.chat.id not in active_tasks:
                active_tasks[message.chat.id] = {}
            # Запускаем периодическую проверку статуса
            task = asyncio.create_task(check_order_status_periodically(order_key, message.chat.id))
            active_tasks[message.chat.id][order_key] = task
            await message.answer("Запущена периодическая проверка статуса заказа.")
    else:
        await message.answer(
            "Не удалось найти заказ с таким ключом. Проверьте ключ и попробуйте снова."
        )

async def main() -> None:
    # Инициализация бота

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())