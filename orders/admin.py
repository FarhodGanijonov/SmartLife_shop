from django.contrib import admin
from .models import Order, DeliveryOption, PromoCode


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Admin ro‘yxat sahifasida ko‘rinadigan ustunlar
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')

    # Filter paneli uchun ustunlar
    list_filter = ('status', 'delivery_option', 'payment_method')

    # Qidiruv maydonlari
    search_fields = ('user__username', 'product__title', 'phone', 'email')


@admin.register(DeliveryOption)
class DeliveryOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'delivery_time', 'cost', 'nationwide')
    list_filter = ('nationwide',)
    search_fields = ('name',)


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'discount_type', 'amount',
        'valid_until', 'is_active', 'used_count'
    )
    list_filter = ('discount_type',)
    search_fields = ('code',)
    ordering = ('-valid_until',)
    readonly_fields = ('used_count',)

    # Ma'lumotlarni guruhlab ko‘rsatish
    fieldsets = (
        ('PromoCode maʼlumotlari', {
            'fields': ('code', 'discount_type', 'amount')
        }),
        ('Muddati va holati', {
            'fields': ('valid_until', 'used_count')
        }),
    )

    def is_active(self, obj):
        # PromoCode aktivligini boolean ko‘rinishda ko‘rsatadi
        return obj.is_valid()
    is_active.boolean = True
    is_active.short_description = "Aktivmi?"

    def get_queryset(self, request):
        # Admin ro‘yxatini muddati bo‘yicha kamayish tartibida ko‘rsatadi
        qs = super().get_queryset(request)
        return qs.order_by('-valid_until')
