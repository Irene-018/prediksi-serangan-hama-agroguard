# dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Max, Min
from .models import SensorData
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
    return render(request, 'dashboard/rekomendasi.html')

@login_required(login_url='/accounts/login/')
def riwayat_view(request):
    return render(request, 'dashboard/riwayat.html')

@login_required(login_url='/accounts/login/')
def pengaturan_view(request):
    return render(request, 'dashboard/pengaturan.html')

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
    """Ambil statistik harian"""
    try:
        today = timezone.now().date()
        today_data = SensorData.objects.filter(
            timestamp__date=today
        )
        
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