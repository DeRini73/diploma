from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User


class RegistrationAuthTest(APITestCase):
    def test_user_registration(self):
        """Регистрация нового пользователя."""
        url = reverse('user-list')
        data = {
            'email': 'newuser@mail.com',
            'first_name': 'Прекрасное имя',
            'last_name': 'Красивая фамилия',
            'password': 'LongPass!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('email', response.data)

    def test_jwt_authentication(self):
        """Получение JWT токена по email и паролю"""
        user = User.objects.create_user(
            email='auth@example.com',
            password='AuthPass123',
            first_name='Auth',
            last_name='Test'
        )
        url = reverse('jwt-create')
        data = {'email': 'auth@example.com', 'password': 'AuthPass123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)