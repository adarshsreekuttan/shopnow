from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.utils.text import slugify

from core.models import User, Product, SubCategory
from seller.models import SellerProfile

from .decorators import seller_required


# Create your views here.
def seller_registration(request):
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('password')

        if User.objects.filter(email=email).exists():
            messages.error(request,'email already registered')
            return redirect('seller_login')
        if password!=request.POST.get('confirm_password'):
            messages.error(request,'password in not matched')
            return redirect('seller_login')
        user=User.objects.create_user(
            username=email,
            email=email,
            password=password,
            phone=request.POST.get('phone'),
            role='seller',
            is_verified=False
                    )
        SellerProfile.objects.create(
                user=user,
                shop_name=request.POST.get('shop_name'),
                address=request.POST.get('address'),
                pincode=request.POST.get('pincode'),
                state=request.POST.get('state'),
                city=request.POST.get('city'),
                gst_number=request.POST.get('gst_number'),  
                shop_logo=request.POST.get('shop_logo')      
                )
        messages.success(request,'succesfully created seller account')
        return redirect('seller_login')     
    return render(request,"seller/seller_registration.html")

def seller_login(request):
    if request.method=="POST":
        email=request.POST.get('seller_email')
        password=request.POST.get('seller_password')
        user=authenticate(request,username=email,password=password)
        print("USER:", user)
        if user is not None and user.role=='seller':
            sellerprofile=user.seller_profile
            if not sellerprofile.approved:
                messages.error(request,'your seller account not approved')
                return redirect('seller_login')
            login(request,user)  
            return redirect('seller_home')
        else:
            messages.error(request,'error')              
    return render(request,"seller/seller_login.html")

@seller_required
def seller_home(request):
    seller=request.user
    sellerprofile=seller.seller_profile

    return render(request, "seller/seller_home.html",{'sellerprofile':sellerprofile})  

def seller_profile(request):
    seller=request.user
    sellerprofile=seller.seller_profile
    return render(request,"seller/seller_profile.html",{'sellerprofile':sellerprofile}) 
 
def seller_profile_edit(request):
    seller_id=request.session.get('seller_id')
    seller=SellerProfile.objects.get(id=seller_id)        
    if request.method == "POST":
        seller.shop_name=request.POST.get('shop_name')
        seller.password=make_password(request.POST.get('password'))
        seller.email=request.POST.get('email')
        seller.phone=request.POST.get('phone')
        seller.address=request.POST.get('address')
        seller.pincode=request.POST.get('pincode')
        seller.state=request.POST.get('state')
        seller.city=request.POST.get('city')
        seller.gst_number=request.POST.get('gst_number')
        seller.save()
        return redirect('seller_profile')
    return render(request,"seller/seller_profile_edit.html",{'seller':seller})   

def seller_add_product(request):
    subcategory=SubCategory.objects.all()
    if request.method=="POST":
        product=Product()
        product.name=request.POST.get('product_name')
        product.price=request.POST.get('product_price')
        product.image=request.FILES.get('product_image')
        product.discount_price=request.POST.get('discount_price')
        product.description=request.POST.get('description')
        product.stock=request.POST.get('stock')
        product.sub_category=SubCategory.objects.get(id=request.POST.get('sub_category'))        
        base_slug=slugify(product.name)
    
        slug=base_slug
        count=1
        
        while Product.objects.filter(slug=slug).exists():
            slug=f"{base_slug}-{count}"
            count+=1
        
        
        product.slug= slug
        product.save()
        return redirect('seller_home')        
    return render(request,"seller/seller_add_product.html",{'subcategory':subcategory})

def seller_product_view(request,slug):
    product=Product.objects.get(slug=slug)
    return render(request,"seller/seller_product_view.html",{'product':product})
def seller_product_edit(request,slug):
    subcategory=SubCategory.objects.all()
    if request.method=="POST":
        product=Product()
        product.name=request.POST.get('product_name')
        product.price=request.POST.get('product_price')
        product.image=request.FILES.get('product_image')
        product.discount_price=request.POST.get('discount_price')
        product.description=request.POST.get('description')
        product.stock=request.POST.get('stock')
        product.sub_category=SubCategory.objects.get(id=request.POST.get('sub_category'))        
        base_slug=slugify(product.name)
        
        slug=base_slug
        count=1  
        while Product.objects.filter(slug=slug).exists():
            slug=f"{base_slug}-{count}"
            count+=1        
        product.slug= slug
        product.save()
        
        return redirect('seller_product_view')        
    return render(request,"seller/seller_product_edit.html",{'subcategory':subcategory})

def seller_password(request):
    seller_id=request.session.get('seller_id')
    seller=SellerProfile.objects.get(id=seller_id)
    if request.method=='POST':
        current_password=request.POST.get('current_password')
        new_password=request.POST.get('new_password')
        confirm_pssword=request.POST.get('confirm_password')
                
        if check_password(current_password,seller.password):
            if new_password==confirm_pssword:
                seller.password=make_password(new_password)
                seller.save()   
            else:
                error="new password is not matched"  
        else:
            error="current password is incorrect"  
        return render(request,'seller/seller_password.html',{'seller':seller,'error':error})                       
    return render(request,'seller/seller_password.html',{'seller':seller})