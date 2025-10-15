from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import PencegahanHama


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


# =======================
# ⚙️ ADMIN DASHBOARD
# =======================
@login_required(login_url='dashboard:login')
def admin_dashboard(request):
    chart_data = {
        'labels': ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat'],
        'values': [12, 19, 3, 5, 2],
    }
    return render(request, 'admin_dashboard/index.html', {'chart_data': chart_data})


# =======================
# 🪲 CRUD PENCEGAHAN HAMA
# =======================
@login_required(login_url='dashboard:login')
def pencegahan_list(request):
    data = PencegahanHama.objects.all()
    return render(request, 'admin_dashboard/pencegahan_list.html', {'data': data})

@login_required(login_url='dashboard:login')
def tambah_pencegahan(request):
    if request.method == 'POST':
        jenis_hama = request.POST['jenis_hama']
        judul = request.POST['judul']
        sumber = request.POST['sumber']
        deskripsi = request.POST.get('deskripsi', '')

        PencegahanHama.objects.create(
            jenis_hama=jenis_hama,
            judul=judul,
            sumber=sumber,
            deskripsi=deskripsi
        )
        return redirect('dashboard:pencegahan_list')

    return render(request, 'admin_dashboard/tambah_pencegahan.html')

@login_required(login_url='dashboard:login')
def edit_pencegahan(request, id):
    data = get_object_or_404(PencegahanHama, id=id)
    if request.method == 'POST':
        data.jenis_hama = request.POST['jenis_hama']
        data.judul = request.POST['judul']
        data.sumber = request.POST['sumber']
        data.deskripsi = request.POST.get('deskripsi', '')
        data.save()
        return redirect('dashboard:pencegahan_list')

    return render(request, 'admin_dashboard/edit_pencegahan.html', {'data': data})

@login_required(login_url='dashboard:login')
def hapus_pencegahan(request, id):
    data = get_object_or_404(PencegahanHama, id=id)
    data.delete()
    return redirect('dashboard:pencegahan_list')

@login_required(login_url='dashboard:login')
def detail_pencegahan(request, id):
    data = get_object_or_404(PencegahanHama, id=id)
    return render(request, 'admin_dashboard/detail_pencegahan.html', {'data': data})


# =======================
# 🔑 LOGIN & LOGOUT
# =======================
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard:admin_dashboard')
        else:
            return render(request, 'accounts/login.html', {'error': 'Username atau password salah.'})

    return render(request, 'accounts/login.html')


@login_required(login_url='dashboard:login')
def logout_view(request):
    logout(request)
    return redirect('dashboard:login')
