from django.db import models

class PencegahanHama(models.Model):
    jenis_hama = models.CharField(max_length=100)
    judul = models.CharField(max_length=200)
    sumber = models.CharField(max_length=200)
    deskripsi = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.judul
