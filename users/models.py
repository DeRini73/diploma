from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email не указан!')
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('username', email)

        if not extra_fields.get('is_staff'):
            raise ValueError('Суперпользователь должен иметь признак "is_staff".')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Суперпользователь должен иметь признак "is_superuser".')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email')
    middle_name = models.CharField(max_length=50, blank=True, verbose_name='Отчество')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class Contact(models.Model):
    TYPE_CHOICES = [
        ('phone', 'Телефон'),
        ('address', 'Адрес'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    type = models.CharField(max_length=20,choices=TYPE_CHOICES,verbose_name='Контактные данные')
    value = models.CharField(max_length=200, verbose_name='Значение')

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return f'{self.get_type_display()}: {self.value}'
