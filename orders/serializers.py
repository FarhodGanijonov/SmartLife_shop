
from .models import Order, DeliveryOption, CartItem, Cart, OrderItem
from rest_framework import serializers
from .models import PromoCode

class DeliveryOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryOption
        fields = ['id', 'name', 'delivery_time', 'cost', 'description']


class PromoCodeSerializer(serializers.ModelSerializer):
    """Promokodlar uchun serializer"""
    is_valid = serializers.SerializerMethodField()

    class Meta:
        model = PromoCode
        fields = [
            'id',
            'code',
            'discount_type',
            'amount',
            'min_order_amount',
            'usage_limit',
            'used_count',
            'valid_from',
            'valid_to',
            'is_active',
            'is_valid',
        ]
        read_only_fields = ['used_count', 'is_valid']

    def get_is_valid(self, obj):
        """Promokod amal qiladimi yoki yo‘qmi"""
        return obj.is_valid()

class OrderItemSerializer(serializers.ModelSerializer):
    variant_title = serializers.CharField(source="variant.title", read_only=True)
    variant_price = serializers.DecimalField(source="price", max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'variant', 'variant_title', 'variant_price', 'quantity', 'subtotal']

    def get_subtotal(self, obj):
        return obj.subtotal


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    total_items_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'delivery_option', 'address', 'city', 'phone',
            'email', 'contact_method', 'payment_method',
            'initial_payment', 'promo_code', 'total_price',
            'comment', 'items', 'total_items_price'
        ]

    def get_items(self, obj):
        return [
            {
                "id": item.id,
                "variant": item.variant.id,
                "variant_color": str(
                    item.variant.color.name if hasattr(item.variant.color, "name") else item.variant.color
                ),
                "variant_price": str(item.price),
                "quantity": item.quantity,
                "subtotal": float(item.subtotal),
            }
            for item in obj.items.all()
        ]

    def get_total_items_price(self, obj):
        return sum(item.subtotal for item in obj.items.all())

    def get_total_price(self, obj):
        total_items_price = sum(item.subtotal for item in obj.items.all())
        if obj.promo_code:
            promo = PromoCode.objects.filter(code=obj.promo_code).first()
            if promo and promo.is_valid():
                return promo.apply_discount(total_items_price)
        return total_items_price

    def create(self, validated_data):
        user = self.context['request'].user
        promo_code_str = validated_data.get('promo_code')
        validated_data.pop('user', None)

        cart = Cart.objects.filter(user=user).first()
        if not cart:
            raise serializers.ValidationError("Savat topilmadi.")

        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items.exists():
            raise serializers.ValidationError("Savat bo‘sh.")

        # Buyurtma yaratish
        order = Order.objects.create(user=user, **validated_data)

        # Har bir cart itemni order item sifatida yaratish
        total_items_price = 0
        for item in cart_items:
            subtotal = item.variant.price * item.quantity
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                price=item.variant.price,
                quantity=item.quantity,
                # subtotal=subtotal
            )
            total_items_price += subtotal

        # PromoCode qo‘llash
        final_total = total_items_price
        if promo_code_str:
            promo = PromoCode.objects.filter(code=promo_code_str).first()
            if promo and promo.is_valid():
                final_total = promo.apply_discount(total_items_price)
                promo.used_count += 1
                promo.save()
            else:
                raise serializers.ValidationError({
                    "promo_code": "Ushbu promo kod yaroqsiz yoki muddati tugagan."
                })

        # Yakuniy narxni saqlash
        order.total_price = final_total
        order.save()

        # Savatni tozalash
        cart_items.delete()

        return order

# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True, read_only=True) # CartItem qiymatini OrderItem da olib kelish
#     total_items_price = serializers.SerializerMethodField()  # jami items narxi
#
#     class Meta:
#         model = Order
#         fields = [
#             'id',
#             'delivery_option',
#             'address',
#             'city',
#             'phone',
#             'email',
#             'contact_method',
#             'payment_method',
#             'initial_payment',
#             'promo_code',
#             'total_price',
#             'comment',
#             'items',
#             'total_items_price',  # qo‘shdik
#         ]
#         read_only_fields = ('total_price',)
#
#     def get_total_items_price(self, obj):
#         """
#         Savatdagi barcha itemlarning narxini jamlaydi
#         subtotal = price * quantity
#         """
#         return sum(item.price * item.quantity for item in obj.items.all())
#
#     def create(self, validated_data):
#         request = self.context.get('request')
#         user = request.user if request and request.user.is_authenticated else None
#         validated_data.pop('user', None)
#
#         with transaction.atomic():
#             # Order yaratamiz
#             order = Order.objects.create(user=user, **validated_data)
#
#             # Foydalanuvchining savatini tekshiramiz
#             cart = Cart.objects.filter(user=user).first()
#             if not cart:
#                 raise serializers.ValidationError("Savat topilmadi.")
#
#             cart_items = CartItem.objects.filter(cart=cart)
#             if not cart_items.exists():
#                 raise serializers.ValidationError("Savat bo‘sh — buyurtma yaratilmaydi.")
#
#             total_quantity = sum(item.quantity for item in cart_items)
#             if total_quantity <= 0:
#                 raise serializers.ValidationError("Savatdagi mahsulotlar soni 0 bo‘lishi mumkin emas.")
#
#             # OrderItemlarni yaratamiz
#             total_price = 0
#             for item in cart_items:
#                 OrderItem.objects.create(
#                     order=order,
#                     variant=item.variant,
#                     quantity=item.quantity,
#                     price=item.variant.price
#                 )
#                 total_price += item.variant.price * item.quantity
#
#             # Promokodni hisoblash
#             promo_code_str = order.promo_code
#             if promo_code_str:
#                 try:
#                     promo = PromoCode.objects.get(code__iexact=promo_code_str)
#                     if promo.is_valid():
#                         total_price = promo.apply_discount(total_price)
#                         promo.used_count += 1
#                         promo.save(update_fields=['used_count'])
#                     else:
#                         raise serializers.ValidationError({
#                             "promo_code": "Bu promokod muddati tugagan yoki ishlatilgan."
#                         })
#                 except PromoCode.DoesNotExist:
#                     raise serializers.ValidationError({
#                         "promo_code": "Bunday promokod topilmadi."
#                     })
#
#             # Yakuniy narxni yozamiz
#             order.total_price = total_price
#             order.save(update_fields=['total_price'])
#
#             #  Savatni tozalaymiz
#             cart_items.delete()
#
#         return order


class CartItemSerializer(serializers.ModelSerializer):
    variant_title = serializers.CharField(source='variant.product.title', read_only=True)
    variant_price = serializers.DecimalField(source='variant.price', max_digits=10, decimal_places=2, read_only=True)
    variant_color = serializers.CharField(source='variant.color', read_only=True)
    variant_memory = serializers.CharField(source='variant.memory', read_only=True)
    subtotal = serializers.SerializerMethodField()
    bundle_id = serializers.IntegerField(source='bundle.id', read_only=True)
    bundle_name = serializers.CharField(source='bundle.name', read_only=True)
    bundle_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'variant', 'variant_title', 'variant_price', 'variant_color', 'variant_memory', 'quantity', 'bundle_id', 'bundle_name', 'bundle_price', 'subtotal']

    def get_subtotal(self, obj):
        return obj.subtotal

    def get_bundle_price(self, obj):
        if obj.bundle:
            return obj.bundle.total_price
        return None


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total']

    def get_total(self, obj):
        return obj.total_price()