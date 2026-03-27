from functools import wraps
from django.shortcuts import redirect

def customer_required(view_func):

    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):

        if request.user.role != "customer":
            return redirect("customer_login")

        return view_func(request, *args, **kwargs)

    return wrapped_view