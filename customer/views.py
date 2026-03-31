from django.shortcuts import get_object_or_404, render, redirect
from core.models import User
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.http import HttpResponse
from core.models import Product
from seller.models import Category, SubCategory
from django.contrib.auth.decorators import login_required
from .models import Address, Cart, CartItem, WishList, Reviews, Order, OrderItem
from .decorators import customer_required
from django.http import JsonResponse

from django.contrib import messages

from django.core.paginator import Paginator

import pyotp
from django.core.mail import send_mail
from django.conf import settings

import razorpay
from django.db import transaction

from django.db.models import Avg, Count

import random

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
        action = request.POST.get("action")

        if action == "send_otp":
            email = request.POST.get('email')
            if not email:
                return JsonResponse({"status": "error", "message": "Email is required"}, status=400)
            
            secret = pyotp.random_base32()
            request.session['otp_secret'] = secret
            request.session['email'] = email
            request.session['otp_sent'] = True

            totp = pyotp.TOTP(secret)
            otp = totp.now()

            try:
                send_mail("Email verification", f"Your OTP is {otp}","blackasta0999@gmail.com", [email], fail_silently=False)
                return JsonResponse({"status": "success", "message": "OTP sent successfully!"})
            except Exception as e:
                return JsonResponse({"status": "error", "message": "Failed to send email."}, status=500)
        
        if action == "register":

            otp = request.POST.get('otp')
            secret = request.session.get("otp_secret")

            if not secret:
                return render(request, 'customer/register.html', {"error":"Send OTP first"})
            
            totp = pyotp.TOTP(secret)

            if not totp.verify(otp, valid_window=10):
                return render(request,'customer/register.html', {"error":"Invalid or expired OTP"})
            
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.session.get("email")
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

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
        
    return render(request,'customer/register.html')

def home_view(request):
    
    all_products = Product.objects.filter(status = "approved") \
        .select_related('category') \
        .prefetch_related('productimage_set') \
        .annotate(
            avg_rating = Avg('reviews__rating'),
            number_of_reviews = Count('reviews')
        ) \
        .order_by("-created_at")
    
    category = Category.objects.all()

    paginator = Paginator(all_products, 15)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    is_authenticated = request.user.is_authenticated

    trending_products = Product.objects.all()
    trending_products = list(trending_products)
    random.shuffle(trending_products)
    trending_products = trending_products[:3    ]

    if is_authenticated:
        wishlist_products = set(WishList.objects.filter(user=request.user).values_list('product_id', flat=True))
    else:
        wishlist_products = set()

    for product in products:
        primary = next(
            (img for img in product.productimage_set.all() if img.is_primary),
            None
        ) or product.productimage_set.all().first()
        product.primary_image = primary

        product.is_in_wishlist = product.id in wishlist_products
        
    return render(request, 'customer/home.html', {"products":products, 
                                                  "categories":category, 
                                                  "is_authenticated":is_authenticated,
                                                  "trending_products":trending_products})
    
def load_subcategories(request):
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        subcategories = SubCategory.objects.filter(category=category)
    else:
        subcategories = SubCategory.objects.all().order_by('name')

    data = []
    for sub in subcategories:
        data.append({
            "slug":sub.slug,
            "name":sub.name
        })

    return JsonResponse(data, safe=False)

def search_products(request):
    search_keyword = request.GET.get("search_keyword", "")
    all_result_products = Product.objects.filter(name__icontains=search_keyword)

    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    category = request.GET.get('category')
    subcategory = request.GET.get('subcategory')

    if min_price:
        all_result_products = all_result_products.filter(discount_price__gte=min_price)

    if max_price:
        all_result_products = all_result_products.filter(discount_price__lte=max_price)
    
    if category:
        category = get_object_or_404(Category, slug=category)
        all_result_products = all_result_products.filter(category = category)
    
    if subcategory:
        subcategory = get_object_or_404(SubCategory, slug=subcategory)
        all_result_products = all_result_products.filter(sub_category = subcategory)

    
    paginator = Paginator(all_result_products, 12)
    page_number = request.GET.get('page')
    result_products = paginator.get_page(page_number)

    for product in result_products:
        primary = product.productimage_set.filter(is_primary=True).first()
        if not primary:
            primary = product.productimage_set.first()
        product.primary_image = primary

        avg_rating = Reviews.objects.filter(product=product)\
        .aggregate(Avg('rating'))['rating__avg'] or 0
        product.avg_rating = int(round(avg_rating))

        number_of_reviews = Reviews.objects.filter(product=product).count()
        product.number_of_reviews = number_of_reviews  

    return render(request, 'customer/search_results.html', 
                  {"products":result_products, 
                   "search_keyword":search_keyword,
                   "categories" : categories,
                   "subcategories" :subcategories})

