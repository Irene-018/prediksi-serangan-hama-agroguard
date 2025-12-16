# dashboard/serializers.py

from rest_framework import serializers
from .models import SensorData

class SensorDataSerializer(serializers.ModelSerializer):
    """Serializer untuk API Sensor Data dengan 3 sensor"""
    
    # Tambahkan computed fields untuk status tanah
    soil_status = serializers.SerializerMethodField()
    soil_status_color = serializers.SerializerMethodField()
    
    class Meta:
        model = SensorData
        fields = [
            'id', 
            'device_id', 
            'temperature', 
            'humidity', 
            'soil_moisture',        # ← TAMBAHAN BARU
            'soil_status',          # ← Status tanah (computed)
            'soil_status_color',    # ← Warna untuk UI (computed)
            'timestamp'
        ]
        read_only_fields = ['id', 'timestamp', 'soil_status', 'soil_status_color']
    
    def get_soil_status(self, obj):
        """Get human-readable soil moisture status"""
        if hasattr(obj, 'get_soil_status'):
            return obj.get_soil_status()
        return '-'
    
    def get_soil_status_color(self, obj):
        """Get color code for UI"""
        if hasattr(obj, 'get_soil_status_color'):
            return obj.get_soil_status_color()
        return '#666666'
    
    def validate_temperature(self, value):
        """Validasi suhu (-50°C s/d 100°C)"""
        if value < -50 or value > 100:
            raise serializers.ValidationError(
                "Suhu harus antara -50°C hingga 100°C"
            )
        return value
    
    def validate_humidity(self, value):
        """Validasi kelembapan udara (0-100%)"""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Kelembapan udara harus antara 0% hingga 100%"
            )
        return value
    
    def validate_soil_moisture(self, value):
        """Validasi kelembapan tanah (0-100%)"""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Kelembapan tanah harus antara 0% hingga 100%"
            )
        return value
    
    def to_representation(self, instance):
        """Custom representation untuk format yang lebih baik"""
        data = super().to_representation(instance)
        
        # Format timestamp untuk Indonesia
        if instance.timestamp:
            data['timestamp_formatted'] = instance.timestamp.strftime('%d %b %Y, %H:%M:%S')
        
        return data