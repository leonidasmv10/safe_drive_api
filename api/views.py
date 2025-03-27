from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

# profiles/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

@login_required
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Se encarga de crear el usuario con contraseña encriptada
        user = User.objects.create_user(**validated_data)
        return user

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Anidamos el usuario

    class Meta:
        model = Profile
        fields = ['user', 'full_name', 'phone_number', 'preferred_alert_type', 'vehicle_type', 'suscription']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer().create(user_data)
        profile = Profile.objects.create(user=user, **validated_data)
        return profile
