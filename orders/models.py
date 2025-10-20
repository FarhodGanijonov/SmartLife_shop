from django.utils import timezone
from django.db import models
from django.conf import settings
from products.models import ProductVariant, Bundle, Accessory
from django.contrib.auth import get_user_model

User = get_user_model()


# Yetkazib berish varianti (masalan: express, oddiy, viloyat bo‘yicha)
class DeliveryOption(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    delivery_time = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    nationwide = models.BooleanField(default=False)  # Butun mamlakat bo‘yicha yetkazish
    priority = models.IntegerField(default=0)  # Ko‘rsatish tartibi

    class Meta:
        ordering = ['priority']  # Admin va frontendda tartiblangan ko‘rinadi

    def __str__(self):
        return f"{self.name} ({self.delivery_time})"


# To‘lov usullari
class PaymentMethod(models.TextChoices):
    CASH = 'cash', 'Naqt pul'
    CARD = 'card', 'Plastik/Online'
    INSTALLMENT = 'installment', 'Bo‘lib to‘lash'


# Aloqa usullari
class ContactMethod(models.TextChoices):
    PHONE = 'phone', 'Telefon orqali'
    EMAIL = 'email', 'Email orqali'


# Promokod modeli
class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=[('percent', 'Foiz'), ('fixed', 'Summaga')])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_until = models.DateTimeField()
    used_count = models.PositiveIntegerField(default=0)

    def is_valid(self):
        # Promokod muddati tugamagan bo‘lsa, aktiv hisoblanadi
        return timezone.now() <= self.valid_until

    def apply_discount(self, total):
        # Chegirma turiga qarab narxni kamaytiradi
        if self.discount_type == 'percent':
            return float(total) * (1 - float(self.amount) / 100)
        return float(total) - float(self.amount)


# Buyurtma modeli
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="orders")
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
        Buyurtma uchun umumiy narxni hisoblaydi.
        - OrderItem lar asosida narx yig‘iladi
        - Promokod bo‘lsa, chegirma qo‘llanadi
        """
        if not self.pk:
            return 0

        total = sum(item.price * item.quantity for item in self.items.all())

        if self.promo_code:
            promo = PromoCode.objects.filter(code__iexact=self.promo_code).first()
            if promo and promo.is_valid():
                total = promo.apply_discount(total)
                promo.used_count = models.F('used_count') + 1
                promo.save(update_fields=['used_count'])

        return round(total, 2)

    def save(self, *args, **kwargs):
        # Saqlashdan oldin narxni hisoblaydi (agar skip_calculation berilmagan bo‘lsa)
        if not kwargs.pop('skip_calculation', False):
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)


# Buyurtmadagi har bir item (variant, aksessuar, yoki bundle)
class OrderItem(models.Model):
    order = models.ForeignKey("Order", related_name="items", on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    accessory = models.ForeignKey(Accessory, on_delete=models.SET_NULL, null=True, blank=True)
    bundle = models.ForeignKey(Bundle, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        # Item narxi × miqdor
        return round(self.price * self.quantity, 2)

    def __str__(self):
        if self.variant:
            return f"{self.variant} x {self.quantity}"
        elif self.accessory:
            return f"{self.accessory} x {self.quantity}"
        return f"Item x {self.quantity}"


# Savatcha modeli (foydalanuvchi yoki sessiya asosida)
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="cart")
    session_key = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"{self.user.full_name} savatchasi"
        return f"Session {self.session_key} savatchasi"

    def total_price(self):
        # Savatchadagi jami narx
        return sum([item.subtotal for item in self.items.all()])


# Savatchadagi har bir item
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    bundle = models.ForeignKey(Bundle, on_delete=models.SET_NULL, null=True, blank=True)
    accessory = models.ForeignKey(Accessory, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'variant', 'bundle')  # Har bir kombinatsiya savatchada bir marta bo‘ladi

    def __str__(self):
        return f"{self.variant} × {self.quantity} ({self.bundle.name if self.bundle else 'No bundle'})"

    @property
    def unit_price(self):
        # Narxni bundle, accessory yoki variantdan oladi
        if self.bundle:
            return self.bundle.total_price
        elif self.accessory:
            return self.accessory.price
        return self.variant.price

    @property
    def subtotal(self):
        # Narx × miqdor
        return round(self.unit_price * self.quantity, 2)
