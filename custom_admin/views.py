from django.shortcuts import render,redirect
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from customer.models import *
from core.models import *
from seller.models import *
from custom_admin.models import *
from django.contrib import messages

from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce

from django.db.models import Sum
from core.models import Product, User
from seller.models import SellerProfile
from customer.models import Order


def admin_dashboard(request):

    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_sellers = SellerProfile.objects.count()
    total_orders = Order.objects.count()

    recent_users = User.objects.order_by('-id')[:5]
    recent_orders = Order.objects.order_by('-id')[:5]
    recent_products = Product.objects.order_by('-id')[:5]
    recent_sellers = SellerProfile.objects.order_by('-id')[:5]

    low_stock_alert = Product.objects.filter(status = 'approved', stock__lt = 10).count()

    pending_sellers = SellerProfile.objects.filter(is_verified = True)
    pending_sellers_count = pending_sellers.count()

    total_revenue = OrderItem.objects.aggregate(
        total=Coalesce(
            Sum(
                ExpressionWrapper(
                    F('price') * F('quantity'),
                    output_field=DecimalField()
                )
            ),
            0,
            output_field=DecimalField()
        )
    )['total']

    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_sellers': total_sellers,
        'total_orders': total_orders,
        'pending_sellers_count' : pending_sellers_count,
        'low_stock_alert': low_stock_alert,

        'pending_sellers':pending_sellers,
        'recent_sellers':recent_sellers,
        'recent_users': recent_users,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
        'total_revenue': total_revenue,
    }

    return render(request, 'admin/admindashboard.html', context)

def admin_pending_products(request):
    products = Product.objects.filter(status='pending')
    messages.success(request,'Product approved successfully')
    return render(request,'admin/pending_products.html',{'products': products}) 


def approve_products(request,id):
    products = Product.objects.get(id=id)
    products.status = 'approved'
    products.save()
    return redirect('pending_products')


def reject_products(request,id):
    products = Product.objects.get(id)
    products.status = 'rejected'
    products.save()
    return redirect('pending_products')


def products_view(request):
    products = Product.objects.all()
    return render(request,'admin/productview.html',{'products':products})


def edit_product(request,id):
    products = Product.objects.get(id=id)
    category = Category.objects.all()
    subcategory = SubCategory.objects.all()
    seller = SellerProfile.objects.all()
    product_status = products.status

    if request.method  == 'POST':

        products.seller_id = request.POST.get('seller')
        products.name = request.POST.get('name')
        products.price = request.POST.get('price')
        products.discount_price = request.POST.get('discount_price')
        products.status = product_status
        products.description = request.POST.get('description')
        products.stock = request.POST.get('stock')
        products.category_id = request.POST.get('category')
        products.sub_category_id = request.POST.get('subcategory')
        products.save()

        return redirect('product_view')

    return render(request,'admin/edit_product.html',{'products':products, 'category':category, 'subcategory':subcategory, 'seller':seller})   



def seller_view(request):
    sellers = SellerProfile.objects.all()
    return render(request,'admin/sellerview.html',{'sellers':sellers})


def order_view(request):
    orders = Order.objects.all()
    return render(request,'admin/orderview.html',{'orders':orders})    


def user_view(request):
    users = User.objects.all()
    return render(request,'admin/userview.html',{'users':users})


def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name') 
        description = request.POST.get('description')
        image = request.FILES.get('image')

        Category.objects.create(

            name = name,
            description = description,
            image = image

        )  

        return redirect('category_list')
    
    return render(request,'admin/add_category.html') 


def category_list(request):
    categories = Category.objects.filter(is_active=True).prefetch_related('subcategory_set')
    return render(request,'admin/category_list.html',{'categories':categories})


def delete_category(request,id):
    categories = Category.objects.get(id=id)
    categories.delete()
    return redirect('category_list') 


def update_category(request,id):
    category = Category.objects.get(id=id)
    if request.method == 'POST':
        category.name = request.POST.get('name') 
        category.description = request.POST.get('description')
        category.image = request.FILES.get('image')
        category.save()

        return redirect('category_list')
    
    return render(request,'admin/update_category.html',{'category':category})


def active_category(request,id):
    category = Category.objects.get(id=id)
    category.is_active = True
    category.save()
    return redirect('category_list')


def deactivate_category(request,id):
    category = Category.objects.get(id=id)
    category.is_active = False
    category.save()
    return redirect('category_list')


def add_subcategory(request):
    categories = Category.objects.filter(is_active=True)
    selected_category = request.GET.get('category')
    if selected_category:
        selected_category=int(selected_category)
    if request.method == "POST":
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id)

        SubCategory.objects.create(

            name = name,
            category = category

        )

        return redirect('category_list')

    return render(request,'admin/add_subcategory.html',{'categories':categories, 'selected_category':selected_category})  

def update_subcategory(request,id):
    subcategory = SubCategory.objects.get(id=id)
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    if selected_category:
        selected_category=int(selected_category)
    if request.method == 'POST':
        subcategory.name = request.POST.get('name')
        subcategory.category_id = request.POST.get('category')
        subcategory.save()
        return redirect('category_list')
    
    return render(request,'admin/update_subcategory.html',{'subcategory':subcategory , 'categories':categories})


def delete_subcategory(request,id):
    subcategories = SubCategory.objects.get(id=id)
    subcategories.delete()
    return redirect('category_list')


def delete_product(request,id):
    products = Product.objects.get(id=id)
    products.delete()
    return redirect('product_view')


def deactivate_user(request,id):
    user = User.objects.get(id=id)
    user.is_active = False
    return redirect('user_view')


def order_details(request,id):
    orders = Order.objects.get(id=id)
    order_items = OrderItem.objects.all()
    return render(request,'admin/order_details.html',{'orders':orders, 'order_items':order_items})


def delete_order(request,id):
    orders = Order.objects.get(id=id)
    orders.delete
    return redirect('order_view')


def seller_details(request,id):
    sellers = SellerProfile.objects.get(id=id)
    return render(request,'admin/seller_details.html',{'sellers':sellers}) 


def deactivate_seller(request,id):
    sellers = SellerProfile.objects.get(id=id)
    sellers.is_active = False
    sellers.save()
    return redirect('seller_view')


def pending_seller(request):
    sellers  = SellerProfile.objects.filter(approved=False, is_active=True)
    count = SellerProfile.objects.count()
    messages.success(request,'Seller approved successfully')
    return render(request,'admin/pending_seller.html',{'sellers':sellers, 'count':count})


def approve_seller(request,id):
    sellers = SellerProfile.objects.get(id=id)
    sellers.approved = True
    sellers.save()
    return redirect('pending_seller')