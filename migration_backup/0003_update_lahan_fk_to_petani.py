from django.db import migrations
from django.db.models import F

def copy_fk_data(apps, schema_editor):
    """Copy user_id ke petani_id"""
    Lahan = apps.get_model('dashboard', 'Lahan')
    
    # Update semua baris yang punya user_id
    updated = Lahan.objects.filter(user__isnull=False).update(petani=F('user'))
    print(f"✅ Updated {updated} rows: user_id → petani_id")

def reverse_copy_fk_data(apps, schema_editor):
    """Rollback: kosongkan petani_id"""
    Lahan = apps.get_model('dashboard', 'Lahan')
    Lahan.objects.update(petani=None)
    print("🔙 Rollback: Set all petani_id to NULL")

class Migration(migrations.Migration):
    dependencies = [
        ('dashboard', '0004_lahan_petani'),  # Sesuaikan dengan nomor migration sebelumnya
        ('accounts', '0002_migrate_users_to_isa'),
    ]
    
    operations = [
        migrations.RunPython(copy_fk_data, reverse_copy_fk_data),
    ]