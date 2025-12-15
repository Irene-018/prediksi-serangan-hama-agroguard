# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Petani, Admin
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings
import random



# =======================
# LOGIN VIEW
# =======================
def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard:dashboard')
        return redirect('dashboard:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard:dashboard')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Username atau password salah.')
            return redirect('accounts:login')

    return render(request, 'accounts/login.html')


# =======================
# FORGOT PASSWORD VIEW
# ======================= 
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # 🔥 Ambil user dari DATABASE (hasil register / login)
        user = CustomUser.objects.filter(email=email).first()

        if not user:
            messages.error(request, "Email tidak terdaftar. Gunakan email saat registrasi.")
            return redirect('accounts:forgot_password')

        # Generate kode reset
        reset_code = str(random.randint(100000, 999999))

        # Simpan di session
        request.session['reset_email'] = email
        request.session['reset_code'] = reset_code

        # Kirim email (console / smtp)
        send_mail(
            subject='Kode Reset Password AgroGuard',
            message=f'Halo {user.username},\n\nKode reset password kamu adalah: {reset_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, "Kode reset telah dikirim ke email terdaftar.")
        return redirect('accounts:reset_password')

    return render(request, 'accounts/forgot_password.html')

# =======================
# RESET PASSWORD VIEW
# =======================
def reset_password_view(request):
    if request.method == 'POST':
        email = request.session.get('reset_email')
        reset_code = request.session.get('reset_code')

        input_code = request.POST.get('reset_code')
        new_password = request.POST.get('new_password')

        if input_code != reset_code:
            messages.error(request, "Kode reset salah.")
            return render(request, 'accounts/reset_password.html')

        user = CustomUser.objects.filter(email=email).first()
        if not user:
            messages.error(request, "User tidak ditemukan.")
            return redirect('accounts:forgot_password')

        user.set_password(new_password)
        user.save()

        request.session.flush()

        messages.success(request, "Password berhasil direset.")
        return redirect('accounts:login')

    return render(request, 'accounts/reset_password.html')

# =======================
# VERIFY RESET CODE VIEW
# =======================
def verify_reset_code_view(request):
    return HttpResponse("Verify reset code page (TODO)")


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