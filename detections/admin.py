from django.contrib import admin
from .models import VisualDetection

@admin.register(VisualDetection)
class VisualDetectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'vehicle_type', 'frequency', 'detection_date')
    list_filter = ('vehicle_type', 'detection_date')
    search_fields = ('user__username', 'vehicle_type__type_name')
    ordering = ('-detection_date',)
