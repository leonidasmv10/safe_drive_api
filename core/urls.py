from django.urls import path
from .views import VehicleTypeCreateView

urlpatterns = [
    path('vehicle-types/', VehicleTypeCreateView.as_view(), name='vehicle_type_create'),
]
