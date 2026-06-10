from django.db import models


class Shop(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название магазина.')
    is_active = models.BooleanField(default=True, verbose_name='Принимает заказы.')

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории.')
    external_id = models.PositiveIntegerField(unique=True, verbose_name='Внешний ID.')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=300, verbose_name='Наименование.')
    description = models.TextField(blank=True, verbose_name='Описание.')
    model = models.CharField(max_length=200, blank=True, verbose_name='Модель.')
    external_id = models.PositiveIntegerField(verbose_name='Внешний ID.')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена.')
    price_rrc = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Рекомендованная цена.')
    quantity = models.PositiveIntegerField(verbose_name='Количество.')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        unique_together = ('external_id', 'shop')

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='parameters')
    name = models.CharField(max_length=200, verbose_name='Название характеристики.')
    value = models.CharField(max_length=500, verbose_name='Значение.')

    class Meta:
        verbose_name = 'Характеристика товара'
        verbose_name_plural = 'Характеристики товаров'

    def __str__(self):
        return f"{self.name}: {self.value}"