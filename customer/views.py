from django.shortcuts import get_object_or_404, render, redirect
from core.models import User
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.http import HttpResponse
from core.models import Product
from seller.models import Category, SubCategory
from django.contrib.auth.decorators import login_required
from .models import Address

def customer_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            error = None
            return redirect('home')
        else:
            error = "invalid edwuug or password"
            return render(request, 'customer/login.html', {"error":error})

    return render(request, 'customer/login.html')

def customer_register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.create_user(
            username = email,
            email = email,
            password = password,
            first_name = first_name,
            last_name = last_name
        )

        return HttpResponse("user creted!!!")

    return render(request, 'customer/register.html')

def home_view(request):
    products = Product.objects.all()
    category = Category.objects.all()
    return render(request, 'customer/home.html', {"products":products, "categories":category})

def single_product_view(request, slug):
    product = Product.objects.get(slug=slug)
    return render(request, 'customer/single_product_view.html', {"product":product})

def profile_page(request):
    return render(request, 'customer/profile.html')

def customer_logout(request):
    logout(request)
    return redirect('home')

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

def view_addresses(request):
    user = request.user
    addresses = Address.objects.filter(user = user.id)
    return render(request, 'customer/view_addresses.html', {"addresses":addresses})

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

def delete_address(request,id):
    address = get_object_or_404(Address, id=id, user=request.user)
    address.delete()
    return redirect('view_addresses')