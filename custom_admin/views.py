from django.shortcuts import render,redirect
from django.contrib.auth import login,logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from seller.models import Category, SubCategory
from custom_admin.models import AdminLogin


# Create your views here.


def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            admin = AdminLogin.objects.get(email=email, password=password)
            request.session['admin_email'] = admin.email
            return redirect('admin_dash')
        
        except AdminLogin.DoesNotExist:
            return render(request, "admin/adminlogin.html", {"error": "Invalid Email or Password"})

    return render(request, "admin/adminlogin.html")    


def admin_dash(request):
    if request.session.get('admin_email'):
        return render(request, "admin/admindash.html")
    else:
        return redirect('adminlogin')

def category_list(request):
    categories =  Category.objects.all()
    return render(request,'admin/catlist.html',{'cat':categories})


def add_category(request):
    if request.method == "POST":
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')

        Category.objects.create(
            name = name,
            slug = slugify(name),
            description = description
        )

        return redirect('cat_list')

    return render(request,'admin/addcat.html')  


def delete_cat(request,id):
     categories = Category.objects.get(id=id)
     categories.delete()
     return redirect('cat_list')
   

def update_category(request,id):

    update = Category.objects.get(id=id)
    if request.method == "POST":
        update.name = request.POST.get('name')
        update.slug = request.POST.get('slug')
        update.description = request.POST.get('description')
        update.save()

        return redirect('cat_list')

    return render(request,'admin/updatecat.html',{'cat':update})     


def admin_logout(request):
    logout(request)
    return redirect('admin_login')



def add_subcategory(request):

    if not request.user.is_staff:
        return redirect('admin_login')
    
    categories = Category.objects.all()

    if request.method == "POST":
        category_id = request.POST.get('category')
        name = request.POST.get('name')

        category = Category.objects.get(id=category_id)

        SubCategory.objects.create(
            Category = category,
            name = name
        )

        return redirect('subcat_list')

    return render(request,'admin/add_subcat.html',{'categories':categories})



def sub_categorylist(request):
    categories = SubCategory.objects.all()
    return render(request,'admin/subcat_list.html',{'cat':categories})

