# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    """Custom manager untuk CustomUser"""
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        """Membuat dan menyimpan User biasa"""
        if not username:
            raise ValueError('Username harus diisi')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Membuat dan menyimpan Superuser dengan role admin"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser harus memiliki is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser harus memiliki is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)


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
    
    objects = CustomUserManager()  # ✅ Gunakan custom manager

    class Meta:
        db_table = 'accounts_customuser'

    def __str__(self):
        return f"{self.username} ({'Admin' if self.is_superuser else 'Petani'})"


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
    divisi = models.CharField(max_length=50, blank=True, default='IT')

    class Meta:
        db_table = 'admin'

    def __str__(self):
        return f"Admin: {self.nama_lengkap}"