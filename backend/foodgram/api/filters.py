from django_filters import rest_framework

from recipes.models import Recipe, Tag
from users.models import User


class RecipesFilter(rest_framework.FilterSet):
    """Фильтрация по избранному, автору, списку покупок и тегам."""
    # запрос в виде http://localhost:8000/api/recipes/?is_favorited=1 :
    is_favorited = rest_framework.ChoiceFilter(
        choices=((1, '1'), (0, '0')),
        method='is_favorited_method'
    )
    # запрос в виде http://localhost:8000/api/recipes/?author=2 :
    author = rest_framework.ModelChoiceFilter(
        field_name='author',
        queryset=User.objects.all()
    )
    is_in_shopping_cart = rest_framework.ChoiceFilter(
        choices=((1, '1'), (0, '0')),
        method='is_in_shopping_cart_method'
    )
    # запрос в виде http://localhost:8000/api/recipes/?tags=red&yellow :
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    def is_favorited_method(self, queryset, name, value):
        user = self.request.user
        favorites = user.favorites.values_list('recipe', flat=True)
        print(favorites)
        favorite_queryset = queryset.filter(id__in=favorites)
        unfavorite_queryset = queryset.exclude(id__in=favorites)
        if value == '1':
            return favorite_queryset
        return unfavorite_queryset

    def is_in_shopping_cart_method(self, queryset, name, value):
        user = self.request.user
        shoppings = user.shoppings.values_list('recipe', flat=True)
        shopping_queryset = queryset.filter(id__in=shoppings)
        unshopping_queryset = queryset.exclude(id__in=shoppings)
        if value == '1':
            return shopping_queryset
        return unshopping_queryset

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'author', 'is_in_shopping_cart', 'tags']
