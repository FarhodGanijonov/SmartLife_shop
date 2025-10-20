from rest_framework import serializers
from .models import Favorite

class FavoriteSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)
    accessory_title = serializers.CharField(source="accessory.title", read_only=True)

    class Meta:
        model = Favorite  # Modelga bog‘langan serializer
        fields = [
            "id",
            "product",          # Mahsulot ID (kiruvchi so‘rovda)
            "accessory",        # Aksessuar ID (kiruvchi so‘rovda)
            "product_title",    # Mahsulot nomi (chiqishda ko‘rinadi)
            "accessory_title",  # Aksessuar nomi (chiqishda ko‘rinadi)
            "created_at"
        ]
        read_only_fields = ["created_at"]  # Like vaqti avtomatik saqlanadi, o‘zgartirib bo‘lmaydi
