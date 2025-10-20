from django.urls import path
from .views import (
    OrderGenericAPIView,
    CartDetailAPIView,
    CartAddAPIView,
    CartUpdateQuantityAPIView,
    CartRemoveAPIView,
    CartClearAPIView,
)

urlpatterns = [
    # Buyurtma yaratish va buyurtmalar ro‘yxatini olish (GET/POST)
    path("orders-add-get/", OrderGenericAPIView.as_view(), name="orders"),

    # Foydalanuvchining savatini olish (GET)
    path('cart_list/', CartDetailAPIView.as_view(), name='cart-detail'),

    # Savatga mahsulot, bundle yoki aksessuar qo‘shish (POST)
    path('cart_add/', CartAddAPIView.as_view(), name='cart-add'),

    # Savatdagi item miqdorini o‘zgartirish (PATCH)
    path('cart_update_quantity/', CartUpdateQuantityAPIView.as_view(), name='cart-update'),

    # Savatdan bitta itemni o‘chirish (DELETE)
    path('cart_remove/', CartRemoveAPIView.as_view(), name='cart-remove'),

    # Savatni tozalash — barcha itemlarni o‘chirish (DELETE)
    path('cart_clear/', CartClearAPIView.as_view(), name='cart-clear'),
]
