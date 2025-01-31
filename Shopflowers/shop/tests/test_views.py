from django.test import TestCase, Client
from django.urls import reverse
from shop.models import Product, User, Order, OrderItem

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(name='Test Product', price=100)
        self.user = User.objects.create(full_name='John Doe', email='john@example.com', address='123 Main St')

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_products_view(self):
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products.html')
        self.assertIn('products', response.context)

    def test_cart_view_empty(self):
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart.html')
        self.assertEqual(response.context['total_price'], 0)

    def test_add_to_cart(self):
        response = self.client.post(reverse('add_to_cart', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(self.product.id), self.client.session['cart'])
        self.assertEqual(self.client.session['cart'][str(self.product.id)], 1)

    def test_update_cart_increment(self):
        self.client.session['cart'] = {str(self.product.id): 1}
        self.client.session.save()
        response = self.client.get(reverse('update_cart', args=[self.product.id]), {'action': 'increment'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['cart'][str(self.product.id)], 2)

    def test_update_cart_decrement(self):
        self.client.session['cart'] = {str(self.product.id): 2}
        self.client.session.save()
        response = self.client.get(reverse('update_cart', args=[self.product.id]), {'action': 'decrement'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['cart'][str(self.product.id)], 1)

    def test_order_view_empty_cart(self):
        response = self.client.get(reverse('order'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Корзина пуста!', response.content.decode())

    def test_order_creation(self):
        self.client.session['cart'] = {str(self.product.id): 1}
        self.client.session.save()
        response = self.client.post(reverse('order'), {
            'full_name': self.user.full_name,
            'email': self.user.email,
            'address': self.user.address
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Заказ успешно оформлен!', response.content.decode())
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

