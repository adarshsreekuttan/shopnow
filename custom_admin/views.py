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


    