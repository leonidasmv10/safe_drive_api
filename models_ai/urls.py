from django.urls import path
from .views import *

urlpatterns = [
    path(
        "detection-critical-sound/",
        DetectionCriticalSoundAPIView.as_view(),
        name="detection-critical-sound",
    ),
]
