from collections import defaultdict

from api.filters import IngredientsFilter, RecipesFilter
from api.pagination import CustomPageNumberPagination
from api.permissions import IsAuthorOrAdmin
from api.serializers import (FavoriteShoppingSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeWriteSerializer,
                             SubscriptionSerializer, TagSerializer)
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Favorite, Ingredient, Recipe, Shopping, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription, User


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Ingredient.
    Реализован поиск по частичному вхождению в начале названия ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientsFilter,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipe.
    Реализована фильтрация по избранному, автору, списку покупок и тегам.
    Доступны пользовательские действия по добавлению рецепта в избранное
    и удалению, добавлению рецепта в список покупок и удалению, скачиванию
    списка покупок в файл shopping_cart.txt."""
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    permission_classes = (IsAuthorOrAdmin,)
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
            methods=('post', 'delete'),
            detail=True,
            permission_classes=(IsAuthenticated,),
            )
    def favorite(self, request, pk):
        return self.add_or_delete_object(Favorite,
                                         request,
                                         pk)

    @action(
            methods=('post', 'delete'),
            detail=True,
            permission_classes=(IsAuthenticated,),
            )
    def shopping_cart(self, request, pk):
        return self.add_or_delete_object(Shopping,
                                         request,
                                         pk)

    def add_or_delete_object(self, model, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if self.request.method == 'POST':
            if model.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                return Response({'errors': 'Object already exists'},
                                status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(user=user, recipe=recipe)
            serializer = FavoriteShoppingSerializer(
                recipe, context={'request': request},)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            if not model.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Object not found or already deleted'},
                    status=status.HTTP_400_BAD_REQUEST)
            data = get_object_or_404(model, user=user, recipe=recipe)
            data.delete()
            return Response({'messages': 'Object deleted'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Unauthorized'},
            status=status.HTTP_401_UNAUTHORIZED)

    @action(
            methods=('get',),
            detail=False,
            permission_classes=(IsAuthorOrAdmin,),
            )
    def download_shopping_cart(self, request):
        shopping_cart = Shopping.objects.filter(user=self.request.user)
        lines = []
        goods = defaultdict(lambda: 0)
        for item in shopping_cart:
            for ingredientamount in item.recipe.ingredientamount_set.all():
                goods[
                    (ingredientamount.ingredient.name,
                     ingredientamount.ingredient.measurement_unit)
                     ] += ingredientamount.amount
        for (name, measurement_unit), amount in goods.items():
            line = (f'{name}, '
                    f'{amount} '
                    f'{measurement_unit.lower()}')
            lines.append(line)
        filename = 'shopping_cart.txt'
        with open(filename, 'w') as file:
            file.write('\n'.join(lines))
        return FileResponse(
            open(filename, 'rb'), as_attachment=True, filename=filename)


class UserViewSet(UserViewSet):
    """Вьюсет для модели User.
    Доступны пользовательские действия по добавлению подписки на автора
    и удалению, а также просмотра страницы подписок с рецептами авторов.
    Остальные методы (получение информации о текущем пользователе,
    сброс пароля и т.д.) определены в Djoser."""
    queryset = User.objects.all()
    lookup_field = 'id'
    pagination_class = CustomPageNumberPagination

    @action(
            methods=('post', 'delete'),
            detail=True,
            permission_classes=(IsAuthenticated,),
            )
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, pk=id)
        if self.request.method == 'POST':
            if user.id == author.id:
                return Response(
                    {'errors': 'You cannot subscribe to yourself'},
                    status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                return Response({'errors': 'Object already exists'},
                                status=status.HTTP_400_BAD_REQUEST)
            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(
                author, context={'request': request},)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            if not Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                return Response(
                    {'errors': 'Object not found or already deleted'},
                    status=status.HTTP_400_BAD_REQUEST)
            subscription = get_object_or_404(
                Subscription, user=user, author=author)
            subscription.delete()
            return Response({'messages': 'Object deleted'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Unauthorized'},
            status=status.HTTP_401_UNAUTHORIZED)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthorOrAdmin,),
    )
    def subscriptions(self, request):
        user = self.request.user
        user_subscriptions = user.follower.values_list('author_id', flat=True)
        queryset = User.objects.filter(id__in=user_subscriptions)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            paginated_queryset, many=True, context={'request': request},)
        return self.get_paginated_response(serializer.data)
