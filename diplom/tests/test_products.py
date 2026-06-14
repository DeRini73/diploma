from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from products.models import Shop, Category, Product, ProductParameter


class ProductCatalogTest(APITestCase):
    def setUp(self):
        self.shop = Shop.objects.create(name='Test Shop', is_active=True)
        self.category = Category.objects.create(external_id=1, name='Test Category')
        self.category.shops.add(self.shop)
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            external_id=100,
            shop=self.shop,
            price=500,
            price_rrc=600,
            quantity=20
        )
        ProductParameter.objects.create(product=self.product, name='Size', value='Large')

    def test_product_list(self):
        """Получение списка товаров."""
        url = reverse('product-list')
        response = self.client.get(url, {'shop': self.shop.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_product_detail(self):
        """Представление информации о товаре."""
        url = reverse('product-detail', args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')
        self.assertIn('parameters', response.data)