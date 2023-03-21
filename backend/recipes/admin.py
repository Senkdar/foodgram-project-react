from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Ingredients,
    Favorites,
    RecipesIngredients,
    RecipesTags,
    ShoppingCart,
    Recipes,
    Tags,
)
from users.models import Follows, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'username',
        'first_name',
        'last_name',
        'password',
    )
    list_filter = ('email', 'username')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipesIngredients
    extra = 0


class RecipeTagsInline(admin.TabularInline):
    model = RecipesTags
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'in_favorite_count',)
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'author__email')
    inlines = [RecipeIngredientInline, RecipeTagsInline]

    def in_favorite_count(self, obj):
        return Favorites.objects.filter(recipe=obj).count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Recipes, RecipeAdmin)
admin.site.register(Tags)
admin.site.register(Ingredients, IngredientAdmin)
admin.site.register(Follows)
admin.site.register(ShoppingCart)
admin.site.register(Favorites)
