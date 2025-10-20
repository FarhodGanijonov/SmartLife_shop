# E-Commerce Backend API (Django + DRF)

Bu loyiha — mahsulotlar, variantlar, aksessuarlar, savat, buyurtma va promokodlar bilan ishlovchi RESTful backend API. Django va Django REST Framework asosida qurilgan.

## Texnologiyalar

- Python 3.11
- Django 4.x
- Django REST Framework
- PostgreSQL
- Docker / Docker Compose
- Gunicorn

## Xususiyatlar

- Mahsulotlar, kategoriyalar, variantlar, aksessuarlar CRUD
- Savat logikasi (variant, bundle, accessory)
- Buyurtma yaratish va promokod qo‘llash
- Like tizimi
- Filter, qidiruv, sortirovka
- JWT yoki Session-based autentifikatsiya (moslashtiriladi)
- Docker bilan konteynerlashgan

## API endpointlar

### Kategoriyalar

- `GET /api/categories/` — barcha faol kategoriyalar
- `GET /api/categories/<slug>/` — bitta kategoriya va mahsulotlar

### Mahsulotlar

- `GET /api/products/` — mahsulotlar ro‘yxati (filter, qidiruv, sort)
- `GET /api/products/<slug>/` — mahsulot detail
- `POST /api/products/<slug>/like/` — like/unlike qilish
- `GET /api/products/<id>/similar/` — o‘xshash mahsulotlar

### Aksessuarlar

- `GET /api/accessories/?product_id=<id>` — mahsulotga mos aksessuarlar

### Savat

- `GET /api/cart_list/` — joriy savat
- `POST /api/cart_add/` — item qo‘shish
- `PATCH /api/cart_update_quantity/` — miqdorni o‘zgartirish
- `DELETE /api/cart_remove/` — itemni o‘chirish
- `DELETE /api/cart_clear/` — savatni tozalash

### Buyurtma

- `GET /api/orders-add-get/` — buyurtmalar ro‘yxati
- `POST /api/orders-add-get/` — yangi buyurtma yaratish

## Ishga tushirish (Docker)

```bash
# build va ishga tushirish
docker-compose build
docker-compose up

# birinchi marta: migratsiya va superuser
docker-compose run web python manage.py migrate
docker-compose run web python manage.py createsuperuser


.env fayli docker containerni ishga tushirish uchun 
    # Django settings
        DEBUG=1
        DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1
        
        # PostgreSQL settings
        DB_NAME=smart
        DB_USER=user_smart
        DB_PASSWORD=password_smart
        DB_HOST=smart_db
        DB_PORT=5432
