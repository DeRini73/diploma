from rest_framework import serializers
from .models import Product, ProductParameter


class ProductParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductParameter
        fields = ('name', 'value')


class ProductListSerializer(serializers.ModelSerializer):
    shop = serializers.StringRelatedField()
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'shop', 'price', 'quantity')


class ProductDetailSerializer(serializers.ModelSerializer):
    shop = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    parameters = ProductParameterSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'model', 'category', 'shop',
                  'price', 'price_rrc', 'quantity', 'parameters')
