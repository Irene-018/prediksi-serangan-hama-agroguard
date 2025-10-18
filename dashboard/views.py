from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout


# =======================
# 🔐 DASHBOARD USER (Login Required)
# =======================
@login_required(login_url='dashboard:login')
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')

@login_required(login_url='dashboard:login')
def deteksi_view(request):
    return render(request, 'dashboard/deteksi.html')

@login_required(login_url='dashboard:login')
def rekomendasi_view(request):
    return render(request, 'dashboard/rekomendasi.html')

@login_required(login_url='dashboard:login')
def riwayat_view(request):
    return render(request, 'dashboard/riwayat.html')

@login_required(login_url='dashboard:login')
def pengaturan_view(request):
    return render(request, 'dashboard/pengaturan.html')

@login_required(login_url='dashboard:login')
def profile_view(request):
    return render(request, 'dashboard/profile.html')


# =======================
# 🔑 LOGIN & LOGOUT
# =======================
def login_view(request):
    # Jika user sudah login, redirect ke home
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard:home')
        else:
            return render(request, 'accounts/login.html', {'error': 'Username atau password salah.'})

    return render(request, 'accounts/login.html')


@login_required(login_url='dashboard:login')
def logout_view(request):
    logout(request)
    return redirect('dashboard:login')