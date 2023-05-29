from django_filters.rest_framework import (ChoiceFilter, FilterSet,
                                           ModelChoiceFilter,
                                           ModelMultipleChoiceFilter)

from recipes.models import Recipe, Tag
from users.models import User


class RecipesFilter(FilterSet):
    """Фильтрация по избранному, автору, списку покупок и тегам."""
    is_favorited = ChoiceFilter(
        choices=((1, '1'), (0, '0')),
        method='is_favorited_method'
    )
    author = ModelChoiceFilter(
        field_name='author',
        queryset=User.objects.all()
    )
    is_in_shopping_cart = ChoiceFilter(
        choices=((1, '1'), (0, '0')),
        method='is_in_shopping_cart_method'
    )
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    def is_favorited_method(self, queryset, name, value):
        return self.filter(queryset, value, self.request.user.favorites)

    def is_in_shopping_cart_method(self, queryset, name, value):
        return self.filter(queryset, value, self.request.user.shoppings)

    def filter(self, queryset, value, collection):
        data = collection.values_list('recipe', flat=True)
        filtered_queryset = queryset.filter(id__in=data)
        excluded_queryset = queryset.exclude(id__in=data)
        if value == '1':
            return filtered_queryset
        return excluded_queryset

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'author', 'is_in_shopping_cart', 'tags']
