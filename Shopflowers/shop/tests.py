from django.test import TestCase
from django.urls import reverse
from django.core import mail

class RegistrationTest(TestCase):
    def test_registration_email(self):
        response = self.client.post(reverse('account_signup'), {
            'email': 'testuser@example.com',
             'password1': 'strongpassword',
             'password2': 'strongpassword',
        })
        # Проверьте, что пользователь был создан
        self.assertEqual(response.status_code, 302)
        # Проверьте, что одно письмо было отправлено
        self.assertEqual(len(mail.outbox), 1)
        # Проверьте, что письмо отправлено на правильный адрес
        self.assertEqual(mail.outbox[0].to, ['testuser@example.com'])