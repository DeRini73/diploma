from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from users.models import Contact
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, OrderStatusSerializer
from products.models import Product
from .tasks import send_order_confirmation, send_order_to_admin


class CartViewSet(viewsets.GenericViewSet):
    """Управление корзиной товаров текущего авторизованного пользователя."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer

    def get_cart(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @extend_schema(
        summary="Просмотр корзины.",
        description="Возвращает состав текущей корзины пользователя вместе со списком добавленных товаров.",
        responses={200: CartSerializer}
    )
    def list(self, request):
        cart = self.get_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @extend_schema(
        summary="Добавление товара в корзину.",
        description="Добавляет указанный товар в корзину. Если товар уже есть, увеличивает его количество.",
        request=inline_serializer(
            name='CartAddItemRequest',
            fields={
                'product_id': serializers.IntegerField(help_text="ID добавляемого товара"),
                'quantity': serializers.IntegerField(help_text="Количество товара (по умолчанию 1)", default=1, required=False)
            }
        ),
        responses={
            201: CartItemSerializer,
            400: OpenApiResponse(description="Недостаточно товара на складе."),
            404: OpenApiResponse(description="Товар не найден.")
        }
    )
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.select_related('shop').get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден.'}, status=status.HTTP_404_NOT_FOUND)

        if product.quantity < quantity:
            return Response({'error': 'Недостаточно товара на складе.'}, status=status.HTTP_400_BAD_REQUEST)

        cart = self.get_cart()
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            shop=product.shop,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()

        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Удаление позиции из корзины.",
        description="Удаляет одну товарную позицию (CartItem) из корзины текущего пользователя по её ID.",
        request=inline_serializer(
            name='CartRemoveItemRequest',
            fields={
                'item_id': serializers.IntegerField(help_text="ID позиции внутри корзины (CartItem ID)")
            }
        ),
        responses={
            204: OpenApiResponse(description="Позиция успешно удалена"),
            404: OpenApiResponse(description="Позиция не найдена")
        }
    )
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        item_id = request.data.get('item_id')
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'error': 'Позиция не найдена.'}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Очистить корзину.",
        description="Полностью удаляет все товары из корзины текущего пользователя.",
        responses={204: OpenApiResponse(description="Корзина успешно очищена")}
    )
    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self.get_cart()
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['partial_update', 'update', 'update_status']:
            return OrderStatusSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().prefetch_related('items__product')

        return Order.objects.filter(user=user).prefetch_related('items__product')

    @extend_schema(
        summary="Оформить заказ из корзины",
        description="Создает новый заказ на основе текущей корзины пользователя, списывает остатки и отправляет уведомления.",
        request=inline_serializer(
            name='OrderCreateRequest',
            fields={
                'contact_id': serializers.IntegerField(help_text="ID контакта пользователя с типом 'address'")
            }
        ),
        responses={
            201: OrderSerializer,
            400: OpenApiResponse(description="Корзина пуста или недостаточно остатков на складе"),
            404: OpenApiResponse(description="Контактные данные не найдены")
        }
    )
    @transaction.atomic
    def create(self, request):
        contact_id = request.data.get('contact_id')
        if not contact_id:
            return Response({'error': 'Укажите contact_id.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_contact = request.user.contacts.get(id=contact_id, type='address')
        except Contact.DoesNotExist:
            return Response({'error': 'Контакт не найден!'}, status=status.HTTP_404_NOT_FOUND)

        cart = Cart.objects.filter(user=request.user).prefetch_related('items__product').first()
        if not cart or not cart.items.exists():
            return Response({'error': 'Корзина пуста.'}, status=status.HTTP_400_BAD_REQUEST)

        for cart_item in cart.items.all():
            if cart_item.product.quantity < cart_item.quantity:
                return Response(
                    {'error': f'Недостаточно товара: {cart_item.product.name}.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        order = Order.objects.create(
            user=request.user,
            contact=user_contact,
            shipping_address=str(user_contact),
            status='new'
        )

        items_info = []
        total_sum = 0

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
                shop=cart_item.shop
            )

            total_sum += float(cart_item.product.price) * cart_item.quantity

            cart_item.product.quantity -= cart_item.quantity
            cart_item.product.save()
            items_info.append(f"- {cart_item.product.name} x {cart_item.quantity} ({cart_item.shop.name})")

        cart.items.all().delete()

        contact_str = str(user_contact)

        send_order_confirmation.delay(order.id, request.user.email, contact_str, total_sum)
        send_order_to_admin.delay(order.id, "\n".join(items_info), total_sum)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Изменение статуса заказа",
        description="Позволяет обновить текущий статус заказа администратором или менеджером.",
        request=OrderStatusSerializer,
        responses={
            200: OrderSerializer,
            400: OpenApiResponse(description="Передан недопустимый статус")
        }
    )
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({'error': 'Недопустимый статус!'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()

        return Response(OrderSerializer(order).data)