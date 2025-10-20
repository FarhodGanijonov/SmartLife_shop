from django.urls import path
from .views import FavoriteAPIView

urlpatterns = [
    # Mahsulot va aksessuarlarga like bosish, olib tashlash, va ro‘yxatini olish uchun endpoint
    path("product-like", FavoriteAPIView.as_view(), name="favorites"),
]
