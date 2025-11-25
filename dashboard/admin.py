from django.contrib import admin
from .models import SensorData  # ← Tambahkan ini

# ========================================
# ADMIN: SENSOR DATA
# ========================================
@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'temperature', 'humidity', 'timestamp']
    list_filter = ['device_id', 'timestamp']
    search_fields = ['device_id']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
