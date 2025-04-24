from django.urls import path
from .views import (
    PredictFromCameraView,
    VisualDetectionCreateView,
    LocationCreateView,
    AudioDetectionCreateView,
    NotificationView,
    AudioDetectionListView,
)

urlpatterns = [
    path(
        "visual/create/",
        VisualDetectionCreateView.as_view(),
        name="create_visual_detection",
    ),
    path("location/create/", LocationCreateView.as_view(), name="create_location"),
    path(
        "audio/create/",
        AudioDetectionCreateView.as_view(),
        name="create_audio_detection",
    ),
    path("api/notifications/", NotificationView.as_view()),
    path("visual/predict-camera/", PredictFromCameraView, name="predict_from_camera"),
    path('audio_list/', AudioDetectionListView.as_view(), name='list_audio_detections'),
]
