from django.urls import path
from .views import FavoriteAPIView

urlpatterns = [
    path("product-like", FavoriteAPIView.as_view(), name="favorites"), # products ga like bosish va qaytarib olish va like bosilganlar listi
]
