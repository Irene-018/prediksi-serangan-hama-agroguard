# admin_dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='/accounts/login/')
def dashboard_view(request):
    """Dashboard Admin"""
    return render(request, 'admin_dashboard/dashboard.html')

login_required(login_url='/accounts/login/')
def kelola_user_view(request):
    # Logika autentikasi admin harus diterapkan di sini
    return render(request, 'admin_dashboard/kelola_user.html', {})

@login_required(login_url='/accounts/login/')
def data_hama_view(request):
    # Logika autentikasi admin harus diterapkan di sini
    return render(request, 'admin_dashboard/data_hama.html', {})

@login_required(login_url='/accounts/login/')
def data_pencegahan_view(request):
    # Logika autentikasi admin harus diterapkan di sini
    return render(request, 'admin_dashboard/data_pencegahan.html', {})

def data_lahan_view(request):
    # nanti bisa ambil data dari model Lahan, untuk sekarang dummy dulu
    lahan_list = []
    return render(request, 'admin_dashboard/data_lahan.html', {'lahan_list': lahan_list, 'current_user': request.user})

def tambah_lahan_view(request):
    return render(request, 'admin_dashboard/tambah_lahan.html')

def edit_lahan_view(request, id):
    return render(request, 'admin_dashboard/edit_lahan.html', {'id': id})


def tambah_user_view(request):
    return render(request, 'admin_dashboard/tambah_user.html')

def edit_user_view(request, id):
    return render(request, 'admin_dashboard/edit_user.html', {'id': id})

def data_hama_view(request):
    # ganti dengan pengambilan data model sebenarnya nanti
    hama_list = []  # atau Hama.objects.all()
    return render(request, 'admin_dashboard/data_hama.html', {'hama_list': hama_list, 'current_user': request.user})

def tambah_hama_view(request):
    # implementasi form POST nanti; sementara render template placeholder
    if request.method == 'POST':
        # proses form lalu redirect
        pass
    return render(request, 'admin_dashboard/tambah_hama.html')

def edit_hama_view(request, id):
    # ambil instance hama lalu render form edit
    return render(request, 'admin_dashboard/edit_hama.html', {'id': id})

def tambah_pencegahan_view(request):
    return render(request, 'admin_dashboard/tambah_pencegahan.html')

