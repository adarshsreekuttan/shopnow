from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model,update_session_auth_hash
from .models import SellerProfile,SubCategory,Category,ProductImage
from django.contrib import messages
from django.utils.text import slugify
from core.models import User, Product,ProductAttribute
from customer.models import Order,Reviews
from .decorators import seller_required
from django.http import JsonResponse
from custom_admin.models import Coupon
from django.core.paginator import Paginator



# Create your views here.
User = get_user_model()

def testing(request):
    product=Product.objects.filter(status='approved')
    return render(request,'seller/testing.html',{'product':product})

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
    products=Product.objects.filter(seller=sellerprofile,status='approved') 
    return render(request, "seller/seller_home.html",{'sellerprofile':sellerprofile,'product':products})  

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
        seller.email=request.POST.get('email')
        seller.phone=request.POST.get('phone')
        seller.save()
        
        sellerprofile.shop_name=request.POST.get('shop_name')
        sellerprofile.address=request.POST.get('address')
        sellerprofile.pincode=request.POST.get('pincode')
        sellerprofile.state=request.POST.get('state')
        sellerprofile.city=request.POST.get('city')
        sellerprofile.gst_number=request.POST.get('gst_number') 
        sellerprofile.save()
        return redirect('seller_profile')
    return render(request,"seller/seller_profile_edit.html",{'seller':sellerprofile}) 
  
@seller_required
def password_reset(request):
    seller=request.user
    sellerprofile=seller.seller_profile
    if request.method=="POST":
        confirm_password=request.POST.get('confirm_password')
        current_password=request.POST.get('current_password')
        new_password=request.POST.get('new_password')
        if not check_password(current_password,seller.password):
            messages.error(request, "Current password is incorrect")
            return redirect('password_reset')
        if confirm_password!=new_password:
            messages.error(request, "password is mismatch")
            return redirect('password_reset')
        
        seller.set_password(new_password)
        seller.save() 
        update_session_auth_hash(request,seller)
        return redirect('seller_profile')                                 
    return render(request,'seller/password_reset.html',{'seller':sellerprofile})



@seller_required
def seller_add_product(request):
    seller=SellerProfile.objects.get(user=request.user)
    subcategory=SubCategory.objects.all()
    category=Category.objects.all()
    if request.method=="POST":
        product=Product()
        product.seller=seller
        product.name=request.POST.get('product_name')
        product.price=request.POST.get('product_price')
        product.discount_price=request.POST.get('discount_price')
        product.description=request.POST.get('description')
        product.stock=request.POST.get('stock')
        sub_category_slug=request.POST.get('sub_category')        
        product.sub_category=get_object_or_404(SubCategory, slug=sub_category_slug)      
        category_slug=request.POST.get('category')
        product.category=get_object_or_404(Category, slug=category_slug)      
        base_slug=slugify(product.name)
    
        slug=base_slug
        count=1
        
        while Product.objects.filter(slug=slug).exists():
            slug=f"{base_slug}-{count}"
            count+=1
        
        
        product.slug= slug
        product.save()
        images=request.FILES.getlist('product_images')
        for img in images:
            ProductImage.objects.create(
                product=product,
                image=img
            ) 
        first=product.productimage_set.first()
        if first:
            first.is_primary=True
            first.save()
        attribute_names=request.POST.getlist("attribute_names")
        attribute_values=request.POST.getlist("attribute_values")
        for name, value in  zip(attribute_names,attribute_values):
            if name and value:
                ProductAttribute.objects.create(
                    product=product,
                    name=name,
                    value=value
                )
            
            
                         
        return redirect('seller_approval')        
    return render(request,"seller/seller_add_product.html",{'category':category,'subcategory':subcategory})

def set_primary_img(request,id):
    image=ProductImage.objects.get(id=id)
    if request.method=="POST":
        ProductImage.objects.filter(product=image.product).update(is_primary=False)       
        image.is_primary=True
        image.save()
        
        product=image.product
        if product.status=="pending":
            return redirect('pending_edit',slug=image.product.slug)
        if product.status=="approved":
            return redirect('seller_product_edit',slug=image.product.slug)
        if product.status=="rejected":
            return redirect("reject_product_edit",slug=image.product.slug)

