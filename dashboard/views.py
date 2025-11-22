# dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='/accounts/login/')
def dashboard_view(request):
    """Dashboard utama untuk Petani"""
    return render(request, 'dashboard/dashboard.html')

@login_required(login_url='/accounts/login/')
def deteksi_view(request):
    return render(request, 'dashboard/deteksi.html')

@login_required(login_url='/accounts/login/')
def rekomendasi_view(request):
    return render(request, 'dashboard/rekomendasi.html')

@login_required(login_url='/accounts/login/')
def riwayat_view(request):
    return render(request, 'dashboard/riwayat.html')

@login_required(login_url='/accounts/login/')
def pengaturan_view(request):
    return render(request, 'dashboard/pengaturan.html')

@login_required(login_url='/accounts/login/')
def profile_view(request):
    return render(request, 'dashboard/profile.html')