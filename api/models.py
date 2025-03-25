from django.db import models
from django.contrib.auth.models import User

# Enumeraciones
ALERT_TYPE_CHOICES = [('visual', 'Visual'), ('audio', 'Audio'), ('vibration', 'Vibration')]
VEHICLE_TYPE_CHOICES = [('car', 'Car'), ('motorcycle', 'Motorcycle'), ('bicycle', 'Bicycle'), ('truck', 'Truck')]
SUSCRIPTION_CHOICES = [('free', 'Free'), ('', 'None')]
STATUS_CHOICES = [('normal', 'Normal'), ('warning', 'Warning'), ('critical', 'Critical')]


# Perfil
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    preferred_alert_type = models.CharField(max_length=10, choices=ALERT_TYPE_CHOICES, default='visual')
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES, default='car')
    suscription = models.CharField(max_length=10, choices=SUSCRIPTION_CHOICES, default='free')

# Historial de conducción
class DrivingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    avg_speed = models.DecimalField(max_digits=6, decimal_places=2)
    total_hard_brakes = models.IntegerField()
    total_horns = models.IntegerField()
    total_sirens = models.IntegerField()
    registration_date = models.DateTimeField(auto_now_add=True)

# Tipos de sonido
class SoundType(models.Model):
    type_name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

# Ubicación
class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitud = models.FloatField()
    longitud = models.FloatField()
    date = models.DateTimeField()

# Detección de audio
class AudioDetection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sound_type = models.ForeignKey(SoundType, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    detection_date = models.DateTimeField(auto_now_add=True)

# Recomendaciones
class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    detection = models.ForeignKey(AudioDetection, on_delete=models.CASCADE)
    history = models.ForeignKey(DrivingHistory, on_delete=models.CASCADE)
    message = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='normal')

# Tipos de vehículos
class VehicleType(models.Model):
    type_name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

# Sensores del vehículo
class VehicleSensor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sensor_type = models.CharField(max_length=50)
    sensor_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='normal')
    sensor_time = models.DateTimeField(auto_now_add=True)

# Detección visual
class VisualDetection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    frequency = models.IntegerField()
    detection_date = models.DateTimeField(auto_now_add=True)
