from django.contrib import admin

from recipes.models import Ingredient, IngredientAmount, Recipe, RecipeTag, Tag


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeTagInline, RecipeIngredientInline,)
    list_display = ('name', 'author', 'favorite')
    list_filter = ('author', 'name', 'tags')

    def favorite(self, recipe):
        return recipe.favorite.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
