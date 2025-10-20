from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductVariant, Color, MemoryOption, Accessory, Bundle


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'is_main', 'preview')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" style="border-radius:8px;" />', obj.image.url)
        return "-"
    preview.short_description = "Preview"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'sub_count', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ('order', 'is_active')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductVariantInline]

    list_display = (
        'title',
        'category',
        'price',
        'discount_percent',
        'likes_count_display',
        'is_featured',
        'is_available',
        'main_image_preview',
        'created_at',
    )
    list_filter = ('is_featured', 'is_available', 'category', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('likes_count_display', 'created_at', 'updated_at', 'main_image_preview')
    prepopulated_fields = {"slug": ("title",)}
    ordering = ('-created_at',)

    fieldsets = (
        ('Asosiy maʼlumotlar', {
            'fields': ('title', 'slug', 'category', 'description')
        }),
        ('Narx va chegirma', {
            'fields': ('price', 'discount_percent', 'old_price')
        }),
        ('Mahsulot holati', {
            'fields': (
                'availability',
                'warranty',
                'delivery',
                'pickup',
                'lifespan',
                'manufacturer'
            )
        }),
        ('О модели', {
            'fields': (
                'operating_system', 'construction', 'material',
                'sim_type', 'sim_count', 'weight', 'stock', 'dimensions'
            )
        }),
        ('Status', {
            'fields': ('is_available', 'is_featured')
        }),
        ('Statistika', {
            'fields': ('likes_count_display', 'created_at', 'updated_at', 'main_image_preview')
        }),
    )

    def likes_count_display(self, obj):
        return obj.likes.count()
    likes_count_display.short_description = "Likes"

    def main_image_preview(self, obj):
        """Mahsulotning asosiy rasm preview"""
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return format_html('<img src="{}" width="100" style="border-radius:10px;" />', main_image.image.url)
        return "-"
    main_image_preview.short_description = "Main Image"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('likes', 'images', 'category')

@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type', 'price']
    list_filter = ['type']
    search_fields = ['name']

@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'product', 'discount', 'get_total_price']
    list_filter = ['name']
    search_fields = ['name', 'product__name']
    filter_horizontal = ['accessories']

    def get_total_price(self, obj):
        return obj.total_price
    get_total_price.short_description = 'Total Price'


admin.site.register(Color)
admin.site.register(MemoryOption)