from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_order_confirmation(order_id, user_email, contact_info,total_sum):
    subject = f'Заказ №{order_id} подтверждён.'
    message = (
        f'Ваш заказ №{order_id} принят.\n'
        f'Адрес доставки: {contact_info}.\n'
        f'Сумма заказа: {total_sum} рублей.\n'
        'Спасибо за заказ!'
    )

    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])

@shared_task
def send_order_to_admin(order_id, items_info, total_sum):
    subject = f'Новый заказ №{order_id}.'
    message = (
        f'Поступил заказ №{order_id}.\n'
        f'Товары:\n{items_info}\n'
        f'Сумма заказа: {total_sum} рублей.\n'
    )

    send_mail(subject, message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])