# from django.db import models
# from django.contrib.auth.models import User
# STATUS_CHOICES = [('normal', 'Normal'), ('warning', 'Warning'), ('critical', 'Critical')]
# # Create your models here.
# class Recommendation(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     detection = models.ForeignKey(AudioDetection, on_delete=models.CASCADE)
#     history = models.ForeignKey(DrivingHistory, on_delete=models.CASCADE)
#     message = models.TextField()
#     creation_date = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='normal')