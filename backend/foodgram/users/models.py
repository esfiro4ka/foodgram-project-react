from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Модель User."""
    email = models.EmailField(
        unique=True,
        blank=False,
        max_length=254
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        validators=[
            RegexValidator(r'^[\w.@-]+$')
        ]
    )
    first_name = models.CharField(
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        max_length=150,
        blank=False
    )
    password = models.CharField(
        max_length=150,
        blank=False
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return (self.username)


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Подписка'
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
