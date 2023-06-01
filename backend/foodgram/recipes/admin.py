from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from recipes.models import Favorite, Ingredient, Recipe, Shopping, Tag


class RecipeIngredientInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total = 0
        deleted = 0
        for form in self.forms:
            if not form.cleaned_data:
                raise ValidationError('Поле не может быть пустым.')
            total += 1
            if form.cleaned_data['DELETE']:
                deleted += 1
        if deleted == total:
            raise ValidationError('Поле не может быть пустым.')


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    formset = RecipeIngredientInlineFormSet
    extra = 0
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
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
admin.site.register(Favorite)
admin.site.register(Shopping)
