# dashboard/models.py

from django.db import models
from accounts.models import Petani  # Import Petani dari accounts

# ============================================
# MODEL LAHAN (Unit Monitoring)
# ============================================
class Lahan(models.Model):
    """
    Lahan/Unit Monitoring milik Petani
    """
    petani = models.ForeignKey(
        Petani,
        on_delete=models.CASCADE,
        related_name='lahan_milik'
    )
    nama_lahan = models.CharField(max_length=100, verbose_name="Nama Unit")
    lokasi = models.CharField(max_length=255, verbose_name="Lokasi")
    luas_daerah = models.CharField(max_length=50, verbose_name="Luas Daerah", help_text="Contoh: 9km atau 2 hektar")
    deskripsi = models.TextField(blank=True, verbose_name="Deskripsi")
    jenis_tanaman = models.CharField(max_length=100, default='Padi', verbose_name="Jenis Tanaman")
    status_aktif = models.BooleanField(default=True, verbose_name="Status Aktif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lahan'
        verbose_name = "Lahan/Unit Monitoring"
        verbose_name_plural = "Lahan/Unit Monitoring"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nama_lahan} - {self.petani.nama_lengkap}"


# ============================================
# MODEL CITRA DAUN (Upload Foto)
# ============================================
class CitraDaun(models.Model):
    """
    Citra/Foto Daun yang diupload Petani untuk deteksi hama
    """
    STATUS_CHOICES = [
        ('pending', 'Menunggu Deteksi'),
        ('processing', 'Sedang Diproses'),
        ('completed', 'Selesai'),
        ('failed', 'Gagal'),
    ]

    petani = models.ForeignKey(
        Petani,
        on_delete=models.CASCADE,
        related_name='citra_upload'
    )
    lahan = models.ForeignKey(
        Lahan,
        on_delete=models.CASCADE,
        related_name='citra_lahan',
        null=True,
        blank=True
    )
    nama_file = models.CharField(max_length=255)
    path_file = models.ImageField(upload_to='citra_daun/%Y/%m/%d/')
    jenis_tanaman = models.CharField(max_length=100, blank=True, verbose_name="Jenis Tanaman")
    status_deteksi = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    waktu_upload = models.DateTimeField(auto_now_add=True)
    waktu_deteksi = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'citra_daun'
        verbose_name = "Citra Daun"
        verbose_name_plural = "Citra Daun"
        ordering = ['-waktu_upload']

    def __str__(self):
        return f"{self.nama_file} - {self.petani.nama_lengkap}"


# ============================================
# MODEL JENIS HAMA (Sudah Ada, Kita Pertahankan)
# ============================================
class JenisHama(models.Model):
    """
    Master Data Jenis Hama
    """
    nama = models.CharField(max_length=100, verbose_name="Nama Hama")
    nama_latin = models.CharField(max_length=150, blank=True, verbose_name="Nama Latin")
    deskripsi = models.TextField(blank=True, verbose_name="Deskripsi")
    gambar = models.ImageField(upload_to='hama/', blank=True, null=True, verbose_name="Gambar Hama")
    gejala = models.TextField(blank=True, verbose_name="Gejala Serangan")
    cara_pencegahan = models.TextField(blank=True, verbose_name="Cara Pencegahan")
    cara_penanganan = models.TextField(blank=True, verbose_name="Cara Penanganan")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'jenis_hama'
        verbose_name = "Jenis Hama"
        verbose_name_plural = "Jenis Hama"
        ordering = ['nama']

    def __str__(self):
        return self.nama


# ============================================
# MODEL HASIL DETEKSI (Update dari Deteksi lama)
# ============================================
class HasilDeteksi(models.Model):
    """
    Hasil deteksi YOLO dari citra daun
    """
    TINGKAT_SERANGAN_CHOICES = [
        ('ringan', 'Ringan'),
        ('sedang', 'Sedang'),
        ('berat', 'Berat'),
    ]

    citra = models.OneToOneField(
        CitraDaun,
        on_delete=models.CASCADE,
        related_name='hasil_deteksi',
        primary_key=True
    )
    jenis_hama = models.ForeignKey(
        JenisHama,
        on_delete=models.CASCADE,
        related_name='deteksi_hama'
    )
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Skor kepercayaan model (0-100)"
    )
    tingkat_serangan = models.CharField(
        max_length=10,
        choices=TINGKAT_SERANGAN_CHOICES,
        null=True,
        blank=True
    )
    jumlah_daun_terinfeksi = models.IntegerField(default=1)
    koordinat_bbox = models.JSONField(
        null=True,
        blank=True,
        help_text="Koordinat bounding box dari YOLO"
    )
    gambar_hasil = models.ImageField(
        upload_to='hasil_deteksi/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text="Gambar dengan bounding box"
    )
    rekomendasi = models.TextField(blank=True, verbose_name="Rekomendasi Penanganan")
    waktu_deteksi = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hasil_deteksi'
        verbose_name = "Hasil Deteksi"
        verbose_name_plural = "Hasil Deteksi"

    def __str__(self):
        return f"{self.jenis_hama.nama} - Confidence: {self.confidence_score}%"


# ============================================
# MODEL RIWAYAT DETEKSI (Log History)
# ============================================
class RiwayatDeteksi(models.Model):
    """
    Log/Riwayat semua deteksi per Petani
    """
    petani = models.ForeignKey(
        Petani,
        on_delete=models.CASCADE,
        related_name='riwayat_deteksi'
    )
    hasil_deteksi = models.ForeignKey(
        HasilDeteksi,
        on_delete=models.CASCADE,
        related_name='riwayat'
    )
    lahan = models.ForeignKey(
        Lahan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    catatan_petani = models.TextField(blank=True, verbose_name="Catatan")
    status_penanganan = models.CharField(
        max_length=20,
        choices=[
            ('belum', 'Belum Ditangani'),
            ('proses', 'Sedang Ditangani'),
            ('selesai', 'Sudah Selesai'),
        ],
        default='belum'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'riwayat_deteksi'
        verbose_name = "Riwayat Deteksi"
        verbose_name_plural = "Riwayat Deteksi"
        ordering = ['-created_at']

    def __str__(self):
        return f"Riwayat {self.petani.nama_lengkap} - {self.created_at.strftime('%Y-%m-%d')}"