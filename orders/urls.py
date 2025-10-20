from django.urls import path
from .views import OrderGenericAPIView, ApplyPromoCodeAPIView, CartDetailAPIView, CartAddAPIView, \
    CartUpdateQuantityAPIView, CartRemoveAPIView, CartClearAPIView

urlpatterns = [
    path("orders-add-get", OrderGenericAPIView.as_view(), name="orders"),
    path("promo/apply/", ApplyPromoCodeAPIView.as_view(), name="apply-promo"),
    path('cart_list', CartDetailAPIView.as_view(), name='cart-detail'),
    path('cart_add/', CartAddAPIView.as_view(), name='cart-add'),
    path('cart_update_quantity/', CartUpdateQuantityAPIView.as_view(), name='cart-update'),
    path('cart_remove/', CartRemoveAPIView.as_view(), name='cart-remove'),
    path('cart_clear/', CartClearAPIView.as_view(), name='cart-clear'),
]
