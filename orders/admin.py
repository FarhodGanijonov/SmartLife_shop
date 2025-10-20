from django.contrib import admin
from .models import Order, DeliveryOption, PromoCode





@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'delivery_option', 'payment_method')
    search_fields = ('user__username', 'product__title', 'phone', 'email')

@admin.register(DeliveryOption)
class DeliveryOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'delivery_time', 'cost', 'nationwide')
    list_filter = ('nationwide',)
    search_fields = ('name',)


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'amount', 'valid_until', 'is_active', 'used_count')
    list_filter = ('discount_type',)
    search_fields = ('code',)
    ordering = ('-valid_until',)
    readonly_fields = ('used_count',)

    fieldsets = (
        ('PromoCode maʼlumotlari', {
            'fields': ('code', 'discount_type', 'amount')
        }),
        ('Muddati va holati', {
            'fields': ('valid_until', 'used_count')
        }),
    )

    def is_active(self, obj):
        """Admin panelda promo aktivligini ko‘rsatish"""
        return obj.is_valid()
    is_active.boolean = True
    is_active.short_description = "Aktivmi?"

    def get_queryset(self, request):
        """Qo‘shimcha tartiblash"""
        qs = super().get_queryset(request)
        return qs.order_by('-valid_until')
