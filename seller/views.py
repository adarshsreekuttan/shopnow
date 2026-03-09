<<<<<<< HEAD

from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth import get_user_model,update_session_auth_hash
from .models import SellerProfile,SubCategory,Category
from django.contrib import messages
from django.utils.text import slugify
from core.models import User, Product
from core.models import User, Product
from .decorators import seller_required
from django.http import JsonResponse


# Create your views here.
User = get_user_model()

def seller_registration(request):
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        if User.objects.filter(email=email).exists():
            messages.error(request,'email already registered')
            return redirect('seller_registration')
        if password!=request.POST.get('confirm_password'):
            messages.error(request,'password in not matched')
            return redirect('seller_registration')
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
                shop_logo=request.FILES.get('shop_logo')      
                )
        messages.success(request,'succesfully created seller account')
        return redirect('seller_login')     
    return render(request,"seller/seller_registration.html")

def seller_login(request):
    if request.method == "POST":
        email = request.POST.get('seller_email')
        password = request.POST.get('seller_password')

        user = authenticate(request, username=email, password=password)

        if user is None:
            messages.error(request, "Invalid email or password")
            return redirect('seller_login')

        if user.role != 'seller':
            messages.error(request, "You are not a seller")
            return redirect('seller_login')

        sellerprofile = user.seller_profile

        if not sellerprofile.approved:
            messages.error(request, "Your seller account is waiting for admin approval")
            return redirect('seller_login')

        login(request, user)
        return redirect('seller_home')

    return render(request, "seller/seller_login.html")
def seller_logout(request):
    logout(request)
    return redirect(seller_login)

@seller_required
def seller_home(request):
    seller=request.user
    sellerprofile=seller.seller_profile
    product=Product.objects.all()
    return render(request, "seller/seller_home.html",{'sellerprofile':sellerprofile,'product':product})  

@seller_required
def seller_profile(request):
    seller=request.user
    sellerprofile=seller.seller_profile
    return render(request,"seller/seller_profile.html",{'sellerprofile':sellerprofile}) 

@seller_required
def seller_profile_edit(request):
    seller=request.user
    sellerprofile=seller.seller_profile  
    if request.method == "POST":
        sellerprofile.shop_name=request.POST.get('shop_name')
        sellerprofile.email=request.POST.get('email')
        sellerprofile.phone=request.POST.get('phone')
        sellerprofile.address=request.POST.get('address')
        sellerprofile.pincode=request.POST.get('pincode')
        sellerprofile.state=request.POST.get('state')
        sellerprofile.city=request.POST.get('city')
        sellerprofile.gst_number=request.POST.get('gst_number')

        password=(request.POST.get('password'))
        if password:
            seller.set_password(password)
            seller.save() 
            update_session_auth_hash(request,seller)   
        sellerprofile.save()
        return redirect('seller_profile')
    return render(request,"seller/seller_profile_edit.html",{'seller':sellerprofile})   

@seller_required
def seller_add_product(request):
    subcategory=SubCategory.objects.all()
    category=Category.objects.all()
    if request.method=="POST":
        product=Product()
        product.name=request.POST.get('product_name')
        product.price=request.POST.get('product_price')
        product.image=request.FILES.get('product_image')
        product.discount_price=request.POST.get('discount_price')
        product.description=request.POST.get('description')
        product.stock=request.POST.get('stock')
        sub_category_slug=request.POST.get('sub_category')        
        product.sub_category=SubCategory.objects.get(slug=sub_category_slug)        
        category_slug=request.POST.get('category')      
        product.category=Category.objects.get(slug=category_slug)        
        base_slug=slugify(product.name)
    
        slug=base_slug
        count=1
        
        while Product.objects.filter(slug=slug).exists():
            slug=f"{base_slug}-{count}"
            count+=1
        
        
        product.slug= slug
        product.save()
        return redirect('seller_home')        
    return render(request,"seller/seller_add_product.html",{'category':category,'subcategory':subcategory})

@seller_required
def seller_product_view(request,slug):
    product=Product.objects.get(slug=slug)
    return render(request,"seller/seller_product_view.html",{'product':product})

@seller_required
def seller_product_edit(request,slug):
    product=Product.objects.get(slug=slug)
    subcategory=SubCategory.objects.all()
    if request.method=="POST":
        name=request.POST.get('product_name')
        product.name=name
        product.price=request.POST.get('product_price')
        product.image=request.FILES.get('product_image')
        product.discount_price=request.POST.get('discount_price')
        product.description=request.POST.get('description')
        product.stock=request.POST.get('stock')
        product.sub_category=SubCategory.objects.get(id=request.POST.get('sub_category'))        
        base_slug=slugify(product.name)
        
        if product.name != slugify(name):
            base_slug=slugify(name)
            new_slug=base_slug
            count=1  
            while Product.objects.filter(slug=new_slug).exclude(id=product.id).exists():
                slug=f"{base_slug}-{count}"
                count+=1        
        product.slug= slug
        product.save()
        
        return redirect('seller_product_view',slug=product.slug)        
    return render(request,"seller/seller_product_edit.html",{'product':product,'subcategory':subcategory})
def product_delete(request,id):
    product=Product.objects.get(id=id)
    product.delete()
    return redirect('seller_home')

def seller_password(request):                       
    return render(request,'seller/seller_password.html')

def load_subcategory(request):
    category_slug=request.GET.get('category_slug')
    subcategories=SubCategory.objects.filter(category__slug=category_slug).values('id','name')
    return JsonResponse(list(subcategories),safe=False)
