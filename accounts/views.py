# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Petani, Admin


# =======================
# LOGIN VIEW
# =======================
def login_view(request):
    # Kalau sudah login, redirect sesuai role
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard:dashboard')
        else:
            return redirect('dashboard:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Redirect otomatis sesuai role
            if user.role == 'admin':
                return redirect('admin_dashboard:dashboard')
            else:
                return redirect('dashboard:home')
        else:
            return render(request, 'accounts/login.html', {
                'error': 'Username atau password salah.'
            })

    return render(request, 'accounts/login.html')


# =======================
# LOGOUT VIEW
# =======================
@login_required(login_url='/accounts/login/') 
def logout_view(request):
    """View untuk logout user"""
    logout(request)
    messages.success(request, 'Anda telah logout.')
    return redirect('accounts:login')


# =======================
# REGISTER VIEW (PETANI)
# =======================
@transaction.atomic
def register_petani(request):
    """View untuk registrasi petani baru"""
    if request.method == 'POST':
        nama_lengkap = request.POST.get('nama_lengkap', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')  # ✅ Cukup 1 field
        
        # Validasi field kosong
        if not all([nama_lengkap, username, email, password]):
            messages.error(request, 'Semua field harus diisi!')
            return render(request, 'accounts/register.html')
        
        # Validasi password minimal 8 karakter
        if len(password) < 8:
            messages.error(request, 'Password minimal 8 karakter!')
            return render(request, 'accounts/register.html')
        
        # Validasi username sudah ada
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan!')
            return render(request, 'accounts/register.html')
        
        # Validasi email sudah ada
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah digunakan!')
            return render(request, 'accounts/register.html')
        
        try:
            # 1. Buat CustomUser
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='petani'
            )
            
            # 2. Buat Petani profile
            Petani.objects.create(
                user=user,
                nama_lengkap=nama_lengkap,
                no_handphone='',
                alamat=''
            )
            
            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('accounts:login')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
            return render(request, 'accounts/register.html')
    
    return render(request, 'accounts/register.html')