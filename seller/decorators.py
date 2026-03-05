from django.shortcuts import redirect
from django.contrib import messages


def seller_required(view_func):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            return redirect('seller_login')
        if request.user.role !='seller':
            messages.error(request,"you are not seller")
            return redirect('seller_login')
        
        return view_func(request,*args,**kwargs)
    return wrapper