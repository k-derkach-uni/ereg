import string
import random
from django.core.mail import send_mail
from django.conf import settings


def generate_password_and_notify(email):
    # генерируем случайный пароль длиной 8 символов из цифр и букв
    password = ''.join(random.choices(
        string.ascii_letters + string.digits, k=10))

    # отправляем письмо на указанный email со сгенерированным паролем
    send_mail(
        'Новый пароль',
        f'Ваш новый пароль: {password}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

    return password
