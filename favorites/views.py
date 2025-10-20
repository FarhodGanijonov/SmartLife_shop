from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Favorite
from .serializers import FavoriteSerializer

class FavoriteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Foydalanuvchi yoqtirgan mahsulotlar ro‘yxati"""
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Yangi like qo‘shish"""
        serializer = FavoriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Like olib tashlash"""
        product_id = request.data.get("product")
        if not product_id:
            return Response({"error": "product ID required"}, status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.filter(user=request.user, product_id=product_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
