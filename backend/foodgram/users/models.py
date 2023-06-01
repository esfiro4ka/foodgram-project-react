import re

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


def validate_username(value):
    pattern = r'^[\w.@+-]+$'
    regex_pattern = re.compile(pattern)
    if not regex_pattern.match(value):
        invalid_chars = []
        for char in value:
            if not regex_pattern.match(char):
                invalid_chars.append(char)
        raise ValidationError(
            f'Неправильные символы: {", ".join(invalid_chars)}')
    if value.lower() == "me":
        raise ValidationError(
            'Нельзя использовать "me" в качестве username!'
        )
    return value


class User(AbstractUser):
    """Модель User."""
    email = models.EmailField(
        unique=True,
        blank=False,
        max_length=254,
        verbose_name='Email'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        validators=[validate_username],
        verbose_name='Username'
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Фамилия'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return (self.username)


class Subscription(models.Model):
    """Модель Subscription."""
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='user_not_author'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.author}'
