from django.contrib import admin
from .models import Ingredients, User, Recipes, Tags, Follows


admin.site.register(Recipes)
admin.site.register(Tags)
admin.site.register(User)
admin.site.register(Ingredients)
admin.site.register(Follows)
