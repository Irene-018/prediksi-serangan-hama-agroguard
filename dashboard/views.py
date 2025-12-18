# dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Max, Min
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import os
import tempfile
from .models import SensorData, CitraDaun, HasilDeteksi, JenisHama, RiwayatDeteksi, Lahan
from .serializers import SensorDataSerializer
from .ai_service import pest_ai

@login_required(login_url='/accounts/login/')
def dashboard_view(request):
    """Dashboard utama untuk Petani"""
    return render(request, 'dashboard/dashboard.html')

@login_required(login_url='/accounts/login/')
def deteksi_view(request):
    return render(request, 'dashboard/deteksi.html')

@login_required(login_url='/accounts/login/')
def rekomendasi_view(request):
    """
    Halaman rekomendasi treatment berbasis hasil deteksi terakhir milik petani.
    Menggunakan tabel:
    - CitraDaun (citra__petani)
    - HasilDeteksi
    - JenisHama
    """
    hasil_terakhir = None

    if hasattr(request.user, 'petani_profile'):
        petani = request.user.petani_profile
        hasil_terakhir = (
            HasilDeteksi.objects
            .select_related('citra', 'jenis_hama')
            .filter(citra__petani=petani)
            .order_by('-waktu_deteksi')
            .first()
        )

    context = {
        'hasil': hasil_terakhir,
    }
    return render(request, 'dashboard/rekomendasi.html', context)

@login_required(login_url='/accounts/login/')
def recommendation_detail(request, detection_id):
    return render(request, "dashboard/rekomendasi_detail.html", {})

@login_required(login_url='/accounts/login/')
def riwayat_view(request):
    """
    Halaman riwayat deteksi untuk petani (server-side, langsung dari database).
    """
    if not hasattr(request.user, 'petani_profile'):
        # Kalau bukan petani, tampilkan halaman kosong
        return render(request, 'dashboard/riwayat.html', {
            'riwayat_list': [],
            'total_deteksi': 0,
            'total_sakit': 0,
            'perlu_penanganan': 0,
        })

    petani = request.user.petani_profile

    riwayat_qs = (
        RiwayatDeteksi.objects
        .filter(petani=petani)
        .select_related('hasil_deteksi__jenis_hama', 'hasil_deteksi__citra', 'lahan')
        .order_by('-created_at')
    )

    total_deteksi = riwayat_qs.count()
    total_sakit = riwayat_qs.exclude(hasil_deteksi__tingkat_serangan__isnull=True).count()
    perlu_penanganan = riwayat_qs.exclude(status_penanganan='selesai').count()

    context = {
        'riwayat_list': riwayat_qs,
        'total_deteksi': total_deteksi,
        'total_sakit': total_sakit,
        'perlu_penanganan': perlu_penanganan,
    }
    return render(request, 'dashboard/riwayat.html', context)