def search_suggestions(request):
    query = request.GET.get('q','')
    products = Product.objects.filter(name__icontains=query)[:5]
    data = list(products.values('name'))
    return JsonResponse(data, safe=False)

def category_filter(request, slug):
    category = get_object_or_404(Category, slug = slug)
    subcategories = SubCategory.objects.filter(category = category)
    all_products = Product.objects.filter(category=category)
    all_products = apply_filter(request, all_products)

    paginator = Paginator(all_products, 15)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    for product in products:

        primary = product.productimage_set.filter(is_primary=True).first()
        if not primary:
            primary = product.productimage_set.first()
        product.primary_image = primary

        avg_rating = Reviews.objects.filter(product=product)\
        .aggregate(Avg('rating'))['rating__avg'] or 0
        product.avg_rating = int(round(avg_rating))

        number_of_reviews = Reviews.objects.filter(product=product).count()
        product.number_of_reviews = number_of_reviews

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
    all_products = apply_filter(request, all_products)

    paginator = Paginator(all_products, 15)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    for product in products:

        primary = product.productimage_set.filter(is_primary=True).first()
        if not primary:
            primary = product.productimage_set.first()
        product.primary_image = primary
        
        avg_rating = Reviews.objects.filter(product=product)\
        .aggregate(Avg('rating'))['rating__avg'] or 0
        product.avg_rating = int(round(avg_rating))

        number_of_reviews = Reviews.objects.filter(product=product).count()
        product.number_of_reviews = number_of_reviews  

    return render(request, 'customer/product_category_filter.html', {
        "category":category,
        "subcategory":subcategory,
        "subcategories":subcategories,
        "products":products,
    })


def single_product_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    category = product.category
    is_in_wishlist = False

    reviews = Reviews.objects.filter(product=product).order_by('-created_at')

    avg_rating = Reviews.objects.filter(product=product)\
        .aggregate(Avg('rating'))['rating__avg'] or 0
    avg_rating = round(avg_rating, 1)
    
    number_of_ratings = Reviews.objects.filter(product=product).count()

    if request.user.is_authenticated:
        is_in_wishlist = WishList.objects.filter(user=request.user, product=product).exists()

    related_products = Product.objects.filter(category=category).exclude(slug=slug)[:5]

    for related_product in related_products:

        primary = related_product.productimage_set.filter(is_primary=True).first()
        if not primary:
            primary = related_product.productimage_set.first()
        related_product.primary_image = primary
        
        avg_rating = Reviews.objects.filter(product=product)\
        .aggregate(Avg('rating'))['rating__avg'] or 0
        related_product.avg_rating = int(round(avg_rating))

        number_of_reviews = Reviews.objects.filter(product=product).count()
        related_product.number_of_reviews = number_of_reviews

    product_attributes = product.productattribute_set.all()

    return render(request, 'customer/single_product_view.html', 
                  {"product" : product, 
                   "is_in_wishlist" : is_in_wishlist, 
                   "reviews" : reviews, 
                   "related_products" : related_products,
                   "avg_rating": avg_rating,
                   "number_of_ratings": number_of_ratings,
                   "product_attributes":product_attributes})

@customer_required
@login_required
def profile_page(request):
    active_orders_count = Order.objects.filter(user=request.user).exclude(status__in=['delivered', 'cancelled']).count()
    return render(request, 'customer/profile.html',{"active_orders_count":active_orders_count})

@customer_required
@login_required
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

@login_required
@customer_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    return render(request, 'customer/view_cart.html', {"cart":cart})

@login_required
@customer_required
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

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success', 
            'message': 'Added to cart',
        })

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

@login_required
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

    for item in wishlist:
        primary = item.product.productimage_set.filter(is_primary=True).first()
        if not primary:
            primary = item.product.productimage_set.first()

        item.primary_image = primary

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
            status = "removed"
        else:  
            WishList.objects.create(
                user=user,
                product=product
            )
            status = "added"
        return JsonResponse({"status":status})
        
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
  
