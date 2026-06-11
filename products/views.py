import yaml
from rest_framework import viewsets, filters, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from .models import Product, Shop, Category, ProductParameter
from .serializers import ProductListSerializer, ProductDetailSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(quantity__gt=0, shop__is_active=True).select_related('shop', 'category')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['shop', 'category']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer


class SupplierUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        yaml_data = request.data.get('file')
        if not yaml_data:
            return Response({'error': 'YAML-файл обязателен!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = yaml.safe_load(yaml_data)
        except yaml.YAMLError:
            return Response({'error': 'Некорректный YAML!'}, status=status.HTTP_400_BAD_REQUEST)

        shop_name = data.get('shop')
        if not shop_name:
            return Response({'error': 'Не указано название магазина!'}, status=status.HTTP_400_BAD_REQUEST)

        shop, _ = Shop.objects.get_or_create(name=shop_name)

        for cat_data in data.get('categories', []):
            Category.objects.get_or_create(
                external_id=cat_data['id'],
                defaults={'name': cat_data['name']}
            )

        for item in data.get('goods', []):
            category = Category.objects.get(external_id=item['category'])
            product, _ = Product.objects.update_or_create(
                external_id=item['id'],
                shop=shop,
                defaults={
                    'name': item['name'],
                    'model': item.get('model', ''),
                    'category': category,
                    'price': item['price'],
                    'price_rrc': item.get('price_rrc', item['price']),
                    'quantity': item['quantity'],
                }
            )
            product.parameters.all().delete()
            for param_name, param_value in item.get('parameters', {}).items():
                ProductParameter.objects.create(
                    product=product,
                    name=param_name,
                    value=str(param_value)
                )

        return Response({'status': 'OK', 'message': f'Прайс магазина {shop.name} обновлён.'})


class SupplierStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        shop = Shop.objects.filter(name__iexact=request.data.get('shop')).first()
        if not shop:
            return Response({'error': 'Магазин не найден!'}, status=status.HTTP_404_NOT_FOUND)

        is_active = request.data.get('is_active')
        if is_active is None:
            return Response({'error': 'Укажите признак is_active (true/false)!'}, status=status.HTTP_400_BAD_REQUEST)

        shop.is_active = is_active
        shop.save()
        return Response({'status': 'OK', 'is_active': shop.is_active})