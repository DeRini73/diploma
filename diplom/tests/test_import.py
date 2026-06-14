from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from products.models import Product, Shop, Category
from users.models import User


class ImportTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='supplier@test.ru',
            password='Test1234',
            first_name='Поставщик',
            last_name='Товаров'
        )
        self.client.force_authenticate(user=self.user)

    def test_supplier_update_endpoint(self):
        """Обновление прайса через API поставщика."""
        url = reverse('supplier-update')
        yaml_content = """
shop: NewShop
categories:
  - id: 2
    name: NewCat
goods:
  - id: 200
    category: 2
    name: New Product
    price: 500
    price_rrc: 600
    quantity: 5
    model: new/model
    parameters:
      "Size": "Large"
"""
        response = self.client.post(url, {'file': yaml_content}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Product.objects.filter(external_id=200).exists())