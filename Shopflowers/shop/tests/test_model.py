from venv import create
from django.core.files.base import ContentFile
from certifi import contents
from django.test import TestCase
from django.utils import timezone
import os
from shop.models import Product, User, Order, OrderItem


class ProductModelTest(TestCase):

    def test_product_creation(self):
        product = Product.objects.create(name='Test Product', price=10.99)
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.price, 10.99)

    def test_product_delete(self):
        product = Product.objects.create(name='Test Product', price=10.99)
        product.image.save('test_image.jpg', ContentFile(b'content'), save=False)
        product.save()
        product_path = product.image.path
        self.assertTrue(os.path.isfile(product_path))
        product.delete()
        self.assertFalse(os.path.isfile(product_path))


class UserModelTest(TestCase):

    def test_user_creation(self):
        user = User.objects.create(full_name='Test User', email='test@example.com', address='123 Street')
        self.assertEqual(user.full_name, 'Test User')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.address, '123 Street')


class OrderModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(full_name='Test User', email='test@example.com', address='123 Street')
        self.product = Product.objects.create(name='Test Product', price=10.99)

    def test_order_creation(self):
        order = Order.objects.create(user=self.user, order_key='ABC123')
        order.products.add(self.product, through_defaults={'quantity': 2})

        self.assertEqual(order.user, self.user)
        self.assertEqual(order.products.first(), self.product)
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.delivery_address, self.user.address)
        self.assertIsNotNone(order.delivery_time)

    def test_order_delivery_info(self):
        order = Order.objects.create(user=self.user, order_key='ABC123')
        delivery_info = order.delivery_info()

        self.assertEqual(delivery_info['delivery_address'], self.user.address)
        self.assertTrue(isinstance(delivery_info['delivery_time'], type(timezone.now())))


class OrderItemModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(full_name='Test User', email='test@example.com', address='123 Street')
        self.product = Product.objects.create(name='Test Product', price=10.99)
        self.order = (Order.objects.
        create(user=self.user, order_key='ABC123'))

        def test_order_item_creation(self):
            order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=3)
            self.assertEqual(order_item.order, self.order)
            self.assertEqual(order_item.product, self.product)
            self.assertEqual(order_item.quantity, 3)