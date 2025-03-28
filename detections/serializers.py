from rest_framework import serializers
from .models import VisualDetection

class VisualDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisualDetection
        fields = ['id', 'user', 'vehicle_type', 'frequency', 'detection_date']
        read_only_fields = ['user', 'detection_date']


# class AudioDetectionSerializer(serializers.ModelSerializer):
#     sound_type = SoundTypeSerializer()
#     location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())
#     class Meta:
#         model = AudioDetection
#         fields = ['id', 'user', 'sound_type', 'location', 'detection_date']

#     def create(self, validated_data):
#         user = self.context['request'].user
#         validated_data['user'] = user
#         return super().create(validated_data)