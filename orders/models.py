from django.db import models
from users.models import User, Contact
from products.models import Product, Shop


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name='Пользователь.')
    created_at = models.DateTimeField(auto_now_add=True,verbose_name='Дата создания.')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f"Корзина {self.user.email}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items',verbose_name='Корзина.')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар.')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество.')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин.')

    class Meta:
        verbose_name = 'Позиция корзины'
        verbose_name_plural = 'Позиции корзины'
        unique_together = ('cart', 'product', 'shop')

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый.'),
        ('confirmed', 'Подтверждён.'),
        ('processing', 'В обработке.'),
        ('delivered', 'Доставлен.'),
        ('canceled', 'Отменён.'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Пользователь.')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, verbose_name='Контакт доставки.')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус.')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания.')
    shipping_address = models.TextField(blank=True, verbose_name='Адрес доставки')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ №{self.id} от {self.created_at.strftime('%d.%m.%Y')}."


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items',verbose_name='Заказ.')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар.')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество.')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена.')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин.')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f"{self.product.name} x{self.quantity}."