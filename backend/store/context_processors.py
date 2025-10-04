from .models import Category

def categories_processor(request):
    return {'categories': Category.objects.all()}
def cart_item_count(request):
    cart = request.session.get('cart', {})
    count = sum(item['quantity'] for item in cart.values())
    return {'cart_count': count}
