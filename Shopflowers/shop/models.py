from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    image = models.ImageField(upload_to='products/', blank=True, verbose_name='Изображение')

    def __str__(self):
        return self.name

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

    def __str__(self):
        return f"Заказ {self.id} ({self.user.full_name})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items',
    verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Цветы')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"




