from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
    path('test/', TestView.as_view(), name='user_test'),
    path('register/', RegisterAPIView.as_view(), name='user_register'),
    path('login/', TokenObtainPairView.as_view(), name='user_login'),
    path('logout/', LogoutAPIView.as_view(), name='user_logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
