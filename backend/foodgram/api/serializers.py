from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from users.models import User


class UserReadSerializer(UserSerializer):
    """Сериализатор модели User для чтения объектов."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'email', 'id', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, author):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=author).exists()


class UserWriteSerializer(UserCreateSerializer):
    """Сериализатор модели User для записи объектов."""
    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'password')
        model = User


class SubscriptionSerializer(UserReadSerializer):
    """Сериализатор модели User.
    Используется при добавлении подписок и просмотре страницы подписок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, author):
        recipes = Recipe.objects.filter(author=author)
        if recipes:
            serializer = FavoriteShoppingSerializer(
                recipes,
                context={'request': self.context.get('request')},
                many=True
            )
            return serializer.data
        return Recipe.objects.none()

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag."""
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient."""
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class IngredientRecipeReadSerialiser(serializers.ModelSerializer):
    """Сериализатор промежуточной модели IngredientAmount,
    используемый при чтении рецептов. Значения id, name и
    measurement_unit берутся с помощью related name
    промежуточной модели IngredientAmount."""
    id = serializers.IntegerField(
        source='ingredient.id',
        read_only=True)
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient, используемый при записи рецептов.
    id, автоматически генерируемый джанго, имеет параметр read_only, поэтому
    поле явно указано в сериализаторе."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe, используемый при чтении рецептов.
    Для вычисления значения ingredients происходит обращение к данным
    промежуточной модели."""
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientRecipeReadSerialiser(
        read_only=True,
        many=True,
        source='ingredientamount_set')
    author = UserReadSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        model = Recipe

    def get_is_favorited(self, recipe):
        return self.get_parameter_value(recipe, 'favorites')

    def get_is_in_shopping_cart(self, recipe):
        return self.get_parameter_value(recipe, 'shoppings')

    def get_parameter_value(self, recipe, collection_name):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return getattr(user, collection_name).filter(recipe=recipe).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe, используемый при записи объектов."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientRecipeWriteSerializer(
        many=True)
    author = UserReadSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')
        model = Recipe

    def create_ingredient_amount(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredient_amount(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe.ingredients.clear()
        tags = validated_data.pop('tags')
        recipe.tags.clear()
        self.create_ingredient_amount(ingredients, recipe)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        representation = RecipeReadSerializer(
            recipe, context={'request': self.context.get('request')})
        return representation.data


class FavoriteShoppingSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe для записи объектов.
    Используется при добавлении рецептов в избранное или список покупок."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
