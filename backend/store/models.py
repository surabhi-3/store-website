from django.db import models
from django.contrib.auth.models import User

# Book Categories (Romantic, Fiction, Non-Fiction, Thriller, etc.)
from django.db import models

# ---- Category Model (Parent / Child) ----
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )

    def __str__(self):
        return self.name


# ---- Book Model ----
class Book(models.Model):
    LANG_CHOICES = [
        ('EN', 'English'),
        ('HI', 'Hindi'),
    ]

    SECTION_CHOICES = [
        ('KIDS', 'Kids'),
        ('ADULTS', 'Adults'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    stock = models.PositiveIntegerField(default=0)   # ✅ no. of copies available
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    language = models.CharField(max_length=10, choices=LANG_CHOICES, default='EN')
    section = models.CharField(max_length=10, choices=SECTION_CHOICES, default='ADULTS')
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title







# Orders (User, Books, Status)
class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    address = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


# Order Items (Many books per order)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"{self.book.title} x {self.quantity}"


from django.db import models
from django.contrib.auth.models import User
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey("Book", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.book.price * self.quantity

    def __str__(self):
        return f"{self.book.title} ({self.quantity})"