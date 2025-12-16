# accounts/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Admin, Petani


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal: Otomatis buat profil berdasarkan is_superuser
    - is_superuser = 1 → Buat profil Admin
    - is_superuser = 0 → Buat profil Petani
    """
    if created:  # Hanya saat user baru dibuat
        try:
            if instance.is_superuser:
                # ✅ Superuser → Buat profil Admin
                Admin.objects.create(
                    user=instance,
                    nama_lengkap=instance.first_name or instance.username,
                    divisi='IT'
                )
                print(f"✅ Created Admin profile for: {instance.username}")
                
                # Pastikan role-nya admin
                if instance.role != 'admin':
                    instance.role = 'admin'
                    instance.save(update_fields=['role'])
                    
            else:
                # ✅ User biasa → Buat profil Petani
                Petani.objects.create(
                    user=instance,
                    nama_lengkap=instance.first_name or instance.username,
                    no_handphone='',
                    alamat=''
                )
                print(f"✅ Created Petani profile for: {instance.username}")
                
                # Pastikan role-nya petani
                if instance.role != 'petani':
                    instance.role = 'petani'
                    instance.save(update_fields=['role'])
                    
        except Exception as e:
            print(f"❌ Error creating profile for {instance.username}: {e}")


@receiver(post_save, sender=CustomUser)
def update_user_profile_on_superuser_change(sender, instance, created, **kwargs):
    """
    Signal: Update profil saat is_superuser berubah
    - Jadi superuser → Pindah dari Petani ke Admin
    - Jadi user biasa → Pindah dari Admin ke Petani
    """
    if not created:  # Hanya saat user di-update
        try:
            if instance.is_superuser:
                # ✅ Jadi superuser → Pastikan ada profil Admin
                if not hasattr(instance, 'admin_profile'):
                    # Hapus profil Petani jika ada
                    if hasattr(instance, 'petani_profile'):
                        instance.petani_profile.delete()
                        print(f"🗑️  Deleted Petani profile for: {instance.username}")
                    
                    # Buat profil Admin
                    Admin.objects.create(
                        user=instance,
                        nama_lengkap=instance.first_name or instance.username,
                        divisi='IT'
                    )
                    print(f"✅ Created Admin profile for: {instance.username}")
                
                # Update role
                if instance.role != 'admin':
                    CustomUser.objects.filter(pk=instance.pk).update(role='admin')
                    
            else:
                # ✅ Bukan superuser → Pastikan ada profil Petani
                if not hasattr(instance, 'petani_profile'):
                    # Hapus profil Admin jika ada
                    if hasattr(instance, 'admin_profile'):
                        instance.admin_profile.delete()
                        print(f"🗑️  Deleted Admin profile for: {instance.username}")
                    
                    # Buat profil Petani
                    Petani.objects.create(
                        user=instance,
                        nama_lengkap=instance.first_name or instance.username,
                        no_handphone='',
                        alamat=''
                    )
                    print(f"✅ Created Petani profile for: {instance.username}")
                
                # Update role
                if instance.role != 'petani':
                    CustomUser.objects.filter(pk=instance.pk).update(role='petani')
                    
        except Exception as e:
            print(f"❌ Error updating profile for {instance.username}: {e}")