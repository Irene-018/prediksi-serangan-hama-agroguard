# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

# Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Selamat datang, {user.username}!')
            return redirect('dashboard:home')  # ✅ Redirect ke dashboard
        else:
            messages.error(request, "Username atau password salah")
    return render(request, 'accounts/login.html')

# Register
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, "Password tidak sama")
            return redirect('accounts:register')  # ✅ Pakai app_name:url_name

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah terdaftar")
            return redirect('accounts:register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email sudah terdaftar")
            return redirect('accounts:register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Akun berhasil dibuat, silakan login")
        return redirect('accounts:login')  # ✅ Pakai app_name:url_name

    return render(request, 'accounts/register.html')

# Logout
def logout_view(request):
    logout(request)
    messages.success(request, 'Anda berhasil logout. Sampai jumpa lagi!')
    return redirect('accounts:login')  # ✅ Redirect ke login