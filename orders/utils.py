# carts/utils.py
from .models import Cart

def get_or_create_cart(request):
    """Har bir foydalanuvchi uchun savatni olish yoki yaratish"""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart

