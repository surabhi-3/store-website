from rest_framework import viewsets
from .models import Category, Book, Order,OrderItem
from .serializers import CategorySerializer, BookSerializer, OrderSerializer
from django.core.mail import send_mail


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer



from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q


def book_list(request):
    q = request.GET.get('q', '')
    section = request.GET.get('section', '').upper()
    books = Book.objects.all()
    if section in ('KIDS', 'ADULT'):
        books = books.filter(section=section)
    if q:
        books = books.filter(Q(title__icontains=q) | Q(author__icontains=q))
    cart = request.session.get('cart', {})
    cart_count = sum(item["quantity"] for item in cart.values())
    return render(request, 'book_list.html', {'books': books, 'cart_count': cart_count})


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Home page
def home(request):
    categories = Category.objects.filter(parent__isnull=True)  # only parent categories (Adults, Kids)
    books = Book.objects.all()[:5]  # first 5 books as "featured"

    # ✅ calculate cart count properly
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values()) if isinstance(cart, dict) else 0

    return render(
        request,
        "home.html",
        {
            "categories": categories,
            "books": books,
            "cart_count": cart_count,  # ✅ send to template
        }
    )


# Book detail
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'book_detail.html', {'book': book})

# Add to cart

def add_to_cart(request, book_id):
    cart = request.session.get("cart", {})
    book = get_object_or_404(Book, id=book_id)

    if str(book_id) not in cart:
        cart[str(book_id)] = {
            "title": book.title,   # ✅ add title
            "price": float(book.price),
            "quantity": 1,
            "total": float(book.price),
        }
    else:
        cart[str(book_id)]["quantity"] += 1
        cart[str(book_id)]["total"] = cart[str(book_id)]["quantity"] * cart[str(book_id)]["price"]

    request.session["cart"] = cart
    return redirect("cart")


# Cart view
def cart_view(request):
    cart = request.session.get('cart', {})
    grand_total = sum(item['total'] for item in cart.values())
    return render(request, 'cart.html', {'cart': cart, 'grand_total': grand_total})

# Register new user
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4



@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "my_orders.html", {"orders": orders})


@login_required
def download_invoice(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)

    # generate PDF using reportlab
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 100, f"Invoice for Order #{order.id}")

    p.setFont("Helvetica", 12)
    y = height - 150
    p.drawString(100, y, f"Customer: {order.user.username}")
    y -= 30
    p.drawString(100, y, f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}")

    y -= 50
    p.drawString(100, y, "Items:")
    y -= 30

    for item in order.items.all():
        p.drawString(120, y, f"{item.book.title} (x{item.quantity}) - ₹{item.price * item.quantity}")
        y -= 20

    y -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y, f"Total: ₹{order.total}")

    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
    return response


def search_books(request):
    query = request.GET.get('q', '')
    books = Book.objects.all()
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(description__icontains=query)
        )
    return render(request, 'search_results.html', {'books': books, 'query': query})


def books_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    books = Book.objects.filter(category=category)
    return render(request, 'books_by_category.html', {'category': category, 'books': books})


from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')

    if request.method == "POST":
        address = request.POST.get("address", "")
        total_price = sum(item['total'] for item in cart.values())

        # create order
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            status="CONFIRMED",   # ✅ confirm immediately
            is_paid=True   ,
            address=address        # ✅ simulate paid
        )

        # inside checkout function, after saving the order
        subject = f"Order Confirmation - #{order.id}"
        message = f"""
        Hi {request.user.username},

        Thank you for your order!

        Order ID: {order.id}
        Total: ₹{total_price}

        We will notify you once your order is shipped.

        - Online Bookstore Team
        """

        send_mail(
            subject,
            message,
            "your_email@gmail.com",       # FROM (must match EMAIL_HOST_USER)
            [request.user.email],         # TO (user’s email)
            fail_silently=False,
        )


        for book_id, item in cart.items():
            OrderItem.objects.create(
                order=order,
                book=Book.objects.get(id=book_id),  # ✅ fixed
                quantity=item['quantity'],
                price=item['price'],
            )

        request.session['cart'] = {}  # clear cart
        return render(request, "order_success.html", {"order": order})


    grand_total = sum(item['total'] for item in cart.values())
    return render(request, "checkout.html", {"cart": cart, "grand_total": grand_total})


from django.shortcuts import redirect, get_object_or_404
from .models import Book

from django.http import JsonResponse

def update_cart(request, book_id):
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        cart = request.session.get("cart", {})

        if str(book_id) in cart:
            cart[str(book_id)]["quantity"] = quantity
            cart[str(book_id)]["total"] = quantity * cart[str(book_id)]["price"]

        request.session["cart"] = cart

        # return JSON response
        item_total = cart[str(book_id)]["total"]
        grand_total = sum(item["total"] for item in cart.values())
        return JsonResponse({"item_total": item_total, "grand_total": grand_total})


def remove_from_cart(request, book_id):
    cart = request.session.get("cart", {})
    if str(book_id) in cart:
        del cart[str(book_id)]

    request.session["cart"] = cart
    grand_total = sum(item["total"] for item in cart.values())
    return JsonResponse({"grand_total": grand_total})



