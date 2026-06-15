from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from .tasks import generate_thumbnails

@receiver(post_save, sender=Product)
def trigger_thumbnail_generation(sender, instance, created, **kwargs):
    if instance.image:
        generate_thumbnails.delay(instance.id)