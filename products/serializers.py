from rest_framework import serializers
from .models import (
    Category, Product, ProductImage, MemoryOption, Color,
    ProductVariant, AccessoryTarif, Bundle,
    Accessory, AccessoryImage
)


# Kategoriya serializer
class CategorySerializer(serializers.ModelSerializer):
    sub_count = serializers.IntegerField(read_only=True)  # Faol sub-kategoriyalar soni
    product_count = serializers.IntegerField(read_only=True)  # Kategoriyadagi mahsulotlar soni

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'sub_count', 'product_count']


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'hex_code']


class MemoryOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryOption
        fields = ['id', 'size']


class ProductVariantSerializer(serializers.ModelSerializer):
    color = ColorSerializer(read_only=True)
    memory = MemoryOptionSerializer(read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'color', 'memory', 'price', 'stock']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main']


class ProductSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField()  # faqat nomini ko‘rsatadi

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'price', 'old_price', 'discount_percent',
            'category', 'likes_count', 'is_featured', 'created_at', 'images'
        ]


class AccessoryTarifSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessoryTarif
        fields = ['id', 'name', 'price', 'type', 'image']


class BundleSerializer(serializers.ModelSerializer):
    accessories = AccessoryTarifSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Bundle
        fields = ['id', 'name', 'discount', 'total_price', 'accessories']

    def get_total_price(self, obj):
        return obj.total_price


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    bundles = BundleSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description',
            'price', 'old_price', 'discount_percent', 'category',
            'operating_system', 'construction', 'material',
            'sim_type', 'sim_count', 'weight', 'dimensions',
            'stock', 'is_available',
            'likes_count', 'images', 'variants', 'created_at',
            'availability', 'warranty', 'delivery', 'pickup', 'lifespan', 'manufacturer', 'bundles',
        ]


class AccessoryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessoryImage
        fields = ['id', 'image', 'alt_text']


class AccessorySerializer(serializers.ModelSerializer):
    compatible_products = serializers.StringRelatedField(many=True)  # Mahsulot nomlari
    images = AccessoryImageSerializer(many=True, read_only=True)

    class Meta:
        model = Accessory
        fields = ['id', 'title', 'price', 'description', 'compatible_products', 'images']
