import os
from django.core.signals import got_request_exception
from django.dispatch import receiver
from hawk_python_sdk import Hawk


hawk_client = Hawk(os.getenv('HAWK_API_KEY'))

@receiver(got_request_exception)
def send_to_hawk(sender, request, **kwargs):
    exc = kwargs.get('exception')
    if exc:
        hawk_client.capture_exception(exc)