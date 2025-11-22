from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Petani, Admin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Konfigurasi tampilan model CustomUser di Django Admin."""

    list_display = ['username', 'email', 'role', 'is_staff', 'get_profile_status']
    list_filter = ['role', 'is_staff']

    def get_profile_status(self, obj):
        """
        Menampilkan status apakah user sudah memiliki profil Petani/Admin.
        """
        if hasattr(obj, 'petani_profile'):
            return '✅ Profil Petani Ada'
        elif hasattr(obj, 'admin_profile'):
            return '✅ Profil Admin Ada'
        return '⚠️ Belum ada profil'

    get_profile_status.short_description = 'Status Profil IS-A'


@admin.register(Petani)
class PetaniAdmin(admin.ModelAdmin):
    """Konfigurasi tampilan model Petani di Django Admin."""

    list_display = ['nama_lengkap', 'get_username', 'no_handphone', 'jumlah_lahan']
    search_fields = ['nama_lengkap', 'user__username']

    def get_username(self, obj):
        """Menampilkan username user yang terhubung ke Petani."""
        return obj.user.username

    get_username.short_description = 'Username'

    def jumlah_lahan(self, obj):
        """Menghitung jumlah lahan yang dimiliki Petani."""
        return obj.lahan_milik.count()

    jumlah_lahan.short_description = 'Jumlah Lahan'


@admin.register(Admin)
class AdminModelAdmin(admin.ModelAdmin):
    """Konfigurasi tampilan model Admin di Django Admin."""

    list_display = ['nama_lengkap', 'get_username', 'divisi']
    search_fields = ['nama_lengkap', 'user__username']

    def get_username(self, obj):
        """Menampilkan username user yang terhubung ke Admin."""
        return obj.user.username

    get_username.short_description = 'Username'
