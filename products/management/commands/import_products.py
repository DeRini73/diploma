import yaml
from django.core.management.base import BaseCommand
from products.models import Shop, Category, Product, ProductParameter


class Command(BaseCommand):
    help = 'Импорт товаров из YAML-файла'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к YAML-файлу')

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        shop_name = data.get('shop')
        if not shop_name:
            self.stdout.write(self.style.ERROR('Не указано название магазина.'))
            return

        shop, _ = Shop.objects.get_or_create(name=shop_name)

        for cat_data in data.get('categories', []):
            Category.objects.get_or_create(
                external_id=cat_data['id'],
                defaults={'name': cat_data['name']}
            )

        for item in data.get('goods', []):
            category = Category.objects.get(external_id=item['category'])

            product, created = Product.objects.update_or_create(
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

            if not created:
                product.parameters.all().delete()

            for param_name, param_value in item.get('parameters', {}).items():
                ProductParameter.objects.create(
                    product=product,
                    name=param_name,
                    value=str(param_value)
                )

        self.stdout.write(self.style.SUCCESS(f'Импорт завершён. Магазин: {shop_name} обновлен'))