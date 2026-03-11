from django.shortcuts import get_object_or_404, render, redirect
from core.models import User
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.http import HttpResponse
from core.models import Product
from seller.models import Category, SubCategory
from django.contrib.auth.decorators import login_required
from .models import Address, Cart, CartItem, WishList, Reviews, Order, OrderItem
from .decorators import customer_required

from django.core.paginator import Paginator


def customer_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.role != 'customer':
                return render(request, 'customer/login.html',
                              {'error': "Seller cannot login here"})
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'customer/login.html',
                          {"error": "Invalid email or password"})

    return render(request, 'customer/login.html')

def customer_register(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            return render(request,'customer/register.html',
                          {"error":"Email already exists"})

        if len(password) < 6:
            return render(request,'customer/register.html',
                          {"error":"Password too short"})

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='customer'
        )
        login(request,user)
        return redirect('home')

    return render(request,'customer/register.html')

def home_view(request):
    all_products = Product.objects.filter(status = "approved")
    category = Category.objects.filter()

    paginator = Paginator(all_products, 15)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    for product in products:
        primary = product.productimage_set.filter(is_primary=True).first()
        if not primary:
            primary = product.productimage_set.first()

        product.primary_image = primary
        
    return render(request, 'customer/home.html', {"products":products, "categories":category})


def single_product_view(request, slug):
    product = Product.objects.get(slug=slug)
    is_in_wishlist = False
    reviews = Reviews.objects.filter(product=product).order_by('-created_at')
    if request.user.is_authenticated:
        is_in_wishlist = WishList.objects.filter(user=request.user, product=product).exists()
    return render(request, 'customer/single_product_view.html', {"product":product, "is_in_wishlist":is_in_wishlist, "reviews":reviews})

@customer_required
@login_required
def profile_page(request):
    return render(request, 'customer/profile.html')

def customer_logout(request):
    logout(request)
    return redirect('home')

@customer_required
@login_required
def update_profile(request):
    user = request.user
    if request.method == "POST":
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.save()
        return redirect("profile_page")    
    return render(request, 'customer/update_profile.html')

@customer_required
@login_required
def password_update(request):
    print(request.user.username)
    error = None
    user = request.user
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        retype_new_password = request.POST.get('retype_new_password')
        if not user.check_password(current_password):
            error = "current password is incorrect"
        elif new_password != retype_new_password:
            error = "retyped password not matching"
        elif len(new_password) < 8:
            error = "Password must be at least 8 characters"
        else:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            return redirect('profile_page')
    return render(request, 'customer/password_update.html',{"error":error})

@customer_required
@login_required
def view_addresses(request):
    user = request.user
    addresses = Address.objects.filter(user = user.id)
    return render(request, 'customer/view_addresses.html', {"addresses":addresses})

@customer_required
@login_required
def add_new_address(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        house_name = request.POST.get('house_name')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        user = request.user

        Address.objects.create(
            full_name = full_name,
            phone = phone,
            house_name = house_name,
            street = street,
            city = city,
            state = state,
            pincode = pincode,
            user = user
        )
        return redirect('view_addresses')
    return render(request, 'customer/add_new_address.html')

@customer_required
@login_required
def edit_address(request,id):
    address = get_object_or_404(Address, id=id, user=request.user)
    if request.method == 'POST':
        address.full_name = request.POST.get('full_name')
        address.phone = request.POST.get('phone')
        address.house_name = request.POST.get('house_name')
        address.street = request.POST.get('street')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.pincode = request.POST.get('pincode')
        address.save()
        return redirect('view_addresses')
    return render(request, 'customer/edit_address.html', {"address":address})

@customer_required
@login_required
def delete_address(request,id):
    address = get_object_or_404(Address, id=id, user=request.user)
    address.delete()
    return redirect('view_addresses')

@customer_required
@login_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    return render(request, 'customer/view_cart.html', {"cart":cart})

@customer_required
@login_required
def add_to_cart(request, id):
    user = request.user
    product = get_object_or_404(Product, id=id)
    
    cart, created = Cart.objects.get_or_create(
        user = user,
    )

    cart_item, item_created = CartItem.objects.get_or_create(
        cart = cart,
        product = product,
        defaults={
        'price': product.discount_price
    }
    )

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')

@customer_required
@login_required
def delete_cart_item(request, id):
    cart_item = CartItem.objects.get(id=id)
    cart_item.delete()
    return redirect('view_cart')

@customer_required
@login_required
def clear_all_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user).first()
    if cart:
        cart.cartitem_set.all().delete()
    return redirect('view_cart')

