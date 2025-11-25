from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_staff and not request.user.is_superuser:
            messages.error(request, "Anda tidak memiliki izin untuk mengakses halaman ini.")
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def user_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.is_staff or request.user.is_superuser:
            messages.warning(request, "Admin tidak bisa mengakses halaman ini.")
            return redirect('admin_dashboard:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