@seller_required
def load_subcategory(request):
    category_slug=request.GET.get('category_slug')
    subcategories=SubCategory.objects.filter(category__slug=category_slug).values('slug','name')
    return JsonResponse(list(subcategories),safe=False)

@seller_required
def seller_approval(request):
    return render(request,'seller/seller_approval.html')

def reject_product(request):
    product=Product.objects.filter(status='rejected')
    return render(request,'seller/reject_product.html',{'product':product})

@seller_required
def reject_product_edit(request,slug):
    
    product=Product.objects.get(slug=slug,status="rejected")
    subcategory=SubCategory.objects.all()
    if request.method=="POST":
        name=request.POST.get('product_name')
        product.name=name
        product.price=request.POST.get('product_price')
        product.discount_price=request.POST.get('discount_price')
        product.description=request.POST.get('description')
        product.stock=request.POST.get('stock')
        product.category=Category.objects.get(slug=request.POST.get('category'))        
        product.sub_category=SubCategory.objects.get(slug=request.POST.get('sub_category'))        
        
        base_slug=slugify(name)
        new_slug=base_slug
        count=1  
        while Product.objects.filter(slug=new_slug).exclude(id=product.id).exists():
                new_slug=f"{base_slug}-{count}"
                count+=1        
        product.slug= new_slug
        product.status="pending"
        product.save()
        images=request.FILES.getlist('product_image')
        if images:
            ProductImage.objects.filter(product=product).delete()
            for img in images:
                ProductImage.objects.create(
                    product=product,
                    image=img
                )        
        return redirect('seller_approval')        
    return render(request,"seller/reject_product_edit.html",{'product':product,'subcategory':subcategory})

@seller_required
def product_control(request):
    return render(request,'seller/product_control.html')

def inventory(request):
    seller=SellerProfile.objects.get(user=request.user)
    all_products=Product.objects.filter(seller=seller,status='approved')
    paginator=Paginator(all_products,15)
    page_no=request.GET.get('page')
    products=paginator.get_page(page_no)
    return render(request,'seller/inventory.html',{'products':products})

@seller_required
def seller_pending_approval(request):
    product=Product.objects.filter(status="pending")
    return render(request,"seller/seller_pending_approval.html",{'product':product})

def pending_product_delete(request,id):
    seller=SellerProfile.objects.get(user=request.user)
    product=get_object_or_404(Product,status="pending",id=id,seller=seller)
    product.delete()
    return redirect('seller_pending_approval')

@seller_required
def seller_product_view(request,slug):
    product=Product.objects.get(slug=slug,status='approved')
    if product.status=="pending":
        return redirect('seller_pending_approval')
    return render(request,"seller/seller_product_view.html",{'product':product})

@seller_required
def seller_product_edit(request,slug):
    product=Product.objects.get(slug=slug,status='approved')
    category=Category.objects.all()
    subcategory=SubCategory.objects.all()
    if request.method=="POST":
        name=request.POST.get('product_name')
        product.name=name
        product.price=request.POST.get('product_price')
        product.discount_price=request.POST.get('discount_price')
        product.description=request.POST.get('description')
        product.stock=request.POST.get('stock')
        sub_category_slug=request.POST.get('sub_category')        
        product.sub_category=get_object_or_404(SubCategory, slug=sub_category_slug)      
        category_slug=request.POST.get('category') 
        product.category=get_object_or_404(Category, slug=category_slug) 
               
        base_slug=slugify(name)
        new_slug=base_slug
        count=1  
        while Product.objects.filter(slug=new_slug).exclude(id=product.id).exists():
                new_slug=f"{base_slug}-{count}"
                count+=1        
        product.slug= new_slug
        product.status="pending"
        product.save()
        images=request.FILES.getlist('product_image')
        if images:
            ProductImage.objects.filter(product=product).delete()
            for img in images:
                ProductImage.objects.create(
                    product=product,
                    image=img
                )        
        return redirect('seller_pending_approval')        
    return render(request,"seller/seller_product_edit.html",{'product':product,'category':category,'subcategory':subcategory})

@seller_required
def product_delete(request,id):
    product=Product.objects.get(id=id,status='approved')
    product.delete()
    return redirect('seller_home')

