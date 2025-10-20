from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Favorite
from .serializers import FavoriteSerializer


class FavoriteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Faqat autentifikatsiyadan o‘tgan foydalanuvchilar uchun

    def get(self, request):
        # Foydalanuvchining barcha like bosgan itemlarini ro‘yxat tarzida qaytaradi
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Mahsulot yoki aksessuarga yangi like qo‘shadi
        serializer = FavoriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Like foydalanuvchiga bog‘lanadi
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Mahsulot yoki aksessuarga bosilgan like’ni olib tashlaydi
        product_id = request.data.get("product")
        accessory_id = request.data.get("accessory")

        if product_id:
            Favorite.objects.filter(user=request.user, product_id=product_id).delete()
        elif accessory_id:
            Favorite.objects.filter(user=request.user, accessory_id=accessory_id).delete()
        else:
            return Response(
                {"error": "product yoki accessory ID kerak"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
