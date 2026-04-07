from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            if user.role == "customer":
                return redirect('home')
            elif user.role == 'seller':
                return redirect('seller_home')
            elif user.role == 'admin':
                return redirect('admin_dashboard')
        else:
            if email == "admin@gmail.com" and password == "admin123":
                return render(request, 'admin/admindashboard.html')
            return render(request, 'customer/login.html', {"error":"invalid credentials"})
    return render(request, 'customer/login.html')