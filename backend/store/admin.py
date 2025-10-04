from django.contrib import admin
from .models import Category, Book, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'category')   # ✅ only real fields
    list_filter = ('category',)                               # ✅ filter only by existing field
    search_fields = ('title', 'author')                       # ✅ search by title & author

admin.site.register(Book, BookAdmin)



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    inlines = [OrderItemInline]
