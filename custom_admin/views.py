from django.shortcuts import render,redirect
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from customer.models import *
from core.models import *
from seller.models import *
from custom_admin.models import *


# Create your views here.

def admin_dashboard(request):

    total_users = User.objects.all().count()
    total_products = Product.objects.all().count()
    total_sellers = SellerProfile.objects.all().count()
    total_orders = Order.objects.all().count()

    context = {
        'total_users' : total_users,
        'total_products' : total_products,
        'total_sellers' : total_sellers,
        'total_orders' : total_orders 
    }

    return render(request,'admin/admindashboard.html', context )


def admin_pending_products(request):
    products = Product.objects.filter(status='pending')
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
    categories = Category.objects.filter(is_active=True)
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
    if request.method == "POST":
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id)

        SubCategory.objects.create(

            name = name,
            category = category

        )

        return redirect('subcategory_list')

    return render(request,'admin/add_subcategory.html',{'categories':categories})  


def subcategory_list(request):
    subcategories = SubCategory.objects.all()
    return render(request,'admin/subcategory_list.html',{'subcategories':subcategories})


def update_subcategory(request,id):
    subcategory = SubCategory.objects.get(id=id)
    categories = Category.objects.all()
    if request.method == 'POST':
        subcategory.name = request.POST.get('name')
        subcategory.category_id = request.POST.get('category')
        subcategory.save()
        return redirect('subcategory_list')
    
    return render(request,'admin/update_subcategory.html',{'subcategory':subcategory , 'categories':categories})


def delete_subcategory(request,id):
    subcategories = SubCategory.objects.get(id=id)
    subcategories.delete()
    return redirect('subcategory_list')