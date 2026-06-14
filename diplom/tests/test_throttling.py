from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.throttling import BaseThrottle
from unittest.mock import patch


class TestThrottle(BaseThrottle):
    counter = 0
    max_requests = 5

    def allow_request(self, request, view):
        TestThrottle.counter += 1
        return TestThrottle.counter <= TestThrottle.max_requests

    def wait(self):
        return 1


class ThrottlingTest(APITestCase):
    def test_anonymous_throttle(self):
        with patch('products.views.ProductViewSet.throttle_classes', [TestThrottle]):
            url = reverse('product-list')

            # Проход 200 для первых пяти запросов
            for _ in range(5):
                resp = self.client.get(url)
                self.assertEqual(resp.status_code, status.HTTP_200_OK)

            resp = self.client.get(url)
            self.assertEqual(resp.status_code, status.HTTP_429_TOO_MANY_REQUESTS)