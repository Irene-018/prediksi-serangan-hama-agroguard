# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Supertype - tetap pakai role untuk backward compatibility
    """
    role = models.CharField(
        max_length=10,
        choices=[('petani', 'Petani'), ('admin', 'Admin')],
        default='petani'
    )
    # Field lama (akan deprecated nanti)
    nama = models.CharField(max_length=100, blank=True)
    no_handphone = models.CharField(max_length=15, blank=True)

    class Meta:
        db_table = 'accounts_customuser'

    def __str__(self):
        return self.username


class Petani(models.Model):
    """Subtype: Petani IS-A CustomUser"""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='petani_profile'
    )
    nama_lengkap = models.CharField(max_length=100)
    no_handphone = models.CharField(max_length=15, blank=True)
    alamat = models.TextField(blank=True)

    class Meta:
        db_table = 'petani'

    def __str__(self):
        return f"{self.nama_lengkap} ({self.user.username})"


class Admin(models.Model):
    """Subtype: Admin IS-A CustomUser"""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='admin_profile'
    )
    nama_lengkap = models.CharField(max_length=100)
    divisi = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'admin'

    def __str__(self):
        return f"Admin: {self.nama_lengkap}"
