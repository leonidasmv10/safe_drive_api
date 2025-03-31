from rest_framework import serializers
from .models import VisualDetection, Location, AudioDetection

class VisualDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisualDetection
        fields = ['id', 'user', 'vehicle_type', 'frequency', 'detection_date']
        read_only_fields = ['user', 'detection_date']
    
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'user', 'latitud', 'longitud', 'date']

class AudioDetectionSerializer(serializers.ModelSerializer):
    location = LocationSerializer()

    class Meta:
        model = AudioDetection
        fields = ['id', 'user', 'sound_type', 'location', 'detection_date']