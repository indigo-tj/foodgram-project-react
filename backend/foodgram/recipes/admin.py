from django.contrib import admin

from .models import IngredientInRecipe, Ingredients, Recipe, Tags

admin.site.site_header = "Администрирование Foodgram"


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name', )
    search_fields = ('name', )


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'


class IngredientInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 3
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name', 'text', 'cooking_time',
        'image', 'author', 'pub_date'
    )
    list_editable = (
        'name', 'cooking_time',
        'image', 'author'
    )
    inlines = (IngredientInline,)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    @admin.display(description='В избранном')
    def in_favorites(self, obj):
        return obj.favorite_recipe.count()


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    list_editable = ('recipe', 'ingredient', 'amount')


admin.site.register(Ingredients, IngredientAdmin)
admin.site.register(Tags, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientInRecipe, RecipeIngredientAdmin)
