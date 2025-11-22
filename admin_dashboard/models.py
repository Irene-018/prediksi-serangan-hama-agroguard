from django.db import models
from django.conf import settings

# ==============================================
# MODEL JENIS HAMA (Admin Dashboard)
# ==============================================
class JenisHama(models.Model):
    """
    Master Data Jenis Hama untuk Admin
    """
    nama = models.CharField(max_length=100, verbose_name="Nama Hama")
<<<<<<< HEAD
    nama_latin = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nama Latin")
    deskripsi = models.TextField(verbose_name="Deskripsi")
    gejala = models.TextField(blank=True, null=True, verbose_name="Gejala Serangan")
=======
    deskripsi = models.TextField(verbose_name="Deskripsi")
>>>>>>> 002ca9f904786c4b20dacc25f539d698733278cc
    gambar = models.ImageField(
        upload_to='hama/', 
        blank=True, 
        null=True, 
        verbose_name="Gambar Hama"
    )
    jumlah_serangan = models.IntegerField(
        default=0, 
        verbose_name="Jumlah Serangan"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'admin_jenis_hama'
        verbose_name = "Jenis Hama"
        verbose_name_plural = "Jenis Hama"
        ordering = ['-jumlah_serangan']
    
    def __str__(self):
        return self.nama


# ==============================================
# MODEL PENCEGAHAN HAMA
# ==============================================
class PencegahanHama(models.Model):
    """
    Library Pencegahan Hama
    """
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('pending', 'Pending'),
        ('selesai', 'Selesai'),
    ]
    
    jenis_hama = models.ForeignKey(
        JenisHama,
        on_delete=models.CASCADE,
        related_name='pencegahan_hama',
        verbose_name="Jenis Hama"
    )
    judul = models.CharField(max_length=200, verbose_name="Judul")
    sumber = models.URLField(max_length=500, verbose_name="Sumber")
    deskripsi = models.TextField(blank=True, verbose_name="Deskripsi Lengkap")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='aktif', 
        verbose_name="Status"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Dibuat Oleh"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pencegahan_hama'
        verbose_name = "Pencegahan Hama"
        verbose_name_plural = "Pencegahan Hama"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.jenis_hama.nama} - {self.judul}"


# ==============================================
# MODEL STATISTIK HAMA
# ==============================================
class StatistikHama(models.Model):
    """
    Statistik Serangan Hama (untuk chart)
    """
    TINGKAT_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    tanggal = models.DateField(verbose_name="Tanggal")
    tingkat = models.CharField(
        max_length=20, 
        choices=TINGKAT_CHOICES, 
        verbose_name="Tingkat"
    )
    jumlah = models.IntegerField(verbose_name="Jumlah Kasus")
    keterangan = models.TextField(blank=True, verbose_name="Keterangan")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'statistik_hama'
        verbose_name = "Statistik Hama"
        verbose_name_plural = "Statistik Hama"
        ordering = ['tanggal']
    
    def __str__(self):
        return f"{self.tanggal} - {self.tingkat}: {self.jumlah}"