from rest_framework import serializers
from .models import Favorite

class FavoriteSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "product", "product_title", "created_at"]
        read_only_fields = ["created_at"]
