from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, UpdateUserProfileSerializer, ChangePasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .serializers import ProfileSerializer
from rest_framework import generics

class TestView(APIView):
    def get(self, request):
        return Response({"message": "¡Bienvenido de nuevo!"}, status=status.HTTP_200_OK)

class RegisterAPIView(APIView):
    def post(self, request):
        print("Datos recibidos:", request.data)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            print("Usuario registrado:", user)
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Usuario registrado con éxito',
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Invalida el token
            return Response({"message": "Logout exitoso"}, status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return Response({"error": "Refresh token no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
    

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({'message': 'Usuario eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)


class UpdateUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UpdateUserProfileSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Usuario y perfil actualizados correctamente'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Contraseña actualizada correctamente'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        print(email)
        print(User.objects.values_list('email', flat=True))
        user = get_object_or_404(User, email=email)
        print(user.pk)
        
        token = default_token_generator.make_token(user)
        reset_link = f"http://127.0.0.1:8000/reset-password/{user.pk}/{token}"
        print(reset_link)
        
        send_mail(
            subject="Restablecer tu contraseña",
            message=f"Haz clic en el enlace para cambiar tu contraseña: {reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email]
        )

        return Response({"message": "Correo enviado"}, status=status.HTTP_200_OK)

    
class PasswordResetConfirmView(APIView):
    def post(self, request,uidb64, token):
        user = get_object_or_404(User, pk=uidb64)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get('password')
        user.set_password(new_password)
        user.save()

        return Response({"message": "Contraseña cambiada exitosamente"}, status=status.HTTP_200_OK)
