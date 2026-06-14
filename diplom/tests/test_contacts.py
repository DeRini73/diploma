from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User, Contact


class ContactTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='contact@example.com',
            password='Test1234',
            first_name='Contact',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)

    def test_add_and_delete_contact(self):
        """Добавление и удаление контакта (адреса доставки)."""
        list_url = reverse('contacts-list')  # /api/v1/users/user/contacts/
        data = {'type': 'address', 'value': 'г. Москва, ул. Теплая, д. 10'}
        response = self.client.post(list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        contact_id = response.data['id']

        # Удаление контакта.
        detail_url = reverse('contacts-detail', args=[contact_id])
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)