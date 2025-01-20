import sqlite3
import logging

# Путь к базе данных (скорректируй путь в зависимости от расположения)
DB_PATH = "../Shopflowers/db.sqlite3"


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