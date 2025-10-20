from django.db.models import Sum
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics

from products.models import ProductVariant, Bundle, Accessory
from .models import Order, PromoCode, CartItem
from .serializers import OrderSerializer, PromoCodeSerializer, CartItemSerializer, CartSerializer
from .utils import get_or_create_cart


class OrderGenericAPIView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = []  # login shart emas

    def get_queryset(self):
        # Buyurtmalarni tegishli bog‘lamalar bilan birga olish
        return Order.objects.all().select_related("delivery_option", "user").prefetch_related("items__variant")

    def get(self, request, *args, **kwargs):
        # Barcha buyurtmalarni ro‘yxat tarzida qaytaradi
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # Yangi buyurtma yaratish
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user if request.user.is_authenticated else None
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartDetailAPIView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Foydalanuvchining mavjud yoki yangi savatini qaytaradi
        return get_or_create_cart(self.request)


class CartAddAPIView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        variant_id = request.data.get("variant_id")
        bundle_id = request.data.get("bundle_id")
        accessory_id = request.data.get("accessory_id")
        quantity = int(request.data.get("quantity", 1))

        variant = ProductVariant.objects.filter(pk=variant_id).first() if variant_id else None
        bundle = Bundle.objects.filter(pk=bundle_id, product=variant.product).first() if bundle_id and variant else None
        accessory = Accessory.objects.filter(pk=accessory_id).first() if accessory_id else None

        if not variant and not accessory and not bundle:
            raise ValidationError("Hech qanday mahsulot tanlanmagan.")

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            bundle=bundle,
            accessory=accessory
        )
        item.quantity = item.quantity + quantity if not created else quantity
        item.save()

        serializer = self.get_serializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartUpdateQuantityAPIView(generics.UpdateAPIView):
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
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=request.data.get("item_id"), cart=cart)
        item.delete()
        return Response({"detail": "Item removed"}, status=status.HTTP_200_OK)


class CartClearAPIView(generics.DestroyAPIView):
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        return Response({"detail": "Cart cleared"}, status=status.HTTP_200_OK)
