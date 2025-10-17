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

# Register (versi 1 input password)
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST.get('password1')

        # Validasi username & email
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah terdaftar")
            return redirect('accounts:register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email sudah terdaftar")
            return redirect('accounts:register')

        # Membuat user baru
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Akun berhasil dibuat, silakan login")
        return redirect('accounts:login')

    return render(request, 'accounts/register.html')



# Logout
def logout_view(request):
    logout(request)
    messages.success(request, 'Anda berhasil logout. Sampai jumpa lagi!')
    return redirect('accounts:login')  # ✅ Redirect ke login