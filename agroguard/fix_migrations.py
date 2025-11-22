import os
import django
import shutil
import sqlite3
from pathlib import Path

# === CONFIG ===
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db.sqlite3"  # sesuaikan jika pakai MySQL (lewati hapus DB)
APPS = ["accounts", "admin_dashboard", "dashboard"]

print("🔧 Memulai perbaikan migrasi Django...\n")

# === 1️⃣ Hapus folder migrasi lama ===
for app in APPS:
    mig_dir = BASE_DIR / app / "migrations"
    if mig_dir.exists():
        for file in mig_dir.iterdir():
            if file.name != "__init__.py":
                file.unlink()
        print(f"🧹 Migrasi lama di {app}/migrations dibersihkan.")
    else:
        print(f"⚠️ Folder {app}/migrations tidak ditemukan.")

# === 2️⃣ Hapus isi tabel django_migrations (khusus SQLite) ===
if DB_PATH.exists():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM django_migrations;")
        conn.commit()
        print("🗑️ Isi tabel 'django_migrations' telah dihapus.")
    except Exception as e:
        print(f"⚠️ Gagal menghapus isi tabel django_migrations: {e}")
    conn.close()
else:
    print("⚠️ Database SQLite tidak ditemukan, lewati langkah ini.")

# === 3️⃣ Buat ulang migrasi ===
os.system("python manage.py makemigrations accounts")
os.system("python manage.py makemigrations admin_dashboard")
os.system("python manage.py makemigrations dashboard")

# === 4️⃣ Jalankan migrate bersih ===
os.system("python manage.py migrate --fake-initial")

print("\n✅ Semua migrasi telah diperbaiki!")
print("Sekarang jalankan: python manage.py runserver")
