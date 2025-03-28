from django.db import models
from django.contrib.auth.models import User

class DrivingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    avg_speed = models.DecimalField(max_digits=6, decimal_places=2)
    total_hard_brakes = models.IntegerField()
    total_horns = models.IntegerField()
    total_sirens = models.IntegerField()
    registration_date = models.DateTimeField(auto_now_add=True)


# STATUS_CHOICES = [('normal', 'Normal'), ('warning', 'Warning'), ('critical', 'Critical')]
# class VehicleSensor(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     sensor_type = models.CharField(max_length=50)
#     sensor_value = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='normal')
#     sensor_time = models.DateTimeField(auto_now_add=True)