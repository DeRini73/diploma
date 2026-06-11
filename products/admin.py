from django.contrib import admin
from .models import Shop, Category, Product, ProductParameter


class ProductParameterInline(admin.TabularInline):
    model = ProductParameter
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop', 'category', 'price', 'quantity')
    list_filter = ('shop', 'category')
    search_fields = ('name',)
    inlines = [ProductParameterInline]


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )