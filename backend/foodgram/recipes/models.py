from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    """Модель Tag."""
    name = models.CharField(
        max_length=200,
        blank=False,
        unique=True,
        verbose_name='Название')
    color = models.CharField(
        max_length=7,
        blank=False,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Цвет должен быть HEX-кодом!'
            )
        ],
        unique=True,
        verbose_name='Цвет')
    slug = models.SlugField(
        max_length=200,
        blank=False,
        unique=True,
        verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель Ingredient."""
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель Recipe.
    Значения полей is_favorited и is_in_shopping_cart берется из
    соответствующих методов вьюсета для модели Recipe."""
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        related_name='tags',
        verbose_name='Тег'
    )
    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        through='IngredientAmount',
        related_name='ingredients',
        verbose_name='Ингредиент'
    )
    name = models.CharField(
        blank=False,
        max_length=200,
        db_index=True,
        verbose_name='Название'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        blank=False
    )
    text = models.TextField(
        blank=False,
        verbose_name='Описание'
    )
    cooking_time = models.PositiveIntegerField(
        blank=False,
        validators=[
            MinValueValidator(1,
                              message='Минимальное время 1 минута!')],
        verbose_name='Время приготовления (в минутах)'
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """Промежуточная модель IngredientAmount.
    Нужна для создания поля amount."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient,
        blank=False,
        related_name='ingredient',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент')
    amount = models.PositiveSmallIntegerField(blank=False)

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient')]

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Favorite(models.Model):
    """Модель Favorite."""
    user = models.ForeignKey(
        User,
        related_name='favorites',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'

    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.user}'


class Shopping(models.Model):
    """Модель Shopping."""
    user = models.ForeignKey(
        User,
        related_name='shoppings',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_shopping'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.user}'
