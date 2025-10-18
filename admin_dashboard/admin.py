from django.contrib import admin
from .models import JenisHama, PencegahanHama, StatistikHama

@admin.register(JenisHama)
class JenisHamaAdmin(admin.ModelAdmin):
    list_display = ['nama', 'jumlah_serangan', 'created_at']
    list_filter = ['created_at']
    search_fields = ['nama', 'deskripsi']
    ordering = ['-jumlah_serangan']

@admin.register(PencegahanHama)
class PencegahanHamaAdmin(admin.ModelAdmin):
    list_display = ['judul', 'jenis_hama', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'jenis_hama', 'created_at']
    search_fields = ['judul', 'deskripsi', 'sumber']
    ordering = ['-created_at']

@admin.register(StatistikHama)
class StatistikHamaAdmin(admin.ModelAdmin):
    list_display = ['tanggal', 'tingkat', 'jumlah', 'created_at']
    list_filter = ['tingkat', 'tanggal']
    ordering = ['-tanggal']