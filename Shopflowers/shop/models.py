from django.db import models
import os
from django.utils import timezone
from datetime import timedelta, datetime


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    image = models.ImageField(upload_to='products/', blank=True, verbose_name='Изображение')

    def __str__(self):
        return self.name
# Удаление лишних картинок
    def delete(self, *args, **kwargs):
        # Удаляем файл изображения из файловой системы
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

class User(models.Model):
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    email = models.EmailField(verbose_name='Email')
    address = models.TextField(verbose_name='Адрес')

    def __str__(self):
        return self.full_name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    products = models.ManyToManyField(Product, through='OrderItem', verbose_name='Цветы')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'В ожидании'),
            ('completed', 'Завершён')
        ],
        default='pending',
        verbose_name='Статус'
    )
    order_key = models.CharField(max_length=20, unique=True, verbose_name='Ключ заказа')

    delivery_address = models.TextField(default='', verbose_name='Адрес доставки')
    delivery_time = models.DateTimeField(verbose_name='Время доставки')

    def save(self, *args, **kwargs):

        # Если адрес доставки не задан, берем его из пользователя
        if not self.delivery_address and self.user:
            self.delivery_address = self.user.address

        if not self.delivery_time:  # Устанавливаем только, если значение не задано
            if self.created_at:  # Проверяем, что created_at не None
                self.delivery_time = self.created_at + timedelta(hours=24)
            else:
                self.delivery_time = timezone.now() + timedelta(hours=24)  # Или любое другое значение по умолчанию
        super().save(*args, **kwargs)

    def delivery_info(self):
        # Проверяем, что created_at не None
        if self.created_at:
            delivery_time = self.created_at + timedelta(hours=24)
        else:
            delivery_time = timezone.now() + timedelta(hours=24)  # Или любое другое значение по умолчанию

        # delivery_address = self.delivery_address  # Исправлено, чтобы использовать self.user

        return {
            'delivery_time': delivery_time,
            'delivery_address': self.delivery_address,
        }

    def __str__(self):
        return f"Заказ {self.id} ({self.user.full_name})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items',
    verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Цветы')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"




