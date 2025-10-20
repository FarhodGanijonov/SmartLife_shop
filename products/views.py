from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from .models import Category, Product, Accessory
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductDetailSerializer, AccessoryTarifSerializer, AccessorySerializer,
)
from rest_framework.pagination import PageNumberPagination


#  Custom pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12  # Default page size
    page_size_query_param = "page_size"  # Frontenddan o‘zgartirish mumkin
    max_page_size = 100  # Limit



class CategoryListAPIView(generics.ListAPIView):
    """
    Barcha faol kategoriyalarni chiqaradi.
    Har bir categoryda nechta subcategory borligi va product soni ham chiqadi.
    """
    queryset = Category.objects.filter(is_active=True).annotate(product_count=Count("products"))
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None  # To‘liq ro‘yxat

class CategoryDetailAPIView(APIView):
    """
    Category slug orqali chiqadi (subcategories va products bilan birga)
    """
    permission_classes = [AllowAny]

    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug, is_active=True)
        products = category.products.filter(is_available=True)
        serializer = CategorySerializer(category, context={"request": request})
        product_serializer = ProductSerializer(products, many=True, context={"request": request})
        return Response({
            "category": serializer.data,
            "products": product_serializer.data
        })



class ProductListAPIView(generics.ListAPIView):
    """
    Barcha productlar — filter, qidiruv, sortirovka bilan.
    """
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True).select_related('category').prefetch_related('images', 'likes')

        category_slug = self.request.query_params.get("category")
        search = self.request.query_params.get("search")
        ordering = self.request.query_params.get("ordering")  # price, -price, created_at, -likes

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(short_description__icontains=search))

        if ordering:
            if ordering == "likes":
                queryset = queryset.annotate(likes_count=Count("likes")).order_by("-likes_count")
            else:
                queryset = queryset.order_by(ordering)

        return queryset

class ProductDetailAPIView(APIView):
    """
    Mahsulotni slug orqali olish (rasmlar, like soni bilan)
    """
    permission_classes = [AllowAny]

    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug, is_available=True)
        serializer = ProductDetailSerializer(product, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductLikeAPIView(APIView):
    """
    Like / Unlike qilish uchun API
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        user = request.user

        if product.likes.filter(id=user.id).exists():
            product.likes.remove(user)
            liked = False
        else:
            product.likes.add(user)
            liked = True

        return Response({
            "liked": liked,
            "likes_count": product.likes.count()
        }, status=status.HTTP_200_OK)



class AccessoryListAPIView(generics.ListAPIView):
    """
    Mahsulotga mos aksessuarlar ro‘yxati
    """
    serializer_class = AccessorySerializer

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return Accessory.objects.filter(compatible_products__id=product_id, is_active=True)
        return Accessory.objects.none()


class SimilarProductAPIView(APIView):
    """
    Mahsulotga o‘xshash boshqa mahsulotlar (kategoriya bo‘yicha)
    """
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Mahsulot topilmadi"}, status=404)

        similar_products = Product.objects.filter(category=product.category).exclude(id=product.id)
        serializer = ProductSerializer(similar_products, many=True, context={"request": request})
        return Response(serializer.data)
