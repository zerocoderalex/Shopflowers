import unittest
from unittest.mock import patch, MagicMock
import sqlite3
from aiogram.types import Message
from aiogram import Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot
import os
from dotenv import load_dotenv

# Импортируем функции и объекты из вашего кода
from main import get_order_status, command_start_handler  # Замените your_bot_module на название вашего модуля

load_dotenv()

# Настройка тестового бота
TOKEN = os.environ.get("TEST_TOKEN")  # Используйте отдельный токен для тестирования
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

class TestBot(unittest.TestCase):

    @patch('your_bot_module.sqlite3.connect')
    def test_get_order_status(self, mock_connect):
        # Настройка mock для базы данных
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = ("Completed", "18:00", "Test Address", "image.png", "Product x 1")

        # Вызов тестируемой функции
        order_data = get_order_status("test_order_key")

        # Проверка ожидаемого результата
        self.assertEqual(order_data['status'], "Completed")
        self.assertEqual(order_data['delivery_time'], "18:00")
        self.assertEqual(order_data['delivery_address'], "Test Address")
        self.assertEqual(order_data['items'], "Product x 1")

        # Проверка, что соединение было закрыто
        mock_conn.close.assert_called_once()

    @patch('your_bot_module.Message.answer')
    async def test_command_start_handler(self, mock_answer):
        # Создаем фейковое сообщение
        message = Message(message_id=1, date=None, chat=None, from_user=MagicMock(full_name="Test User"), text='/start')

        # Вызываем обработчикем обработчик
        await command_start_handler(message)

        # Проверяем, что ответное сообщение было отправлено
        mock_answer.assert_called_once_with(
            "Привет, <b>Test User</b>!\n\nОтправь мне ключ заказа, чтобы я сообщил статус и содержимое."
        )

if __name__ == '__main__':
    unittest.main()