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
    """
    Dashboard utama untuk Petani.
    Template akan mengambil data sensor lewat endpoint API
    sehingga di sini kita cukup me-render template.
    """
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
    """Endpoint untuk terima data dari ESP8266"""
    try:
        device_id = request.data.get('device_id', 'ESP8266_001')
        temperature = request.data.get('temperature')
        humidity = request.data.get('humidity')
        
        if temperature is None or humidity is None:
            return Response({
                'success': False,
                'error': 'Missing temperature or humidity'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        temp = float(temperature)
        hum = float(humidity)
        
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
        
        sensor_data = SensorData.objects.create(
            device_id=device_id,
            temperature=temperature,
            humidity=humidity
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
    """Ambil data sensor terbaru (1 data terakhir)"""
    try:
        sensor_data = SensorData.objects.latest('timestamp')
        serializer = SensorDataSerializer(sensor_data)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
        
    except SensorData.DoesNotExist:
        return Response({
            'success': False,
            'message': 'No data available'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sensor_history(request):
    """Ambil riwayat data sensor untuk grafik (24 jam terakhir)"""
    try:
        from django.utils import timezone
        import pytz
        
        hours = int(request.query_params.get('hours', 24))
        time_from = timezone.now() - timedelta(hours=hours)
        
        # Get all data from last X hours
        queryset = SensorData.objects.filter(
            timestamp__gte=time_from
        ).order_by('timestamp')
        
        if not queryset.exists():
            return Response({
                'success': True,
                'message': 'No data in specified time range',
                'data': []
            })
        
        # Convert to WIB timezone
        wib = pytz.timezone('Asia/Jakarta')
        
        # Group data by hour
        chart_data = []
        current_hour = None
        temp_list = []
        humidity_list = []
        
        for item in queryset:
            # Convert UTC to WIB
            timestamp_wib = item.timestamp.astimezone(wib)
            hour_label = timestamp_wib.strftime('%H:%M')  # Changed to HH:MM for more detail
            
            if current_hour != hour_label:
                # Save previous hour data
                if current_hour is not None and temp_list:
                    chart_data.append({
                        'time': current_hour,
                        'temperature': round(sum(temp_list) / len(temp_list), 1),
                        'humidity': round(sum(humidity_list) / len(humidity_list), 1)
                    })
                
                # Start new hour
                current_hour = hour_label
                temp_list = [float(item.temperature)]
                humidity_list = [float(item.humidity)]
            else:
                temp_list.append(float(item.temperature))
                humidity_list.append(float(item.humidity))
        
        # Don't forget last group
        if current_hour is not None and temp_list:
            chart_data.append({
                'time': current_hour,
                'temperature': round(sum(temp_list) / len(temp_list), 1),
                'humidity': round(sum(humidity_list) / len(humidity_list), 1)
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
@permission_classes([AllowAny])
def get_statistics(request):
    """
    Ambil statistik harian untuk kartu di dashboard.
    Response disesuaikan dengan struktur yang di-consume oleh dashboard.html.
    """
    try:
        today = timezone.now().date()
        today_data = SensorData.objects.filter(timestamp__date=today)

        if not today_data.exists():
            return Response(
                {
                    'success': False,
                    'message': 'No data for today',
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        stats = today_data.aggregate(
            avg_temp=Avg('temperature'),
            max_temp=Max('temperature'),
            min_temp=Min('temperature'),
            avg_humidity=Avg('humidity'),
            max_humidity=Max('humidity'),
            min_humidity=Min('humidity'),
        )

        avg_humidity = float(stats['avg_humidity'])
        total_readings = today_data.count()

        # Sederhana: anggap "alerts" = jumlah pembacaan di luar range ideal 60–80%
        alerts = today_data.filter(
            humidity__lt=60
        ).count() + today_data.filter(humidity__gt=80).count()

        return Response(
            {
                'success': True,
                'data': {
                    # Field-field yang dipakai di dashboard.js
                    'total_records': total_readings,
                    'alerts': alerts,
                    'avg_humidity': avg_humidity,
                    # Detail tambahan kalau dibutuhkan di masa depan
                    'temperature': {
                        'avg': round(float(stats['avg_temp']), 1),
                        'max': round(float(stats['max_temp']), 1),
                        'min': round(float(stats['min_temp']), 1),
                    },
                    'humidity': {
                        'avg': round(avg_humidity, 1),
                        'max': round(float(stats['max_humidity']), 1),
                        'min': round(float(stats['min_humidity']), 1),
                    },
                    'total_readings': total_readings,
                },
            }
        )
    except Exception as e:
        return Response(
            {
                'success': False,
                'error': str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_sensor_chart_raw(request):
    """Ambil data sensor untuk chart (grouped by minute)"""
    try:
        import pytz
        from collections import defaultdict
        from django.utils import timezone as django_timezone
        
        hours = float(request.query_params.get('hours', 1))
        
        # PENTING: Gunakan timezone.now() untuk waktu sekarang
        time_now = django_timezone.now()
        time_from = time_now - timedelta(hours=hours)
        
        # DEBUG LOG
        print(f"\n{'='*50}")
        print(f"🔍 DEBUG get_sensor_chart_raw")
        print(f"{'='*50}")
        print(f"Time now (UTC):  {time_now}")
        print(f"Time from (UTC): {time_from}")
        print(f"Hours parameter: {hours}")
        
        # Get all data from time_from to now
        queryset = SensorData.objects.filter(
            timestamp__gte=time_from,
            timestamp__lte=time_now  # ← TAMBAH INI!
        ).order_by('timestamp')
        
        total_count = queryset.count()
        print(f"Total records found: {total_count}")
        
        if not queryset.exists():
            print("❌ No data found in range!")
            return Response({
                'success': True,
                'message': 'No data available',
                'data': []
            })
        
        # Show first and last record timestamps
        first_record = queryset.first()
        last_record = queryset.last()
        print(f"First record: {first_record.timestamp}")
        print(f"Last record:  {last_record.timestamp}")
        
        # Convert to WIB timezone
        wib = pytz.timezone('Asia/Jakarta')
        
        # Group by minute
        grouped_data = defaultdict(lambda: {'temps': [], 'hums': []})
        
        for item in queryset:
            timestamp_wib = item.timestamp.astimezone(wib)
            time_key = timestamp_wib.strftime('%H:%M')
            
            grouped_data[time_key]['temps'].append(float(item.temperature))
            grouped_data[time_key]['hums'].append(float(item.humidity))
        
        # Calculate average for each minute
        chart_data = []
        for time_key in sorted(grouped_data.keys()):
            temps = grouped_data[time_key]['temps']
            hums = grouped_data[time_key]['hums']
            
            chart_data.append({
                'time': time_key,
                'temperature': round(sum(temps) / len(temps), 1),
                'humidity': round(sum(hums) / len(hums), 1)
            })
        
        print(f"Grouped into {len(chart_data)} data points")
        if chart_data:
            print(f"First time: {chart_data[0]['time']}")
            print(f"Last time:  {chart_data[-1]['time']}")
        print(f"{'='*50}\n")
        
        return Response({
            'success': True,
            'count': len(chart_data),
            'time_range': f'Last {hours} hours',
            'data': chart_data
        })
        
    except Exception as e:
        print(f"❌ ERROR in get_sensor_chart_raw: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def test_api(request):
    """Test endpoint"""
    return Response({
        'success': True,
        'message': 'AgroGuard API is running!',
        'timestamp': timezone.now()
    })


# ========================================
# 🔥 AI DETECTION WITH DATABASE SAVING
# ========================================

@api_view(['POST'])
@login_required
def proses_deteksi_ai(request):
    """
    Proses deteksi AI dengan penyimpanan ke database
    Flow:
    1. Upload foto → CitraDaun
    2. AI Prediction → HasilDeteksi
    3. Log History → RiwayatDeteksi
    """
    try:
        print("\n" + "="*60)
        print("🚀 AI DETECTION STARTED")
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
                'error': 'Tidak ada file gambar yang diupload'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        print(f"📷 File: {image_file.name} ({image_file.size} bytes)")
        
        # 2. Simpan ke CitraDaun dulu (status: pending)
        citra = CitraDaun.objects.create(
            petani=petani,
            nama_file=image_file.name,
            path_file=image_file,
            jenis_tanaman=request.POST.get('jenis_tanaman', 'Cabai'),
            status_deteksi='processing'
        )
        print(f"✅ CitraDaun created: ID={citra.id}")
        
        # 3. Proses AI Prediction
        temp_path = None
        try:
            # Save to temp file for AI processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                for chunk in image_file.chunks():
                    tmp_file.write(chunk)
                temp_path = tmp_file.name
            
            print(f"🤖 Running AI prediction...")
            hasil_ai = pest_ai.predict(temp_path)
            print(f"📊 AI Result: {hasil_ai}")
            
            if not hasil_ai.get('success', False):
                citra.status_deteksi = 'failed'
                citra.save()
                return Response({
                    'success': False,
                    'error': hasil_ai.get('error', 'AI prediction failed')
                })
            
            prediction = hasil_ai['prediction']
            class_name = prediction['class_name']
            confidence = prediction['confidence']
            severity = prediction['severity']
            
            # 4. Cari atau Buat JenisHama
            # Mapping class_name ke database
            hama_mapping = {
                'hama': 'Hama Terdeteksi',
                'sehat': 'Tidak ada tanda Penyakit atau Hama'
            }
            
            nama_hama = hama_mapping.get(class_name.lower(), class_name)
            
            jenis_hama, created = JenisHama.objects.get_or_create(
                nama=nama_hama,
                defaults={
                    'nama_latin': f'{class_name.title()}',
                    'deskripsi': f'Deteksi otomatis dari AI: {class_name}',
                    'gejala': 'Terdeteksi melalui analisis citra AI',
                    'cara_pencegahan': 'Lakukan monitoring rutin',
                    'cara_penanganan': 'Konsultasikan dengan ahli pertanian'
                }
            )
            
            if created:
                print(f"🆕 JenisHama baru dibuat: {nama_hama}")
            else:
                print(f"♻️ Menggunakan JenisHama existing: {nama_hama}")
            
            # 5. Simpan HasilDeteksi
            # Map severity ke tingkat_serangan
            tingkat_mapping = {
                'Rendah': 'ringan',
                'Sedang': 'sedang',
                'Tinggi': 'berat'
            }
            tingkat_serangan = tingkat_mapping.get(severity, 'sedang')
            
            # Generate rekomendasi berdasarkan hasil
            if class_name.lower() == 'sehat':
                rekomendasi = "✅ Tanaman dalam kondisi sehat. Lanjutkan perawatan rutin dan monitoring berkala."
            else:
                rekomendasi = f"⚠️ Terdeteksi serangan hama dengan tingkat keparahan {severity}. "
                if severity == 'Tinggi':
                    rekomendasi += "Segera lakukan tindakan pengendalian dan konsultasi dengan ahli."
                elif severity == 'Sedang':
                    rekomendasi += "Lakukan monitoring lebih intensif dan siapkan tindakan pencegahan."
                else:
                    rekomendasi += "Tingkatkan monitoring dan terapkan pencegahan standar."
            
            hasil_deteksi = HasilDeteksi.objects.create(
                citra=citra,
                jenis_hama=jenis_hama,
                confidence_score=confidence,
                tingkat_serangan=tingkat_serangan,
                jumlah_daun_terinfeksi=1,
                rekomendasi=rekomendasi,
                waktu_deteksi=timezone.now()
            )
            print(f"✅ HasilDeteksi created: Confidence={confidence}%, Severity={severity}")
            
            # 6. Update status CitraDaun
            citra.status_deteksi = 'completed'
            citra.waktu_deteksi = timezone.now()
            citra.save()
            
            # 7. Buat RiwayatDeteksi (optional - bisa ambil lahan dari request)
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
                status_penanganan='belum'
            )
            print(f"✅ RiwayatDeteksi created: ID={riwayat.id}")
            
            print("="*60)
            print("✅ AI DETECTION COMPLETED & SAVED TO DATABASE")
            print("="*60 + "\n")
            
            # 8. Return response lengkap
            return Response({
                'success': True,
                'message': 'Deteksi berhasil dan tersimpan ke database',
                'database_saved': True,
                'data': {
                    'citra_id': citra.id,
                    'hasil_deteksi_id': hasil_deteksi.citra_id,
                    'riwayat_id': riwayat.id
                },
                'prediction': {
                    'class_name': class_name,
                    'pest_name': nama_hama,
                    'confidence': confidence,
                    'severity': severity
                },
                'condition': 'SEHAT' if class_name.lower() == 'sehat' else 'HAMA TERDETEKSI',
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
            'error': f'Terjadi kesalahan: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========================================
# API UNTUK MENGAMBIL RIWAYAT DETEKSI
# ========================================

@api_view(['GET'])
@login_required
def get_detection_history(request):
    """Ambil riwayat deteksi user"""
    try:
        if not hasattr(request.user, 'petani_profile'):
            return Response({
                'success': False,
                'error': 'User tidak memiliki profil petani'
            })
        
        petani = request.user.petani_profile
        
        # Ambil semua riwayat deteksi
        riwayat = RiwayatDeteksi.objects.filter(
            petani=petani
        ).select_related(
            'hasil_deteksi__jenis_hama',
            'hasil_deteksi__citra',
            'lahan'
        ).order_by('-created_at')[:10]  # 10 terbaru
        
        data = []
        for r in riwayat:
            hasil = r.hasil_deteksi
            data.append({
                'id': r.id,
                'tanggal': r.created_at.strftime('%Y-%m-%d %H:%M'),
                'gambar': hasil.citra.path_file.url if hasil.citra.path_file else None,
                'jenis_hama': hasil.jenis_hama.nama,
                'confidence': float(hasil.confidence_score),
                'tingkat_serangan': hasil.tingkat_serangan,
                'status_penanganan': r.status_penanganan,
                'lahan': r.lahan.nama_lahan if r.lahan else 'Tidak ada lahan'
            })
        
        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        })


@api_view(['GET'])
@login_required
def get_detection_statistics(request):
    """
    Ambil statistik deteksi AI untuk petani yang login.
    Menghitung dari tabel HasilDeteksi dan RiwayatDeteksi.
    """
    try:
        if not hasattr(request.user, 'petani_profile'):
            return Response({
                'success': False,
                'error': 'User tidak memiliki profil petani'
            })
        
        petani = request.user.petani_profile
        today = timezone.now().date()
        
        # Total deteksi (semua waktu)
        total_deteksi = HasilDeteksi.objects.filter(
            citra__petani=petani
        ).count()
        
        # Total deteksi hari ini
        deteksi_hari_ini = HasilDeteksi.objects.filter(
            citra__petani=petani,
            waktu_deteksi__date=today
        ).count()
        
        # Hama terdeteksi (yang bukan "sehat")
        hama_terdeteksi = HasilDeteksi.objects.filter(
            citra__petani=petani
        ).exclude(
            jenis_hama__nama__icontains='sehat'
        ).exclude(
            jenis_hama__nama__icontains='tidak ada'
        ).count()
        
        # Hama terdeteksi hari ini
        hama_hari_ini = HasilDeteksi.objects.filter(
            citra__petani=petani,
            waktu_deteksi__date=today
        ).exclude(
            jenis_hama__nama__icontains='sehat'
        ).exclude(
            jenis_hama__nama__icontains='tidak ada'
        ).count()
        
        return Response({
            'success': True,
            'data': {
                'total_deteksi': total_deteksi,
                'deteksi_hari_ini': deteksi_hari_ini,
                'hama_terdeteksi': hama_terdeteksi,
                'hama_hari_ini': hama_hari_ini,
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)