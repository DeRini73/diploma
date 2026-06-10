from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    shop_name = serializers.ReadOnlyField(source='shop.name')

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_name', 'shop', 'shop_name', 'quantity')
        read_only_fields = ('shop',)

    def validate(self, value):
        if value <= 0:
            raise serializers.ValidationError('Количество товара должно быть больше 0!')
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'items', 'created_at')


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    shop_name = serializers.ReadOnlyField(source='shop.name')

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price', 'shop')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    contact_info = serializers.SerializerMethodField()
    total_sum = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'contact', 'contact_info', 'status', 'created_at', 'items', 'total_sum')
        read_only_fields = ('user', 'created_at')

    def get_contact_info(self, obj):
        if obj.contact:
            return f"г. {obj.contact.city}, ул. {obj.contact.street}, д. {obj.contact.house}."
        return "Адрес не указан."

    def get_total_sum(self, obj):
        return sum(float(item.price) * item.quantity for item in obj.items.all())


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status',)