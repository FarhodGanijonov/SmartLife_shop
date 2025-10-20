from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children'
    )
    icon = models.ImageField(upload_to='categories/icons/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def sub_count(self):
        """Faol sub-kategoriyalar soni"""
        return self.children.filter(is_active=True).count()


class Product(models.Model):
    """Mahsulotlar haqida asosiy ma’lumotlar"""

    # Asosiy ma’lumotlar
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="products"
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)

    # Narx va chegirma
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField(default=0)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Qo‘shimcha atributlar
    stock = models.PositiveIntegerField(default=0)


    # Tanlovli maydonlar (choices)
    AVAILABILITY_CHOICES = [
        ('in_stock', 'Есть в наличии'),
        ('out_of_stock', 'Нет в наличии'),
        ('pre_order', 'Предзаказ'),
    ]
    WARRANTY_CHOICES = [
        ('6', '6 месяцев'),
        ('12', '12 месяцев'),
        ('24', '24 месяца'),
        ('36', '36 месяцев'),
    ]
    DELIVERY_CHOICES = [
        ('free', 'Бесплатная доставка'),
        ('courier', 'Доставка курьером'),
        ('pickup', 'Самовывоз'),
    ]
    PICKUP_CHOICES = [
        ('available', 'Доступен в Ташкенте'),
        ('unavailable', 'Недоступен'),
    ]
    LIFESPAN_CHOICES = [
        ('1', '1 год'),
        ('3', '3 года'),
        ('5', '5 лет'),
        ('10', '10 лет'),
    ]
    MANUFACTURER_CHOICES = [
        ('apple', 'Apple'),
        ('samsung', 'Samsung'),
        ('xiaomi', 'Xiaomi'),
        ('huawei', 'Huawei'),
        ('other', 'Другой'),
    ]

    OS_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('windows', 'Windows'),
        ('other', 'Другая'),
    ]

    CONSTRUCTION_CHOICES = [
        ('foldable', 'Складной'),
        ('waterproof', 'Влагозащита'),
        ('standard', 'Обычный'),
    ]

    MATERIAL_CHOICES = [
        ('metal', 'Металл'),
        ('plastic', 'Пластик'),
        ('glass', 'Стекло'),
        ('ceramic', 'Керамика'),
    ]

    SIM_TYPE_CHOICES = [
        ('nano', 'Nano SIM'),
        ('micro', 'Micro SIM'),
        ('e-sim', 'eSIM'),
    ]

    SIM_COUNT_CHOICES = [
        (1, '1 SIM'),
        (2, '2 SIM'),
        (3, '3 SIM'),
    ]

    availability = models.CharField(
        max_length=50, choices=AVAILABILITY_CHOICES, default='in_stock'
    )
    warranty = models.CharField(
        max_length=50, choices=WARRANTY_CHOICES, default='12'
    )
    delivery = models.CharField(
        max_length=50, choices=DELIVERY_CHOICES, default='courier'
    )
    pickup = models.CharField(
        max_length=50, choices=PICKUP_CHOICES, default='available'
    )
    lifespan = models.CharField(
        max_length=50, choices=LIFESPAN_CHOICES, default='5'
    )
    manufacturer = models.CharField(
        max_length=50, choices=MANUFACTURER_CHOICES, default='apple'
    )


    operating_system = models.CharField(max_length=100, choices=OS_CHOICES, blank=True, null=True)
    construction = models.CharField(max_length=100, choices=CONSTRUCTION_CHOICES, blank=True, null=True)
    material = models.CharField(max_length=100, choices=MATERIAL_CHOICES, blank=True, null=True)
    sim_type = models.CharField(max_length=50, choices=SIM_TYPE_CHOICES, blank=True, null=True)
    sim_count = models.PositiveIntegerField(choices=SIM_COUNT_CHOICES, default=1)
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, help_text="grammda")
    dimensions = models.CharField(max_length=100, blank=True, null=True, help_text="Masalan: 146.7 x 71.5 x 7.4 mm")

    likes = models.ManyToManyField(User, related_name="liked_products", blank=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['price']),
            models.Index(fields=['is_available']),
        ]

    # Methodlar
    def save(self, *args, **kwargs):
        """Slug va chegirma logikasi"""
        if not self.slug:
            self.slug = slugify(self.title)

        if self.discount_percent > 0:
            if not self.old_price:
                self.old_price = self.price
            discounted_price = self.old_price - (self.old_price * self.discount_percent / 100)
            self.price = round(discounted_price, 2)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    # --- Propertylar ---
    @property
    def likes_count(self):
        """Mahsulotga berilgan like'lar soni"""
        return self.likes.count()

    @property
    def main_image(self):
        """Asosiy rasm URLini qaytaradi"""
        main = self.images.filter(is_main=True).first()
        return main.image.url if main else None

    @property
    def gallery(self):
        """Barcha rasm URLlari ro‘yxati"""
        return [img.image.url for img in self.images.all()]


class ProductImage(models.Model):
    """Mahsulot rasmlari (inline)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/images/')
    is_main = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_main']
        unique_together = ('product', 'image')

    def __str__(self):
        return f"{self.product.title} image"


class Color(models.Model):
    """Mahsulot rangi"""
    name = models.CharField(max_length=100, unique=True)
    hex_code = models.CharField(max_length=7, blank=True, null=True, help_text="Masalan: #FFFFFF")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class MemoryOption(models.Model):
    """Xotira hajmi varianti"""
    size = models.CharField(max_length=50, unique=True, help_text="Masalan: 64GB, 128GB, 256GB")

    class Meta:
        ordering = ['size']

    def __str__(self):
        return self.size


class ProductVariant(models.Model):
    """Mahsulotning rang + xotira kombinatsiyasi"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='variants')
    memory = models.ForeignKey(MemoryOption, on_delete=models.CASCADE, related_name='variants')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'color', 'memory')
        ordering = ['product', 'price']

    def __str__(self):
        return f"{self.product.title} - {self.memory.size} - {self.color.name}"


class Accessory(models.Model):
    TYPE_CHOICES = [
        ('glass', 'Protective Glass'),
        ('case', 'Case'),
        ('cable', 'Cable'),
    ]
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    image = models.ImageField(upload_to="accesuar_image", blank=True, null=True)

    def __str__(self):
        return self.name

class Bundle(models.Model):
    BUNDLE_CHOICES = [
        ('VIP', 'VIP'),
        ('Стандарт', 'Стандарт'),
        ('Мини', 'Мини'),
    ]

    name = models.CharField(max_length=100, choices=BUNDLE_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bundles')
    accessories = models.ManyToManyField(Accessory, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def total_price(self):
        accessories_total = sum([a.price for a in self.accessories.all()])
        total = self.product.price + accessories_total - self.discount
        return max(total, 0)  # narx manfiy bo‘lmasligi uchun

    def __str__(self):
        return f"{self.name} bundle for {self.product.title}"
