from django.db.models import Sum
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics

from products.models import ProductVariant, Bundle
from .models import Order, PromoCode, CartItem
from .serializers import OrderSerializer, PromoCodeSerializer, CartItemSerializer, CartSerializer
from .utils import get_or_create_cart


class OrderGenericAPIView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = []  # login shart emas

    def get_queryset(self):
        """
        Anonymous foydalanuvchi uchun barcha buyurtmalar yoki
        frontend tarafdan filterlangan buyurtmalarni qaytarish.
        """
        return Order.objects.all().select_related("delivery_option", "user").prefetch_related("items__variant")
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # login qilmagan foydalanuvchi uchun user=None
        user = request.user if request.user.is_authenticated else None
        serializer.save(user=user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)



class ApplyPromoCodeAPIView(GenericAPIView):
    """Promokod qo‘llash API (GenericAPIView versiyasi)"""
    serializer_class = PromoCodeSerializer
    queryset = PromoCode.objects.all()

    def post(self, request, *args, **kwargs):
        code = request.data.get('code')
        total = request.data.get('total')
        variant_ids = request.data.get('variant_ids', [])

        #  Validatsiya
        if not code and not total and not variant_ids:
            return Response(
                {"error": "Promokod va summa yoki variantlar kiritilishi kerak."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Variantlar orqali jami summani topish
        if variant_ids:
            variants = ProductVariant.objects.filter(id__in=variant_ids)
            total_amount = variants.aggregate(total=Sum('price'))['total'] or 0
        else:
            total_amount = float(total)

        # Promokodni topish
        promo = self.get_queryset().filter(code__iexact=code).first()
        if not promo:
            return Response({"error": "Bunday promokod topilmadi"}, status=404)

        # Amal qilish muddati va ishlatilish holatini tekshirish
        if not promo.is_valid():
            return Response(
                {"error": "Promokod muddati tugagan yoki ishlatilgan."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Minimal summa shartini tekshirish
        if total_amount < promo.min_order_amount:
            return Response(
                {"error": f"Promokod faqat {promo.min_order_amount} so‘mdan yuqori buyurtmalarga amal qiladi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  Chegirma hisoblash
        new_total = promo.apply_discount(total_amount)

        #  Foydalanilgan promokodni hisoblash
        promo.used_count += 1
        promo.save(update_fields=['used_count'])

        #  Javob
        return Response({
            "code": promo.code,
            "discount_type": promo.discount_type,
            "old_total": total_amount,
            "new_total": new_total,
            "discount_applied": round(total_amount - new_total, 2),
        }, status=status.HTTP_200_OK)




class CartDetailAPIView(generics.RetrieveAPIView):
    """GET /api/cart/ — foydalanuvchining savatini olish"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_or_create_cart(self.request)


class CartAddAPIView(generics.CreateAPIView):
    """POST /api/cart/add/ — savatga mahsulot qo‘shish"""
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        variant_id = request.data.get("variant_id")
        bundle_id = request.data.get("bundle_id")  # optional
        quantity = int(request.data.get("quantity", 1))

        variant = get_object_or_404(ProductVariant, pk=variant_id)
        bundle = None
        if bundle_id:
            bundle = get_object_or_404(Bundle, pk=bundle_id, product=variant.product)

        item, created = CartItem.objects.get_or_create(cart=cart, variant=variant, bundle=bundle)
        item.quantity = item.quantity + quantity if not created else quantity
        item.save()

        serializer = self.get_serializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartUpdateQuantityAPIView(generics.UpdateAPIView):
    """PATCH /api/cart/update_quantity/ — miqdorni o‘zgartirish"""
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=request.data.get("item_id"), cart=cart)
        item.quantity = int(request.data.get("quantity", 1))
        item.save()
        serializer = self.get_serializer(item)
        return Response(serializer.data)


class CartRemoveAPIView(generics.DestroyAPIView):
    """POST /api/cart/remove/ — bitta elementni o‘chirish"""
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=request.data.get("item_id"), cart=cart)
        item.delete()
        return Response({"detail": "Item removed"}, status=status.HTTP_200_OK)


class CartClearAPIView(generics.DestroyAPIView):
    """DELETE /api/cart/clear/ — butun savatni tozalash"""
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        return Response({"detail": "Cart cleared"}, status=status.HTTP_200_OK)
