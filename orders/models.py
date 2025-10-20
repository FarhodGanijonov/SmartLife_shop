from django.utils import timezone
from django.db import models
from django.conf import settings
from products.models import ProductVariant, Bundle
from django.contrib.auth import get_user_model

User = get_user_model()

class DeliveryOption(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    delivery_time = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    nationwide = models.BooleanField(default=False)  # Haqiqiy yetkazish hududi
    priority = models.IntegerField(default=0)

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return f"{self.name} ({self.delivery_time})"


class PaymentMethod(models.TextChoices):
    CASH = 'cash', 'Naqt pul'
    CARD = 'card', 'Plastik/Online'
    INSTALLMENT = 'installment', 'Bolib to‘lash'


class ContactMethod(models.TextChoices):
    PHONE = 'phone', 'Telefon orqali'
    EMAIL = 'email', 'Email orqali'


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=[('percent', 'Foiz'), ('fixed', 'Summaga')])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_until = models.DateTimeField()
    used_count = models.PositiveIntegerField(default=0)

    def is_valid(self):
        return timezone.now() <= self.valid_until

    def apply_discount(self, total):
        if self.discount_type == 'percent':
            return float(total) * (1 - float(self.amount) / 100)
        return float(total) - float(self.amount)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="orders")
    # product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders")
    # quantity = models.PositiveIntegerField(default=1)
    delivery_option = models.ForeignKey(DeliveryOption, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    contact_method = models.CharField(max_length=10, choices=ContactMethod.choices, default=ContactMethod.PHONE)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    initial_payment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    promo_code = models.CharField(max_length=50, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        user_email = self.user.email if self.user else "Anonymous"
        return f"Order {self.id} - {user_email}"



    def calculate_total_price(self):
        """
           Order uchun total_price hisoblash.
           - Order hali saqlanmagan bo‘lsa (pk yo‘q), hisoblashni to‘xtatadi.
           - OrderItem lar asosida jami summani topadi.
           - Agar promo code mavjud bo‘lsa, chegirma qo‘llaydi.
        """
        # Order hali bazaga saqlanmagan bo‘lsa, 0 qaytar
        if not self.pk:
            return 0

        # OrderItem lar asosida jami narxni hisoblash
        total = sum(item.price * item.quantity for item in self.items.all())

        # Promokod bo‘lsa, chegirma qo‘llash
        if self.promo_code:
            promo = PromoCode.objects.filter(code__iexact=self.promo_code).first()
            if promo and promo.is_valid():
                total = promo.apply_discount(total)
                promo.used_count = models.F('used_count') + 1
                promo.save(update_fields=['used_count'])

        # Faqat hisoblab, qaytaramiz — SAQLAMAYMIZ!
        return round(total, 2)

    def save(self, *args, **kwargs):
        # Agar skip_calculation berilmagan bo‘lsa, avtomatik hisoblash
        if not kwargs.pop('skip_calculation', False):
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey("Order", related_name="items", on_delete=models.CASCADE)
    variant = models.ForeignKey("products.ProductVariant", on_delete=models.CASCADE)
    bundle = models.ForeignKey(Bundle, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # variant.price shu yerda saqlanadi
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        """Mahsulotning jami narxi (price * quantity)"""
        return round(self.price * self.quantity, 2)

    def __str__(self):
        return f"{self.variant} x {self.quantity}"

class Cart(models.Model):
    """Foydalanuvchining yoki sessiyaning savatchasi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="cart")
    session_key = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"{self.user.full_name} savatchasi"
        return f"Session {self.session_key} savatchasi"

    def total_price(self):
        """Savatdagi jami summa"""
        return sum([item.subtotal for item in self.items.all()])


class CartItem(models.Model):
    """Har bir mahsulotni savatchadagi yozuvi"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    bundle = models.ForeignKey(Bundle, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'variant', 'bundle')

    def __str__(self):
        return f"{self.variant} × {self.quantity} ({self.bundle.name if self.bundle else 'No bundle'})"

    @property
    def unit_price(self):
        return self.bundle.total_price if self.bundle else self.variant.price

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


# class OrderItem(models.Model):
#     order = models.ForeignKey(
#         Order, on_delete=models.CASCADE, related_name='items'
#     )
#     variant = models.ForeignKey(
#         ProductVariant, on_delete=models.PROTECT, related_name='order_items'
#     )
#     quantity = models.PositiveIntegerField(default=1)
#     price = models.DecimalField(max_digits=10, decimal_places=2)  # variant.price ni saqlaydi
#     subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # price * quantity
#
#     def __str__(self):
#         return f"{self.variant} x {self.quantity}"
#
#     class Meta:
#         verbose_name = "Order Item"
#         verbose_name_plural = "Order Items"