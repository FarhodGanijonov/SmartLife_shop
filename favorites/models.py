from django.db import models
from django.conf import settings
from products.models import Product, Accessory


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="favorites",
        null=True,
        blank=True
    )
    accessory = models.ForeignKey(
        Accessory,
        on_delete=models.CASCADE,
        related_name="favorites",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_favorite"
            ),
            models.UniqueConstraint(
                fields=["user", "accessory"],
                name="unique_user_accessory_favorite"
            ),
        ]

    def __str__(self):
        if self.product:
            return f"{self.user.full_name} → {self.product.title}"
        if self.accessory:
            return f"{self.user.full_name} → {self.accessory.title}"
        return f"{self.user.full_name} → Favorite"
