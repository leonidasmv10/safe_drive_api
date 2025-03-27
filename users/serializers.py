from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['full_name', 'phone_number', 'preferred_alert_type', 'vehicle_type', 'suscription']

class RegisterSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()  # anidado

    class Meta:
        model = User
        fields = ['username', 'password', 'profile']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()

        Profile.objects.create(
            user=user,
            **profile_data
        )

        return user