@login_required(login_url='/accounts/login/')
def pengaturan_view(request):
    """
    Pengaturan akun & unit monitoring:
    - Tab Akun: update nama, email, no HP, dan password user
    - Tab Unit Monitoring: update / buat 1 lahan utama untuk petani
    """
    user = request.user
    petani = getattr(user, 'petani_profile', None)

    # Ambil satu lahan utama (jika ada) untuk form monitoring
    lahan_utama = None
    if petani is not None:
        lahan_utama = (
            Lahan.objects.filter(petani=petani)
            .order_by('-created_at')
            .first()
        )

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        # =====================
        # FORM AKUN
        # =====================
        if form_type == 'account':
            nama = request.POST.get('nama', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            password = request.POST.get('password', '')
            new_password = request.POST.get('newPassword', '')

            # Update nama & kontak
            if petani:
                if nama:
                    petani.nama_lengkap = nama
                petani.no_handphone = phone
                petani.save()
            else:
                # fallback kalau belum punya profil petani
                if nama:
                    user.first_name = nama
                user.no_handphone = phone  # field di CustomUser

            if email:
                user.email = email

            # Ganti password (opsional)
            if new_password:
                if not user.check_password(password):
                    messages.error(request, 'Password saat ini salah, tidak bisa mengganti password.')
                else:
                    user.set_password(new_password)
                    messages.success(request, 'Password berhasil diperbarui.')

            user.save()
            if not messages.get_messages(request):
                messages.success(request, 'Profil berhasil diperbarui.')

            return redirect('dashboard:pengaturan')

        # =====================
        # FORM UNIT MONITORING
        # =====================
        elif form_type == 'monitoring' and petani is not None:
            nama_unit = request.POST.get('nama_unit', '').strip()
            lokasi = request.POST.get('lokasi', '').strip()
            luas_area = request.POST.get('luas_area', '').strip()
            deskripsi = request.POST.get('deskripsi', '').strip()
            foto_unit = request.FILES.get('monitoring_photo')

            if not nama_unit or not lokasi or not luas_area:
                messages.error(request, 'Nama unit, lokasi, dan luas area wajib diisi.')
            else:
                if lahan_utama is None:
                    lahan_utama = Lahan.objects.create(
                        petani=petani,
                        nama_lahan=nama_unit,
                        lokasi=lokasi,
                        luas_daerah=luas_area,
                        deskripsi=deskripsi,
                        jenis_tanaman='Padi',  # default
                        status_aktif=True,
                        foto_unit=foto_unit if foto_unit else None,
                    )
                else:
                    lahan_utama.nama_lahan = nama_unit
                    lahan_utama.lokasi = lokasi
                    lahan_utama.luas_daerah = luas_area
                    lahan_utama.deskripsi = deskripsi
                    if foto_unit:
                        lahan_utama.foto_unit = foto_unit
                    lahan_utama.save()

                messages.success(request, 'Data unit monitoring berhasil disimpan.')

            return redirect('dashboard:pengaturan')

    context = {
        'user_obj': user,
        'petani': petani,
        'lahan_utama': lahan_utama,
    }
    return render(request, 'dashboard/pengaturan.html', context)

@login_required(login_url='/accounts/login/')
def profile_view(request):
    return render(request, 'dashboard/profile.html')


# ========================================
# API ENDPOINTS UNTUK ESP8266
# ========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def receive_sensor_data(request):
    try:
        device_id = request.data.get('device_id', 'ESP8266_001')
        temperature = request.data.get('temperature')
        humidity = request.data.get('humidity')
        soil_moisture = request.data.get('soil_moisture')

        if temperature is None or humidity is None or soil_moisture is None:
            return Response({
                'success': False,
                'error': 'Missing temperature, humidity, or soil_moisture'
            }, status=status.HTTP_400_BAD_REQUEST)

        temp = float(temperature)
        hum = float(humidity)
        soil = int(soil_moisture)

        if not (-40 <= temp <= 80):
            return Response({
                'success': False,
                'error': f'Temperature out of range: {temp}°C'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not (0 <= hum <= 100):
            return Response({
                'success': False,
                'error': f'Humidity out of range: {hum}%'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not (0 <= soil <= 100):
            return Response({
                'success': False,
                'error': f'Soil moisture out of range: {soil}%'
            }, status=status.HTTP_400_BAD_REQUEST)

        sensor_data = SensorData.objects.create(
            device_id=device_id,
            temperature=temp,
            humidity=hum,
            soil_moisture=soil
        )

        serializer = SensorDataSerializer(sensor_data)

        return Response({
            'success': True,
            'message': 'Data received successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_latest_sensor_data(request):
    try:
        latest = SensorData.objects.latest('timestamp')

        return Response({
            'success': True,
            'data': {
                'id': latest.id,
                'device_id': latest.device_id,
                'temperature': float(latest.temperature),
                'humidity': float(latest.humidity),
                'soil_moisture': latest.soil_moisture,
                'timestamp': latest.timestamp.isoformat()
            }
        }, status=200)

    except SensorData.DoesNotExist:
        return Response({
            'success': False,
            'message': 'No data available'
        }, status=200)

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_statistics(request):
    """Ambil statistik harian"""
    try:
        today = timezone.now().date()
        today_data = SensorData.objects.filter(timestamp__date=today)

        if not today_data.exists():
            return Response({
                'success': False,
                'message': 'No data for today'
            }, status=status.HTTP_404_NOT_FOUND)
        
        stats = today_data.aggregate(
            avg_temp=Avg('temperature'),
            max_temp=Max('temperature'),
            min_temp=Min('temperature'),
            avg_humidity=Avg('humidity'),
            max_humidity=Max('humidity'),
            min_humidity=Min('humidity')
        )
        
        return Response({
            'success': True,
            'data': {
                'temperature': {
                    'avg': round(float(stats['avg_temp']), 1),
                    'max': round(float(stats['max_temp']), 1),
                    'min': round(float(stats['min_temp']), 1)
                },
                'humidity': {
                    'avg': round(float(stats['avg_humidity']), 1),
                    'max': round(float(stats['max_humidity']), 1),
                    'min': round(float(stats['min_humidity']), 1)
                },
                'total_readings': today_data.count()
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_sensor_chart_raw(request):
    try:
        import pytz
        from collections import defaultdict
        from django.utils import timezone as django_timezone

        hours = float(request.query_params.get('hours', 1))
        time_now = django_timezone.now()
        time_from = time_now - timedelta(hours=hours)

        queryset = SensorData.objects.filter(
            timestamp__gte=time_from,
            timestamp__lte=time_now
        ).order_by('timestamp')

        if not queryset.exists():
            return Response({
                'success': True,
                'message': 'No data available',
                'data': []
            })

        wib = pytz.timezone('Asia/Jakarta')

        grouped_data = defaultdict(lambda: {
            'temps': [],
            'hums': [],
            'soils': []
        })

        for item in queryset:
            timestamp_wib = item.timestamp.astimezone(wib)
            time_key = timestamp_wib.strftime('%H:%M')

            grouped_data[time_key]['temps'].append(float(item.temperature))
            grouped_data[time_key]['hums'].append(float(item.humidity))
            grouped_data[time_key]['soils'].append(int(item.soil_moisture))

        chart_data = []
        for time_key in sorted(grouped_data.keys()):
            temps = grouped_data[time_key]['temps']
            hums = grouped_data[time_key]['hums']
            soils = grouped_data[time_key]['soils']

            chart_data.append({
                'time': time_key,
                'temperature': round(sum(temps) / len(temps), 1),
                'humidity': round(sum(hums) / len(hums), 1),
                'soil_moisture': round(sum(soils) / len(soils), 1)
            })

        return Response({
            'success': True,
            'count': len(chart_data),
            'time_range': f'Last {hours} hours',
            'data': chart_data
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def test_api(request):
    return Response({
        'success': True,
        'message': 'AgroGuard API is running!',
        'timestamp': timezone.now()
    })

#function_ai
# Di views.py - simple fix untuk testing
# Tambahkan ini ke views.py Anda (replace fungsi proses_deteksi_ai)

@api_view(['POST'])
@login_required
def proses_deteksi_ai(request):
    """
    Proses deteksi AI dengan validasi ketat
    """
    try:
        print("\n" + "="*60)
        print("🚀 AI DETECTION WITH VALIDATION STARTED")
        print("="*60)
        
        # 1. Validasi User & File
        if not hasattr(request.user, 'petani_profile'):
            return Response({
                'success': False,
                'error': 'User tidak memiliki profil petani'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        petani = request.user.petani_profile
        print(f"👤 User: {petani.nama_lengkap}")
        
        if 'image' not in request.FILES:
            return Response({
                'success': False,
                'error': 'Tidak ada file gambar yang diupload',
                'error_type': 'NO_FILE'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        print(f"📷 File: {image_file.name} ({image_file.size} bytes)")
        
        # Validasi tipe file
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
        if image_file.content_type.lower() not in allowed_types:
            return Response({
                'success': False,
                'error': 'Format file tidak didukung. Gunakan JPG atau PNG.',
                'error_type': 'INVALID_FORMAT'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validasi ukuran file (max 10MB)
        if image_file.size > 10 * 1024 * 1024:
            return Response({
                'success': False,
                'error': 'Ukuran file terlalu besar. Maksimal 10MB.',
                'error_type': 'FILE_TOO_LARGE'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. Simpan ke CitraDaun dulu (status: processing)
        citra = CitraDaun.objects.create(
            petani=petani,
            nama_file=image_file.name,
            path_file=image_file,
            jenis_tanaman=request.POST.get('jenis_tanaman', 'Cabai/Tomat'),
            status_deteksi='processing'
        )
        print(f"✅ CitraDaun created: ID={citra.id}")
        
        # 3. Proses AI Prediction dengan Validasi
        temp_path = None
        try:
            # Save to temp file for AI processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                for chunk in image_file.chunks():
                    tmp_file.write(chunk)
                temp_path = tmp_file.name
            
            print(f"🤖 Running AI prediction with validation...")
            hasil_ai = pest_ai.predict(temp_path)
            print(f"📊 AI Result: {hasil_ai}")
            
            # Handle validation/prediction errors
            if not hasil_ai.get('success', False):
                error_type = hasil_ai.get('error_type', 'UNKNOWN_ERROR')
                error_message = hasil_ai.get('error', 'Terjadi kesalahan')
                
                citra.status_deteksi = 'failed'
                citra.save()
                
                print(f"❌ Detection failed: {error_type} - {error_message}")
                
                return Response({
                    'success': False,
                    'error': error_message,
                    'error_type': error_type,
                    'details': hasil_ai.get('details', {}),
                    'suggestion':_get_error_suggestion(error_type)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            prediction = hasil_ai['prediction']
            class_name = prediction['class_name']
            display_name = prediction.get('display_name', class_name)
            confidence = prediction['confidence']
            severity = prediction['severity']
            disease_info = prediction.get('disease_info', {})
            
            # 4. Tentukan apakah sehat atau sakit
            is_healthy = 'healthy' in class_name.lower()
            
            # 5. Cari atau Buat JenisHama
            jenis_hama, created = JenisHama.objects.get_or_create(
                nama=display_name,
                defaults={
                    'nama_latin': disease_info.get('latin_name', '-'),
                    'deskripsi': disease_info.get('description', ''),
                    'gejala': disease_info.get('symptoms', ''),
                    'cara_pencegahan': disease_info.get('prevention', ''),
                    'cara_penanganan': disease_info.get('treatment', '')
                }
            )
            
            if created:
                print(f"🆕 JenisHama baru dibuat: {display_name}")
            else:
                print(f"♻️ Menggunakan JenisHama existing: {display_name}")
            
            # 6. Simpan HasilDeteksi
            tingkat_mapping = {
                'Rendah': 'ringan',
                'Sedang': 'sedang',
                'Tinggi': 'berat'
            }
            tingkat_serangan = tingkat_mapping.get(severity, 'sedang')
            
            # Generate rekomendasi
            if is_healthy:
                rekomendasi = disease_info.get('treatment', 
                    "✅ Tanaman dalam kondisi sehat. Lanjutkan perawatan rutin dan monitoring berkala.")
            else:
                base_recommendation = disease_info.get('treatment', '')
                
                if severity == 'Tinggi':
                    urgency = "⚠️ SEGERA TANGANI! "
                elif severity == 'Sedang':
                    urgency = "⚠️ Perlu Perhatian. "
                else:
                    urgency = "ℹ️ Monitoring Diperlukan. "
                
                rekomendasi = urgency + base_recommendation
            
            hasil_deteksi = HasilDeteksi.objects.create(
                citra=citra,
                jenis_hama=jenis_hama,
                confidence_score=confidence,
                tingkat_serangan=tingkat_serangan if not is_healthy else 'ringan',
                jumlah_daun_terinfeksi=1 if not is_healthy else 0,
                rekomendasi=rekomendasi,
                waktu_deteksi=timezone.now()
            )
            print(f"✅ HasilDeteksi created: Confidence={confidence}%, Severity={severity}")
            
            # 7. Update status CitraDaun
            citra.status_deteksi = 'completed'
            citra.waktu_deteksi = timezone.now()
            citra.save()
            
            # 8. Buat RiwayatDeteksi
            lahan_id = request.POST.get('lahan_id', None)
            lahan = None
            if lahan_id:
                try:
                    lahan = Lahan.objects.get(id=lahan_id, petani=petani)
                except Lahan.DoesNotExist:
                    pass
            
            riwayat = RiwayatDeteksi.objects.create(
                petani=petani,
                hasil_deteksi=hasil_deteksi,
                lahan=lahan,
                catatan_petani='',
                status_penanganan='belum' if not is_healthy else 'selesai'
            )
            print(f"✅ RiwayatDeteksi created: ID={riwayat.id}")
            
            print("="*60)
            print("✅ AI DETECTION COMPLETED & SAVED TO DATABASE")
            print("="*60 + "\n")
            
            # 9. Return response lengkap dengan info penyakit
            return Response({
                'success': True,
                'message': 'Deteksi berhasil',
                'database_saved': True,
                'data': {
                    'citra_id': citra.id,
                    'hasil_deteksi_id': hasil_deteksi.citra_id,
                    'riwayat_id': riwayat.id
                },
                'prediction': {
                    'class_name': class_name,
                    'display_name': display_name,
                    'pest_name': display_name,
                    'confidence': confidence,
                    'severity': severity,
                    'disease_info': {
                        'description': disease_info.get('description', ''),
                        'symptoms': disease_info.get('symptoms', ''),
                        'prevention': disease_info.get('prevention', ''),
                        'treatment': disease_info.get('treatment', ''),
                        'latin_name': disease_info.get('latin_name', '')
                    }
                },
                'condition': 'SEHAT' if is_healthy else 'TERDETEKSI PENYAKIT',
                'is_healthy': is_healthy,
                'validation': hasil_ai.get('validation', {}),
                'mode': hasil_ai.get('mode', 'production'),
                'note': hasil_ai.get('note', '')
            })
            
        finally:
            # Cleanup temp file
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
                print("🗑️ Temp file cleaned up")
        
    except Exception as e:
        print(f"❌ ERROR in proses_deteksi_ai: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Update status jika ada error
        if 'citra' in locals():
            citra.status_deteksi = 'failed'
            citra.save()
        
        return Response({
            'success': False,
            'error': 'Terjadi kesalahan sistem. Silakan coba lagi.',
            'error_type': 'SYSTEM_ERROR',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _get_error_suggestion(error_type):
    """Berikan saran berdasarkan tipe error"""
    suggestions = {
        'VALIDATION_FAILED': 'Pastikan foto menampilkan daun cabai atau tomat dengan jelas, pencahayaan cukup, dan tidak blur.',
        'LOW_CONFIDENCE': 'Coba ambil foto yang lebih jelas dengan fokus pada satu daun saja.',
        'NO_FILE': 'Pilih file gambar terlebih dahulu sebelum melakukan deteksi.',
        'INVALID_FORMAT': 'Gunakan format gambar JPG atau PNG.',
        'FILE_TOO_LARGE': 'Kompres gambar Anda hingga ukurannya di bawah 10MB.',
        'SYSTEM_ERROR': 'Terjadi kesalahan sistem. Hubungi administrator jika masalah berlanjut.'
    }
    return suggestions.get(error_type, 'Silakan coba lagi atau hubungi administrator.')