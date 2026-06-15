from celery import shared_task
from easy_thumbnails.files import generate_all_aliases
from .models import Product

@shared_task
def generate_thumbnails(product_id):
    try:
        product = Product.objects.get(id=product_id)
        if product.image:
            generate_all_aliases(product.image, include_global=True)
    except Product.DoesNotExist:
        pass