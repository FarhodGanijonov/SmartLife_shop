from .models import Cart

def get_or_create_cart(request):
    """
    Foydalanuvchining savatini olish yoki yaratish:
    - Agar foydalanuvchi login bo‘lgan bo‘lsa, user asosida savat olinadi
    - Agar login bo‘lmagan bo‘lsa, session_key asosida savat olinadi
    """
    if request.user.is_authenticated:
        # Login foydalanuvchi uchun savatni user orqali olish yoki yaratish
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        # Session asosida savatni olish yoki yaratish
        session_key = request.session.session_key
        if not session_key:
            # Agar session mavjud bo‘lmasa, yangisini yaratamiz
            request.session.create()
            session_key = request.session.session_key

        cart, _ = Cart.objects.get_or_create(session_key=session_key)

    return cart
