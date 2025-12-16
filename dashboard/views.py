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
@api_view(['POST'])
@login_required
def proses_deteksi_ai(request):
    try:
        from .ai_service import pest_ai
        import tempfile
        import os
        
        # Validasi file
        if 'image' not in request.FILES:
            return Response({'success': False, 'error': 'No image'})
        
        image_file = request.FILES['image']
        
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            for chunk in image_file.chunks():
                tmp_file.write(chunk)
            temp_path = tmp_file.name
        
        # AI Prediction saja, TANPA save database dulu
        hasil = pest_ai.predict(temp_path)
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        
        if not hasil.get('success', False):
            return Response({
                'success': False,
                'error': hasil.get('error', 'AI error')
            })
        
        # Return AI result TANPA database saving
        return Response({
            'success': True,
            'prediction': hasil['prediction'],
            'mode': hasil.get('mode', 'development'),
            'note': 'AI prediction successful (database saving skipped for testing)',
            'database_saved': False  # ← Flag bahwa tidak save ke DB
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        })