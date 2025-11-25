from rest_framework import serializers
from .models import SensorData

class SensorDataSerializer(serializers.ModelSerializer):
    """Serializer untuk API Sensor Data"""
    
    class Meta:
        model = SensorData
        fields = ['id', 'device_id', 'temperature', 'humidity', 'timestamp']
        read_only_fields = ['id', 'timestamp']