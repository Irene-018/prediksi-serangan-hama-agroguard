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
            return redirect('home')  # ganti 'home' dengan nama path yang benar
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
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah terdaftar")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Akun berhasil dibuat, silakan login")
        return redirect('login')

    return render(request, 'accounts/register.html')

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')
