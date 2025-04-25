from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import (
    VisualDetectionSerializer,
    LocationSerializer,
    AudioDetectionSerializer,
)
from .models import AudioDetection
from django.utils import timezone


class VisualDetectionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VisualDetectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AudioDetectionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AudioDetectionSerializer(data=request.data)
        if serializer.is_valid():
            audio_detection = serializer.save(user=request.user)
            return Response(
                {
                    **serializer.data,
                    "creation_timestamp": timezone.localtime(
                        audio_detection.detection_date
                    ).isoformat(),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            location = serializer.save(user=request.user)
            return Response(
                {
                    **serializer.data,  # Datos serializados
                    # "creation_timestamp": location.date.isoformat(),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response([{"type": "police", "direction": "left"}])


class AudioDetectionListView(APIView):
    def get(self, request):
        # Obtiene todas las detecciones de audio sin filtrar por usuario
        audio_detections = AudioDetection.objects.all()
        serializer = AudioDetectionSerializer(audio_detections, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
