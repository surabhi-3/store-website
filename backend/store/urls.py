from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, BookViewSet, OrderViewSet,
    home, book_list, book_detail, cart_view, add_to_cart,
    register, my_orders, download_invoice,  update_cart, remove_from_cart,search_books, books_by_category,checkout
)

# API Router
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'books', BookViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),

    # Website pages
    path("", home, name="home"),
    path("books/", book_list, name="book_list"),  # 🔹 book list (with optional search/filter)
    path("book/<int:book_id>/", book_detail, name="book_detail"),
    path("cart/", cart_view, name="cart"),
    path("add-to-cart/<int:book_id>/", add_to_cart, name="add_to_cart"),
    path("register/", register, name="register"),
    path("my-orders/", my_orders, name="my_orders"),
    path("invoice/<int:order_id>/", download_invoice, name="download_invoice"),
    path("search/", search_books, name="search_books"),
    path("category/<int:category_id>/", books_by_category, name="books_by_category"),
    path("cart/", cart_view, name="cart"),
     path("cart/update/<int:book_id>/",update_cart, name="update_cart"),
    path("cart/remove/<int:book_id>/", remove_from_cart, name="remove_from_cart"),
    path("checkout/", checkout, name="checkout"),   # new line
    path("my-orders/", my_orders, name="my_orders"),
# ✅ new line


]
