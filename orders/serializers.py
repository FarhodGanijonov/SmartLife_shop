
from .models import Order, DeliveryOption, CartItem, Cart, OrderItem
from rest_framework import serializers
from .models import PromoCode

class DeliveryOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryOption
        fields = ['id', 'name', 'delivery_time', 'cost', 'description']


class PromoCodeSerializer(serializers.ModelSerializer):
    is_valid = serializers.SerializerMethodField()  # Promokod amal qiladimi yoki yo‘qmi

    class Meta:
        model = PromoCode
        fields = [
            'id', 'code', 'discount_type', 'amount',
            'min_order_amount', 'usage_limit', 'used_count',
            'valid_from', 'valid_to', 'is_active', 'is_valid'
        ]
        read_only_fields = ['used_count', 'is_valid']

    def get_is_valid(self, obj):
        return obj.is_valid()

class OrderItemSerializer(serializers.ModelSerializer):
    variant_title = serializers.CharField(source="variant.product.title", read_only=True)
    variant_price = serializers.DecimalField(source="price", max_digits=10, decimal_places=2, read_only=True)
    bundle_id = serializers.IntegerField(source="bundle.id", read_only=True)
    bundle_name = serializers.CharField(source="bundle.name", read_only=True)
    bundle_price = serializers.SerializerMethodField()
    accessory_title = serializers.CharField(source='accessory.title', read_only=True, default=None)
    accessory_price = serializers.DecimalField(source='accessory.price', max_digits=10, decimal_places=2, read_only=True, default=None)
    subtotal = serializers.SerializerMethodField()  # Narx × miqdor

    class Meta:
        model = OrderItem
        fields = [
            'id', 'variant', 'variant_title', 'variant_price', 'quantity',
            'bundle_id', 'bundle_name', 'bundle_price',
            'accessory', 'accessory_title', 'accessory_price',
            'subtotal'
        ]

    def get_subtotal(self, obj):
        return obj.subtotal

    def get_bundle_price(self, obj):
        return obj.bundle.total_price if obj.bundle else None

class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()  # Buyurtmadagi itemlar ro‘yxati
    total_items_price = serializers.SerializerMethodField()  # Promokodsiz narx
    total_price = serializers.SerializerMethodField()  # Promokod qo‘llangandan keyingi narx

    class Meta:
        model = Order
        fields = [
            'id', 'delivery_option', 'address', 'city', 'phone',
            'email', 'contact_method', 'payment_method',
            'initial_payment', 'promo_code', 'total_price',
            'comment', 'items', 'total_items_price'
        ]

    def get_items(self, obj):
        return OrderItemSerializer(obj.items.all(), many=True).data

    def get_total_items_price(self, obj):
        return sum(item.subtotal for item in obj.items.all())

    def get_total_price(self, obj):
        total_items_price = self.get_total_items_price(obj)
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

        order = Order.objects.create(user=user, **validated_data)

        total_items_price = 0
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                bundle=item.bundle,
                accessory=item.accessory,
                price=item.unit_price,
                quantity=item.quantity,
            )
            total_items_price += item.subtotal

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

        order.total_price = final_total
        order.save()
        cart_items.delete()

        return order


class CartItemSerializer(serializers.ModelSerializer):
    variant_title = serializers.CharField(source='variant.product.title', read_only=True)
    variant_price = serializers.DecimalField(source='variant.price', max_digits=10, decimal_places=2, read_only=True)
    variant_color = serializers.CharField(source='variant.color', read_only=True)
    variant_memory = serializers.CharField(source='variant.memory', read_only=True)
    subtotal = serializers.SerializerMethodField()
    bundle_id = serializers.IntegerField(source='bundle.id', read_only=True)
    bundle_name = serializers.CharField(source='bundle.name', read_only=True)
    bundle_price = serializers.SerializerMethodField()
    accessory_title = serializers.CharField(source='accessory.title', read_only=True)
    accessory_price = serializers.DecimalField(source='accessory.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'variant', 'variant_title', 'variant_price',
            'variant_color', 'variant_memory', 'quantity',
            'bundle_id', 'bundle_name', 'bundle_price',
            'accessory', 'accessory_title', 'accessory_price',
            'subtotal'
        ]

    def get_subtotal(self, obj):
        return obj.subtotal

    def get_bundle_price(self, obj):
        return obj.bundle.total_price if obj.bundle else None


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()  # Savatdagi jami narx

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total']

    def get_total(self, obj):
        return obj.total_price()
