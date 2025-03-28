from django.urls import path
from .views import VisualDetectionCreateView

urlpatterns = [
    path('visual/create/', VisualDetectionCreateView.as_view(), name='create_visual_detection'),
]
