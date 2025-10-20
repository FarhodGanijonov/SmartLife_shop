from rest_framework import serializers
from .models import Category, Product, ProductImage, MemoryOption, Color, ProductVariant, Accessory, Bundle


class CategorySerializer(serializers.ModelSerializer):
    sub_count = serializers.IntegerField(read_only=True)
    product_count = serializers.IntegerField(read_only=True)

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
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'price', 'old_price', 'discount_percent',
            'category', 'likes_count', 'is_featured', 'created_at', 'images'
        ]


class AccessorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Accessory
        fields = ['id', 'name', 'price', 'type', 'image']

class BundleSerializer(serializers.ModelSerializer):
    accessories = AccessorySerializer(many=True)
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



