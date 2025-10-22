# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import random

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


# Forgot Password
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.filter(email=email).first()

            # Buat kode reset acak
            reset_code = str(random.randint(100000, 999999))

            # Simpan di session (sementara)
            request.session['reset_email'] = email
            request.session['reset_code'] = reset_code

            # Kirim email
            send_mail(
                subject='Kode Reset Password Anda',
                message=f'Kode reset Anda adalah: {reset_code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "Kode reset telah dikirim ke email kamu!")
            return redirect('accounts:verify_reset_code')

        except User.DoesNotExist:
            messages.error(request, "Email tidak ditemukan.")
    
    return render(request, 'accounts/forgot_password.html')

# Reset Password - Verify Code
def verify_reset_code_view(request):
    return render(request, 'accounts/verify_reset_code.html')
def reset_password_view(request):
    if request.method == 'POST':
        email = request.session.get('reset_email')
        reset_code = request.session.get('reset_code')
        input_code = request.POST.get('reset_code')
        new_password = request.POST.get('new_password')

        if input_code == reset_code:
            try:
                user = User.objects.filter(email=email).first()
                user.set_password(new_password)
                user.save()

                # Hapus session
                del request.session['reset_email']
                del request.session['reset_code']

                messages.success(request, "Password berhasil direset! Silakan login.")
                return redirect('accounts:login')
            except User.DoesNotExist:
                messages.error(request, "Terjadi kesalahan. Silakan coba lagi.")
        else:
            messages.error(request, "Kode reset salah. Silakan coba lagi.")

    return render(request, 'accounts/reset_password.html')

# Logout
def logout_view(request):
    logout(request)
    messages.success(request, 'Anda berhasil logout. Sampai jumpa lagi!')
    return redirect('accounts:login')  # ✅ Redirect ke login