@login_required
@customer_required
def checkout_page(request):
    user = request.user
    addresses = Address.objects.filter(user=user)
    
    mode = request.GET.get('mode', 'cart')
    product_id = request.GET.get('product_id')
    
    cart_items = []
    cart = None

    if mode == 'buy-now' and product_id:
        product = get_object_or_404(Product, id=product_id)
        cart_items = [{'product': product, 'quantity': 1}]
    else:
        cart = Cart.objects.filter(user=user).first()
        if not cart or not cart.cartitem_set.exists():
            return redirect('view_cart')
        cart_items = CartItem.objects.filter(cart=cart)
        mode = 'cart'

    return render(request, 'customer/checkout.html', {
        "addresses": addresses,
        "cart_items": cart_items,
        "mode": mode,
        "cart": cart,
    })

@login_required
@customer_required
def place_order(request):
    if request.method == "POST":
        user = request.user
        address_id = request.POST.get('address')
        address = get_object_or_404(Address, id=address_id)
        payment_method = request.POST.get('payment_mode')
        mode = request.POST.get('mode')

        if mode == 'buy-now':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)

            if product.stock < 1:
                messages.error(request, f"{product.name} is out of stock")
                return redirect('checkout_page')

        else:
            cart = get_object_or_404(Cart, user=user)
            cart_items = CartItem.objects.filter(cart=cart)

            for item in cart_items:
                if item.product.stock < item.quantity:
                    messages.error(request, f"{item.product.name} is out of stock")
                    return redirect('checkout_page')

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                address=address,
                payment_method=payment_method,
            )

            if mode == 'buy-now':
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=1,
                    price=product.discount_price
                )

                product.stock -= 1
                product.save()

            else:
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.price
                    )

                    product = item.product
                    product.stock -= item.quantity
                    product.save()

                cart_items.delete()

        if payment_method == 'cod':
            order.payment_status = "pending"
            order.save()
            return redirect('order_success', id=order.id)
        else:
            return redirect('payment_gateway', order_id=order.id)

    return redirect('checkout_page')

@login_required
@customer_required
def view_orders(request):
    status = request.GET.get('status')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    if status == 'all':
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
    elif status == 'pending':
        orders = Order.objects.filter(user=request.user, status="pending").order_by('-created_at')
    elif status == 'processing':
        orders = Order.objects.filter(user=request.user, status="processing").order_by('-created_at')
    elif status == 'shipped':
        orders = Order.objects.filter(user=request.user, status="shipped").order_by('-created_at')
    elif status == 'delivered':
        orders = Order.objects.filter(user=request.user, status="delivered").order_by('-created_at')
    elif status == 'cancelled':
        orders = Order.objects.filter(user=request.user, status="cancelled").order_by('-created_at')

    return render(request, 'customer/view_orders.html', {
        "orders" : orders
    })

def order_success(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)
    return render(request, 'customer/order_successfull.html', {'order': order})

def view_single_order(request, id):
    order = get_object_or_404(Order, id=id)
    return render(request, 'customer/view_single_order.html', {"order":order})

def apply_filter(request, queryset):
    sort_by = request.GET.get('sort_by')
    
    if sort_by == "price_low_to_high":
        queryset = queryset.order_by('discount_price')
    elif sort_by == "price_high_to_low":
        queryset = queryset.order_by('-discount_price')
    elif sort_by == "new_arrivals":
        queryset = queryset.order_by('created_at')

    return queryset

@login_required
@customer_required
def buy_now(request, id):
    user = request.user
    product = get_object_or_404(Product, id=id)

    addresses = Address.objects.filter(user=user)

    item = [{
        "product" : product,
        "quantity" : 1
    }]

    return render(request, 'customer/checkout.html', {
        "addresses" : addresses,
        "cart_items" : item,
        "mode":"buy-now"
    })

@login_required
@customer_required
def payment_gateway(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Initialize Razorpay Client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    # Razorpay expects amount in PAISE (1 INR = 100 Paise)
    # Use your grand_total property
    amount = int(order.grand_total * 100)
    
    data = {
        "amount": amount,
        "currency": "INR",
        "receipt": f"order_rcpt_{order.id}",
    }
    
    # Create the Razorpay Order
    razor_order = client.order.create(data=data)
    
    # Save the ID to our database
    order.razorpay_order_id = razor_order['id']
    order.save()
    
    return render(request, 'customer/payment_page.html', {
        "order": order,
        "razorpay_order_id": razor_order['id'],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "amount": amount,
        "user_email": request.user.email,
        "user_phone": order.address.phone,
    })

@login_required
@customer_required
def payment_success(request):
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    
    order = get_object_or_404(Order, id=order_id)
    
    # Update the order with the payment ID and change status
    order.razorpay_payment_id = payment_id 
    order.payment_status = "paid"
    order.save()
    
    return redirect('order_success', id=order.id)

@login_required
@customer_required
def password_reset(request):
    return render(request, 'customer/password_reset_customer.html')