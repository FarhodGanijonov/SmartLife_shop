from django.urls import path
from .views import (
    CategoryListAPIView,
    CategoryDetailAPIView,
    ProductListAPIView,
    ProductDetailAPIView,
    ProductLikeAPIView,
    AccessoryListAPIView,
    SimilarProductAPIView,
)

urlpatterns = [
    # Kategoriyalar ro‘yxati (faol bo‘lganlar)
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),

    # Bitta kategoriya va unga tegishli mahsulotlar
    path('categories/<slug:slug>/', CategoryDetailAPIView.as_view(), name='category-detail'),

    # Mahsulotlar ro‘yxati (filter, qidiruv, sortirovka bilan)
    path('products/', ProductListAPIView.as_view(), name='product-list'),

    # Mahsulot detail sahifasi (slug orqali)
    path('products/<slug:slug>/', ProductDetailAPIView.as_view(), name='product-detail'),

    # Like / Unlike qilish
    path('products/<slug:slug>/like/', ProductLikeAPIView.as_view(), name='product-like'),

    # Mahsulotga mos aksessuarlar
    path('accessories/', AccessoryListAPIView.as_view(), name='accessory-list'),

    # O‘xshash mahsulotlar (kategoriya bo‘yicha)
    path("products/<int:product_id>/similar/", SimilarProductAPIView.as_view(), name="similar-products"),
]
