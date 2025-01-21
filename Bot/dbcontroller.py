import sqlite3
import logging

# Путь к базе данных (скорректируй путь в зависимости от расположения)
DB_PATH = "../Shopflowers/db.sqlite3"
# Роутеры
router = Router()
API_HOST = "127.0.0.1"
API_PORT = 8002

def get_user_and_order_status(order_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Выполняем запрос для получения Telegram ID пользователя и статуса заказа
        cursor.execute("""
            SELECT u.address, o.order_key, o.status
            FROM shop_user u
            JOIN shop_order o ON u.id = o.user_id
            WHERE o.id = ?
        """, (order_id,))
        result = cursor.fetchone()
        return result  # Вернём результат запроса
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return None
    finally:
        conn.close()


def set_user_telegram_id(order_key, telegram_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Выполняем запрос для обновления Telegram ID в таблице shop_user
        cursor.execute("""
            UPDATE shop_user
            SET address = ?
            WHERE id = (
                SELECT user_id
                FROM shop_order
                WHERE order_key = ?
            )
        """, (telegram_id, order_key))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    finally:
        conn.close()


def get_order_status(order_key):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Выполняем запрос для получения информации о заказе
        cursor.execute("""
            SELECT o.status, GROUP_CONCAT(b.name || ' x ' || oi.quantity, ', ') AS items
            FROM shop_order o
            JOIN shop_orderitem oi ON o.id = oi.order_id
            JOIN shop_product b ON oi.product_id = b.id
            WHERE o.order_key = ?
        """, (order_key,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            return {"status": result[0], "items": result[1]}
        return None
    except sqlite3.Error as e:
        conn.close()
        logging.error(f"Database error: {e}")
        return None

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