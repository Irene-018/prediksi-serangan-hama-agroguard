from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JenisHama, PencegahanHama
from django.db.models import Count
from datetime import datetime

#@login_required
def dashboard_view(request):
    """
    View untuk halaman dashboard admin
    """
    # DATA DUMMY DULU - biar ga error
    context = {
        'total_card1': 15,
        'total_card2': 8, 
        'total_card3': 5,
        'top_hama': [
            {'nama': 'Hama A'},
            {'nama': 'Hama B'}, 
            {'nama': 'Hama C'}
        ],
        'hama_sering': {'nama': 'Hama Serangga'},
        'chart_data': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul'],
            'high': [20, 35, 30, 45, 40, 55, 50],
            'medium': [30, 45, 40, 55, 50, 65, 60],
            'low': [40, 55, 50, 65, 60, 75, 70],
        },
        'high_percent': 53.6,
        'medium_percent': 28.6,
        'low_percent': 17.8,
        'current_user': request.user,
    }
    
    return render(request, 'admin_dashboard/dashboard.html', context)


#@login_required
def library_view(request):
    """
    View untuk halaman library pencegahan hama (CRUD)
    """
    pencegahan_list = PencegahanHama.objects.select_related('jenis_hama').all().order_by('-created_at')
    
    context = {
        'pencegahan_list': pencegahan_list,
        'current_user': request.user,
    }
    
    return render(request, 'admin_dashboard/library.html', context)


#@login_required
def library_create(request):
    """
    View untuk tambah data pencegahan hama
    """
    if request.method == 'POST':
        jenis_hama_id = request.POST.get('jenis_hama')
        judul = request.POST.get('judul')
        sumber = request.POST.get('sumber')
        deskripsi = request.POST.get('deskripsi', '')
        
        try:
            jenis_hama = JenisHama.objects.get(id=jenis_hama_id)
            PencegahanHama.objects.create(
                jenis_hama=jenis_hama,
                judul=judul,
                sumber=sumber,
                deskripsi=deskripsi,
            )
            messages.success(request, 'Data pencegahan berhasil ditambahkan!')
            return redirect('admin_dashboard:library')
        except Exception as e:
            messages.error(request, f'Gagal menambahkan data: {str(e)}')
    
    jenis_hama_list = JenisHama.objects.all()
    context = {
        'jenis_hama_list': jenis_hama_list,
        'current_user': request.user,
    }
    
    return render(request, 'admin_dashboard/library_form.html', context)


#@login_required
def library_edit(request, pk):
    """
    View untuk edit data pencegahan hama
    """
    pencegahan = get_object_or_404(PencegahanHama, pk=pk)
    
    if request.method == 'POST':
        jenis_hama_id = request.POST.get('jenis_hama')
        judul = request.POST.get('judul')
        sumber = request.POST.get('sumber')
        deskripsi = request.POST.get('deskripsi', '')
        
        try:
            jenis_hama = JenisHama.objects.get(id=jenis_hama_id)
            pencegahan.jenis_hama = jenis_hama
            pencegahan.judul = judul
            pencegahan.sumber = sumber
            pencegahan.deskripsi = deskripsi
            pencegahan.save()
            
            messages.success(request, 'Data pencegahan berhasil diupdate!')
            return redirect('admin_dashboard:library')
        except Exception as e:
            messages.error(request, f'Gagal mengupdate data: {str(e)}')
    
    jenis_hama_list = JenisHama.objects.all()
    context = {
        'pencegahan': pencegahan,
        'jenis_hama_list': jenis_hama_list,
        'current_user': request.user,
    }
    
    return render(request, 'admin_dashboard/library_form.html', context)


#@login_required
def library_delete(request, pk):
    """
    View untuk hapus data pencegahan hama
    """
    pencegahan = get_object_or_404(PencegahanHama, pk=pk)
    
    if request.method == 'POST':
        try:
            pencegahan.delete()
            messages.success(request, 'Data pencegahan berhasil dihapus!')
        except Exception as e:
            messages.error(request, f'Gagal menghapus data: {str(e)}')
    
    return redirect('admin_dashboard:library')


#@login_required
def library_detail(request, pk):
    """
    View untuk detail data pencegahan hama
    """
    pencegahan = get_object_or_404(PencegahanHama, pk=pk)
    
    context = {
        'pencegahan': pencegahan,
        'current_user': request.user,
    }
    
    return render(request, 'admin_dashboard/library_detail.html', context)
    