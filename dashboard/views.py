from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='accounts:login')  # ✅ Redirect ke login 
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')

@login_required(login_url='accounts:login')  # ✅ Redirect ke login 
def deteksi_view(request):
    return render(request, 'dashboard/deteksi.html')

@login_required(login_url='accounts:login')  # ✅ Redirect ke login
def rekomendasi_view(request):
    return render(request, 'dashboard/rekomendasi.html')

@login_required(login_url='accounts:login')  # ✅ Redirect ke login
def riwayat_view(request):
    return render(request, 'dashboard/riwayat.html')
