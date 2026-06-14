from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User, Contact
from products.models import Shop, Category, Product


class CartAndOrderTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='order@example.com',
            password='Order1234',
            first_name='Order',
            last_name='Test'
        )
        self.client.force_authenticate(user=self.user)

        self.shop = Shop.objects.create(name='OrderShop')
        self.category = Category.objects.create(external_id=2, name='OrderCat')
        self.product = Product.objects.create(
            name='OrderProduct',
            category=self.category,
            external_id=200,
            shop=self.shop,
            price=1000,
            price_rrc=1100,
            quantity=10
        )
        self.contact = Contact.objects.create(
            user=self.user,
            type='address',
            value='г. Тула, ул. Ленина, д. 5'
        )

    def test_cart_flow(self):
        """Тестирование работы корзины."""
        # Добавление товара в корзину.
        add_url = reverse('cart-add-item')
        data = {'product_id': self.product.id, 'quantity': 2}
        response = self.client.post(add_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Просмотр корзины.
        cart_list_url = reverse('cart-list')
        response = self.client.get(cart_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
        item_id = response.data['items'][0]['id']

        # Удаление позиции.
        remove_url = reverse('cart-remove-item')
        response = self.client.post(remove_url, {'item_id': item_id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_order(self):
        """Создание заказа, проверка уменьшения остатка и списка заказов."""
        add_url = reverse('cart-add-item')
        self.client.post(add_url, {'product_id': self.product.id, 'quantity': 3}, format='json')

        order_url = reverse('order-list')
        response = self.client.post(order_url, {'contact_id': self.contact.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id = response.data['id']
        self.assertEqual(response.data['status'], 'new')

        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 7)

        response = self.client.get(order_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

        detail_url = reverse('order-detail', args=[order_id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)

    def test_order_status_change_by_admin(self):
        """Изменение статуса заказа администратором."""
        self.client.post(reverse('cart-add-item'), {'product_id': self.product.id, 'quantity': 1}, format='json')
        order_resp = self.client.post(reverse('order-list'), {'contact_id': self.contact.id}, format='json')
        order_id = order_resp.data['id']

        admin = User.objects.create_superuser(email='admin@test.com', password='admin')
        self.client.force_authenticate(user=admin)
        status_url = reverse('order-update-status', args=[order_id])
        response = self.client.patch(status_url, {'status': 'confirmed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'confirmed')