@seller_required
def seller_password(request):                       
    return render(request,'seller/seller_password.html')

@seller_required
def seller_orders(request):
    seller=SellerProfile.objects.get(user=request.user)
    orders=Order.objects.filter(orderitem__product__seller=seller)
    return render(request,"seller/seller_orders.html",{'orders':orders})

@seller_required
def seller_single_order(request,id):
    order=get_object_or_404(Order,id=id)
    return render(request,'seller/seller_single_order.html',{'order':order})

@seller_required
def seller_order_status(request,id):
    orders=get_object_or_404(Order,id=id)
    if request.method=="POST":
        status=request.POST.get('status')
        orders.status=status
        orders.save()
    return redirect('seller_orders')

def pending_order(request):
    order=Order.objects.filter(status ="pending")
    return render(request,"seller/pending_order.html",{'order':order})

def ongoing_order(request):
    order=Order.objects.filter(status ="shipped")
    return render(request,"seller/ongoing_order.html",{'order':order})

def finished_order(request):
    order=Order.objects.filter(status="delivered")
    return render(request,'seller/finished_order.html',{'order':order})

@seller_required
def pending_single(request,slug):
    product=Product.objects.get(slug=slug,approved=False)
    return render(request,'seller/pending_single.html',{'product':product})

@seller_required
def pending_edit(request,slug):
    
    product=Product.objects.get(slug=slug,status="pending")
    subcategory=SubCategory.objects.all()
    if request.method=="POST":
        name=request.POST.get('product_name')
        product.name=name
        product.price=request.POST.get('product_price')
        product.discount_price=request.POST.get('discount_price')
        product.description=request.POST.get('description')
        product.stock=request.POST.get('stock')
        product.category=Category.objects.get(slug=request.POST.get('category'))        
        product.sub_category=SubCategory.objects.get(slug=request.POST.get('sub_category'))        
        
        base_slug=slugify(name)
        new_slug=base_slug
        count=1  
        while Product.objects.filter(slug=new_slug).exclude(id=product.id).exists():
                new_slug=f"{base_slug}-{count}"
                count+=1        
        product.slug= new_slug
        product.status="pending"
        product.save()
        images=request.FILES.getlist('product_image')
        if images:
            ProductImage.objects.filter(product=product).delete()
            for img in images:
                ProductImage.objects.create(
                    product=product,
                    image=img
                )        
        return redirect('pending_single',slug=product.slug)        
    return render(request,"seller/pending_edit.html",{'product':product,'subcategory':subcategory})

def message(request):
    return render(request,'seller/message.html')

def coupon(request):
    return render(request,'seller/coupon.html')

def add_coupon(request):
    seller=SellerProfile.objects.get(user=request.user)
    if request.method=='POST':
        coupon=Coupon()
        code=request.POST.get('code')
        if Coupon.objects.filter(code=code).exists():
            messages.error(request,'Coupon code already exists')
            return redirect('add_coupon')
        coupon.seller=seller
        coupon.code=code
        coupon.discount_type=request.POST.get('discount_type')
        coupon.discount_value=request.POST.get('discount_value')
        coupon.min_purchase=request.POST.get('min_purchase')
        coupon.valid_from=request.POST.get('valid_from')
        coupon.valid_to=request.POST.get('valid_to')
        coupon.usage_limit=request.POST.get('usage_limit')
        coupon.save()
        messages.success(request,'successfully created coupon')
        return redirect('coupon_pending')
    return render(request,'seller/add_coupon.html')

def coupon_active(request):
    seller=SellerProfile.objects.get(user=request.user)
    coupon=Coupon.objects.filter(seller=seller,approved=True)
    return render(request,'seller/coupon_active.html',{'coupons':coupon})

def coupon_pending(request):
    seller=SellerProfile.objects.get(user=request.user)
    coupon=Coupon.objects.filter(seller=seller,approved=False)
    return render(request,'seller/coupon_pending.html',{'coupons':coupon})

def coupon_delete(request,id):
    seller=SellerProfile.objects.get(user=request.user)
    coupon=Coupon.objects.filter(seller=seller,id=id)
    coupon.delete()
    return redirect('coupon')
    