@customer_required
def increment_decrement_cartquantity(request, id, action):
    user = request.user
    cart_item = get_object_or_404(CartItem, id=id)
    if action == 'increment':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrement':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('view_cart')

@customer_required
@login_required
def view_wishlist(request):
    wishlist = WishList.objects.filter(user=request.user)
    return render(request, 'customer/view_wishlist.html', {"wishlist":wishlist})

@customer_required
@login_required
def toggle_wishlist(request, id):
    if request.method == 'POST':
        user = request.user
        product = get_object_or_404(Product, id=id)
        item = WishList.objects.filter(user=user, product=product)
        if item.exists():
            item.delete()
            return redirect('single_product', slug=product.slug)
        else:  
            WishList.objects.create(
                user=user,
                product=product
            )
            return redirect('single_product', slug=product.slug)
        
@customer_required
@login_required
def remove_from_wishlist(request, id):
    wishlist_item = get_object_or_404(WishList, id=id, user=request.user)    
    wishlist_item.delete()
    return redirect('view_wishlist')

@customer_required
@login_required
def add_to_cart_from_wishlist(request, id):
    user = request.user
    wishlist_item = get_object_or_404(WishList, id=id, user=user)
    product = wishlist_item.product

    cart, created = Cart.objects.get_or_create(user=user)

    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'price':product.discount_price})

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    wishlist_item.delete()
    return redirect('view_cart')

@customer_required
@login_required
def post_review(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug = slug)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        Reviews.objects.create(rating=rating, comment=comment, user=user, product=product)
        return redirect('single_product', slug=product.slug)
    
@customer_required
def checkout_page(request):
    user=request.user
    addresses = Address.objects.filter(user=user)

    cart = Cart.objects.filter(user=user).first()

    if not cart:
        return redirect('cart_page')

    cart_items = CartItem.objects.filter(cart=cart)

    return render(request, 'customer/checkout.html', {
        "addresses" : addresses,
        "cart" : cart,
        "cart_items" : cart_items
    })

def place_order(request):
    user = request.user

    address_id = request.POST.get('address')
    address = get_object_or_404(Address, id=address_id)

    cart = get_object_or_404(Cart, user=user)
    cart_items = CartItem.objects.filter(cart=cart)

    payment_method = request.POST.get('payment_mode')

    order = Order.objects.create(
        user = user,
        address = address,
        payment_method = payment_method,
    )

    for cart_item in cart_items:
        OrderItem.objects.create(
            order = order,
            product = cart_item.product,
            quantity = cart_item.quantity,
            price = cart_item.price
        )

    cart_items.delete()

    return redirect('order_success', id=order.id)
    
def view_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'customer/view_orders.html', {
        "orders" : orders
    })

def order_success(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)
    return render(request, 'customer/order_successfull.html', {'order': order})

def view_single_order(request, id):
    order = get_object_or_404(Order, id=id)
    return render(request, 'customer/view_single_order.html', {"order":order})

def category_filter(request, slug):
    category = get_object_or_404(Category, slug = slug)
    subcategories = SubCategory.objects.filter(category = category)
    all_products = Product.objects.filter(category=category)

    paginator = Paginator(all_products, 15)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    return render(request, 'customer/product_category_filter.html', {
        "products":products,
        "subcategories":subcategories,
        "category":category,
    })

def subcategory_filter(request, slug, sub_slug):
    category = get_object_or_404(Category, slug = slug)
    subcategory = get_object_or_404(SubCategory, category=category, slug = sub_slug)

    subcategories = SubCategory.objects.filter(category=category)
    all_products = Product.objects.filter(category=category, sub_category=subcategory)

    paginator = Paginator(all_products, 15)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)  

    return render(request, 'customer/product_category_filter.html', {
        "category":category,
        "subcategory":subcategory,
        "subcategories":subcategories,
        "products":products,
    })