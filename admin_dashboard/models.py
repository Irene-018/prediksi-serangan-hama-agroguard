from django.db import models
from django.contrib.auth.models import User

class JenisHama(models.Model):
    """
    Model untuk menyimpan jenis-jenis hama
    """
    nama = models.CharField(max_length=100, verbose_name="Nama Hama")
    deskripsi = models.TextField(verbose_name="Deskripsi")
    gambar = models.ImageField(upload_to='hama/', blank=True, null=True, verbose_name="Gambar Hama")
    jumlah_serangan = models.IntegerField(default=0, verbose_name="Jumlah Serangan")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Jenis Hama"
        verbose_name_plural = "Jenis Hama"
        ordering = ['-jumlah_serangan']
    
    def __str__(self):
        return self.nama


class PencegahanHama(models.Model):
    """
    Model untuk library pencegahan hama
    """
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('pending', 'Pending'),
        ('selesai', 'Selesai'),
    ]
    
    jenis_hama = models.ForeignKey(JenisHama, on_delete=models.CASCADE, verbose_name="Jenis Hama" ,related_name='pencegahan_hama')
    judul = models.CharField(max_length=200, verbose_name="Judul")
    sumber = models.URLField(max_length=500, verbose_name="Sumber")
    deskripsi = models.TextField(blank=True, verbose_name="Deskripsi Lengkap")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif', verbose_name="Status")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Dibuat Oleh")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Pencegahan Hama"
        verbose_name_plural = "Pencegahan Hama"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.jenis_hama.nama} - {self.judul}"


class StatistikHama(models.Model):
    """
    Model untuk statistik serangan hama (untuk chart)
    """
    TINGKAT_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    tanggal = models.DateField(verbose_name="Tanggal")
    tingkat = models.CharField(max_length=20, choices=TINGKAT_CHOICES, verbose_name="Tingkat")
    jumlah = models.IntegerField(verbose_name="Jumlah Kasus")
    keterangan = models.TextField(blank=True, verbose_name="Keterangan")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Statistik Hama"
        verbose_name_plural = "Statistik Hama"
        ordering = ['tanggal']
    
    def __str__(self):
        return f"{self.tanggal} - {self.tingkat}: {self.jumlah}"