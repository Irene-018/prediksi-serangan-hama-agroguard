# admin_dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import JenisHama, PencegahanHama

# Dapatkan model User yang benar (CustomUser)
User = get_user_model()

# ============================================
# USER MANAGEMENT VIEWS (tetap sama seperti sebelumnya)
# ============================================

@login_required(login_url='/accounts/login/')
def dashboard_view(request):
    """Dashboard Admin"""
    return render(request, 'admin_dashboard/dashboard.html')

@login_required(login_url='/accounts/login/')
def kelola_user_view(request):
    """Kelola User - Menampilkan semua pengguna"""
    pengguna_list = User.objects.all().order_by('-date_joined')
    
    context = {
        'pengguna_list': pengguna_list,
        'current_user': request.user,
    }
    return render(request, 'admin_dashboard/kelola_user.html', context)

@login_required(login_url='/accounts/login/')
def tambah_user_view(request):
    """Tambah User Baru"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan!')
            return render(request, 'admin_dashboard/tambah_user.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah digunakan!')
            return render(request, 'admin_dashboard/tambah_user.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        messages.success(request, f'User {username} berhasil ditambahkan!')
        return redirect('admin_dashboard:kelola_user')
    
    return render(request, 'admin_dashboard/tambah_user.html')

@login_required(login_url='/accounts/login/')
def edit_user_view(request, id):
    """Edit User"""
    user_to_edit = get_object_or_404(User, id=id)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        is_active = request.POST.get('is_active') == 'on'
        new_password = request.POST.get('password')
        
        if username != user_to_edit.username:
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Username "{username}" sudah digunakan oleh user lain!')
                context = {'user': user_to_edit}
                return render(request, 'admin_dashboard/edit_user.html', context)
        
        if email != user_to_edit.email:
            if User.objects.filter(email=email).exists():
                messages.error(request, f'Email "{email}" sudah digunakan oleh user lain!')
                context = {'user': user_to_edit}
                return render(request, 'admin_dashboard/edit_user.html', context)
        
        user_to_edit.username = username
        user_to_edit.email = email
        user_to_edit.is_active = is_active
        
        if new_password and new_password.strip():
            user_to_edit.set_password(new_password)
        
        try:
            user_to_edit.save()
            messages.success(request, f'User {user_to_edit.username} berhasil diupdate!')
            return redirect('admin_dashboard:kelola_user')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
            context = {'user': user_to_edit}
            return render(request, 'admin_dashboard/edit_user.html', context)
    
    context = {
        'user': user_to_edit,
    }
    return render(request, 'admin_dashboard/edit_user.html', context)

@login_required(login_url='/accounts/login/')
def hapus_user_view(request, id):
    """Hapus User"""
    user = get_object_or_404(User, id=id)
    
    if user.id == request.user.id:
        messages.error(request, 'Anda tidak bisa menghapus akun sendiri!')
        return redirect('admin_dashboard:kelola_user')
    
    username = user.username
    user.delete()
    messages.success(request, f'User {username} berhasil dihapus!')
    return redirect('admin_dashboard:kelola_user')

# ============================================
# HAMA MANAGEMENT VIEWS
# ============================================

@login_required(login_url='/accounts/login/')
def data_hama_view(request):
    """Menampilkan daftar hama"""
    hama_list = JenisHama.objects.all().order_by('-created_at')
    return render(request, 'admin_dashboard/data_hama.html', {
        'hama_list': hama_list, 
        'current_user': request.user
    })

@login_required(login_url='/accounts/login/')
def tambah_hama_view(request):
    """Tambah Jenis Hama Baru"""
    if request.method == 'POST':
        nama = request.POST.get('nama')
        nama_latin = request.POST.get('nama_latin', '')
        deskripsi = request.POST.get('deskripsi')
        gejala = request.POST.get('gejala', '')
        gambar = request.FILES.get('gambar')
        
        if not nama or not deskripsi:
            messages.error(request, 'Nama dan deskripsi harus diisi!')
            return render(request, 'admin_dashboard/tambah_hama.html')
        
        hama = JenisHama.objects.create(
            nama=nama,
            nama_latin=nama_latin,
            deskripsi=deskripsi,
            gejala=gejala,
            gambar=gambar
        )
        
        messages.success(request, f'Jenis hama "{nama}" berhasil ditambahkan!')
        return redirect('admin_dashboard:data_hama')
    
    return render(request, 'admin_dashboard/tambah_hama.html')

@login_required(login_url='/accounts/login/')
def edit_hama_view(request, id):
    """Edit Jenis Hama"""
    hama = get_object_or_404(JenisHama, id=id)
    
    if request.method == 'POST':
        hama.nama = request.POST.get('nama')
        hama.nama_latin = request.POST.get('nama_latin', '')
        hama.deskripsi = request.POST.get('deskripsi')
        hama.gejala = request.POST.get('gejala', '')
        
        if request.FILES.get('gambar'):
            hama.gambar = request.FILES.get('gambar')
        
        try:
            hama.save()
            messages.success(request, f'Jenis hama "{hama.nama}" berhasil diupdate!')
            return redirect('admin_dashboard:data_hama')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    context = {
        'hama': hama,
    }
    return render(request, 'admin_dashboard/edit_hama.html', context)

@login_required(login_url='/accounts/login/')
def hapus_hama_view(request, id):
    """Hapus Jenis Hama"""
    hama = get_object_or_404(JenisHama, id=id)
    
    nama = hama.nama
    hama.delete()
    messages.success(request, f'Jenis hama "{nama}" berhasil dihapus!')
    return redirect('admin_dashboard:data_hama')

# ============================================
# PENCEGAHAN MANAGEMENT VIEWS
# ============================================

@login_required(login_url='/accounts/login/')
def data_pencegahan_view(request):
    """Menampilkan daftar pencegahan hama"""
    pencegahan_list = PencegahanHama.objects.select_related('jenis_hama').all().order_by('-created_at')
    return render(request, 'admin_dashboard/data_pencegahan.html', {
        'pencegahan_list': pencegahan_list,
        'current_user': request.user
    })

@login_required(login_url='/accounts/login/')
def tambah_pencegahan_view(request):
    """Tambah Data Pencegahan Baru"""
    if request.method == 'POST':
        jenis_hama_id = request.POST.get('jenis_hama')
        judul = request.POST.get('judul')
        sumber = request.POST.get('sumber')
        deskripsi = request.POST.get('deskripsi', '')
        
        # Validasi
        if not jenis_hama_id or not judul or not sumber:
            messages.error(request, 'Jenis hama, judul, dan sumber harus diisi!')
            hama_list = JenisHama.objects.all()
            return render(request, 'admin_dashboard/tambah_pencegahan.html', {'hama_list': hama_list})
        
        try:
            jenis_hama = JenisHama.objects.get(id=jenis_hama_id)
            
            # Buat pencegahan baru
            pencegahan = PencegahanHama.objects.create(
                jenis_hama=jenis_hama,
                judul=judul,
                sumber=sumber,
                deskripsi=deskripsi,
                status='aktif',
                created_by=request.user
            )
            
            messages.success(request, f'Data pencegahan "{judul}" berhasil ditambahkan!')
            return redirect('admin_dashboard:data_pencegahan')
        
        except JenisHama.DoesNotExist:
            messages.error(request, 'Jenis hama tidak ditemukan!')
            hama_list = JenisHama.objects.all()
            return render(request, 'admin_dashboard/tambah_pencegahan.html', {'hama_list': hama_list})
    
    # GET request
    hama_list = JenisHama.objects.all()
    return render(request, 'admin_dashboard/tambah_pencegahan.html', {'hama_list': hama_list})

@login_required(login_url='/accounts/login/')
def edit_pencegahan_view(request, id):
    """Edit Data Pencegahan"""
    pencegahan = get_object_or_404(PencegahanHama, id=id)
    
    if request.method == 'POST':
        jenis_hama_id = request.POST.get('jenis_hama')
        judul = request.POST.get('judul')
        sumber = request.POST.get('sumber')
        deskripsi = request.POST.get('deskripsi', '')
        status = request.POST.get('status', 'aktif')
        
        try:
            jenis_hama = JenisHama.objects.get(id=jenis_hama_id)
            
            # Update data
            pencegahan.jenis_hama = jenis_hama
            pencegahan.judul = judul
            pencegahan.sumber = sumber
            pencegahan.deskripsi = deskripsi
            pencegahan.status = status
            pencegahan.save()
            
            messages.success(request, f'Data pencegahan "{judul}" berhasil diupdate!')
            return redirect('admin_dashboard:data_pencegahan')
        
        except JenisHama.DoesNotExist:
            messages.error(request, 'Jenis hama tidak ditemukan!')
    
    # GET request
    hama_list = JenisHama.objects.all()
    context = {
        'pencegahan': pencegahan,
        'hama_list': hama_list,
    }
    return render(request, 'admin_dashboard/edit_pencegahan.html', context)

@login_required(login_url='/accounts/login/')
def hapus_pencegahan_view(request, id):
    """Hapus Data Pencegahan"""
    if request.method == 'POST':
        pencegahan = get_object_or_404(PencegahanHama, id=id)
        judul = pencegahan.judul
        pencegahan.delete()
        messages.success(request, f'Data pencegahan "{judul}" berhasil dihapus!')
    
    return redirect('admin_dashboard:data_pencegahan')

# ============================================
# LAHAN VIEWS (placeholder)
# ============================================

def data_lahan_view(request):
    lahan_list = []
    return render(request, 'admin_dashboard/data_lahan.html', {
        'lahan_list': lahan_list, 
        'current_user': request.user
    })

def tambah_lahan_view(request):
    return render(request, 'admin_dashboard/tambah_lahan.html')

def edit_lahan_view(request, id):
    return render(request, 'admin_dashboard/edit_lahan.html', {'id': id})