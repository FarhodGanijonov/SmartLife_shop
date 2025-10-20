from django.contrib import admin
from .models import Favorite

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "accessory", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__full_name", "product__title", "accessory__title")
    ordering = ("-created_at",)
