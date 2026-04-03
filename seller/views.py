from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model,update_session_auth_hash
from .models import SellerProfile,SubCategory,Category,ProductImage
from django.contrib import messages
from django.utils.text import slugify
from core.models import User, Product,ProductAttribute
from customer.models import Order,Reviews, OrderItem
from .decorators import seller_required
from django.http import JsonResponse
from custom_admin.models import Coupon
from django.core.paginator import Paginator
from customer.models import Reviews 

from django.db.models import Avg, Sum, F

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
    reviews = Reviews.objects.filter(product__seller=sellerprofile).order_by("-created_at")
    review_count = reviews.count()

    orders = Order.objects.filter(orderitem__seller = sellerprofile).order_by("-created_at")

    avarage_rating = reviews.aggregate(avg=Avg('rating'))['avg']

    total_revenue_data = get_seller_revenue(sellerprofile)

    revenue_data = get_weekly_revenue(sellerprofile)


    total_revenue = total_revenue_data['total_revenue']
    weekly_revenue = total_revenue_data['weekly_revenue']

    return render(request, "seller/seller_home.html",{'sellerprofile' : sellerprofile,
                                                      'product' : products,
                                                      "avarage_rating" : avarage_rating,
                                                      "reviews" : reviews,
                                                      "review_count" : review_count,
                                                      "orders" : orders,
                                                      "total_revenue":total_revenue,
                                                      "weekly_revenue":weekly_revenue,
                                                      "revenue_data" : revenue_data})  

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
        attribute_names=request.POST.getlist("attribute_names[]")
        attribute_values=request.POST.getlist("attribute_values[]")
        for name, value in  zip(attribute_names,attribute_values):
            if name and value:
                ProductAttribute.objects.create(
                    product=product,
                    name=name,
                    value=value
                )

        return redirect('product_control')        
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

def rejected_product(request):
    seller = request.user
    seller = seller.seller_profile
    products = Product.objects.filter(seller=seller, status='rejected')
    return render(request,'seller/rejected_products.html',{'products':products})

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
    seller = request.user
    seller = seller.seller_profile
    products = Product.objects.filter(seller=seller, status="approved")
    return render(request,'seller/product_control.html', {"products":products})

def inventory(request):
    seller=SellerProfile.objects.get(user=request.user)
    all_products=Product.objects.filter(seller=seller,status='approved')
    paginator=Paginator(all_products,15)
    page_no=request.GET.get('page')
    products=paginator.get_page(page_no)
    return render(request,'seller/inventory.html',{'products':products})

@seller_required
def under_review_products(request):
    seller = request.user
    seller = seller.seller_profile
    products = Product.objects.filter(seller=seller, status="pending")
    return render(request,"seller/under_review_products.html",{'products':products})

def pending_product_delete(request,id):
    seller=SellerProfile.objects.get(user=request.user)
    product=get_object_or_404(Product,status="pending",id=id,seller=seller)
    product.delete()
    return redirect('seller_pending_approval')

@seller_required
def seller_product_view(request,slug):
    product=Product.objects.get(slug=slug,status='approved')
    product_attributes = ProductAttribute.objects.filter(product=product)
    reviews = Reviews.objects.filter(product=product)
    if product.status=="pending":
        return redirect('seller_pending_approval')
    return render(request,"seller/seller_product_view.html",{'product':product, "reviews":reviews, "product_attributes":product_attributes})

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
    orders = Order.objects.filter(orderitem__seller=seller).order_by('-created_at')
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
    seller=SellerProfile.objects.get(user=request.user)
    order=Order.objects.filter(orderitem__seller=seller, status ="pending").order_by("-created_at")
    return render(request,"seller/pending_order.html",{'order':order})

@seller_required
def ongoing_order(request):
    seller = SellerProfile.objects.get(user=request.user)

    order = Order.objects.filter(
        orderitem__seller=seller,
        status__in=["shipped", "processing"]
    ).distinct().order_by("-created_at")

    return render(request, "seller/ongoing_order.html", {'order': order})

def finished_order(request):
    seller=SellerProfile.objects.get(user=request.user)
    order=Order.objects.filter(orderitem__seller=seller, status="delivered")
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

def view_reviews(request):
    seller = get_object_or_404(SellerProfile, user=request.user)
    reviews = Reviews.objects.filter(product__seller=seller, product__status = "approved")
    return render(request, 'seller/view_reviews.html', {'reviews': reviews})


from django.db.models import Sum, F

def get_seller_revenue(sellerprofile):
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())  # Monday

    queryset = OrderItem.objects.filter(
        seller=sellerprofile,
        order__status="delivered"
    )

    total_revenue = queryset.aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0
    
    weekly_revenue = queryset.filter(
        order__created_at__date__gte=week_start
    ).aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0

    return {
        "total_revenue": total_revenue,
        "weekly_revenue": weekly_revenue
    }

from django.utils import timezone
from datetime import timedelta

def get_weekly_revenue(sellerprofile):
    data = []
    raw_values = []
    
    for i in range(6, -1, -1):
        day = timezone.now().date() - timedelta(days=i)
        total = OrderItem.objects.filter(
            seller=sellerprofile,
            order__status='delivered',
            order__created_at__date=day
        ).aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or 0
        total = float(total)
        raw_values.append(total)
        data.append({
            'label': 'Today' if i == 0 else day.strftime('%a'),
            'value': float(total)
        })

    max_val = max(raw_values) if max(raw_values) > 0 else 1
    for entry in data:
        entry['percentage'] = (entry['value'] / max_val) * 100
        
    return data