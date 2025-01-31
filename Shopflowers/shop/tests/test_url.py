from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from urllib3 import request


class URLTests(TestCase):


    def test_home_url(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_cart_url(self):
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)

    def test_order_url(self):
        response = self.client.get(reverse('order'))
        self.assertEqual(response.status_code, 200)

    def test_products_url(self):
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)

    def test_admin_url(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Обычно админка перенаправляет на страницу логина

