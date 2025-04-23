from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import (
    VisualDetectionSerializer,
    LocationSerializer,
    AudioDetectionSerializer,
)
from .models import VisualDetection
from django.utils import timezone
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes

from .yolo_predict import predict_image
import cv2


@api_view(["POST"])
def PredictFromCameraView(request):
    # Acceder a la cámara (0 = cámara por defecto)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return Response({"error": "No se pudo acceder a la cámara"}, status=500)

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return Response({"error": "No se pudo capturar un frame"}, status=500)

    # Convertir el frame capturado en bytes
    _, img_encoded = cv2.imencode(".jpg", frame)
    image_bytes = img_encoded.tobytes()

    # Hacer predicción con YOLO
    detections = predict_image(image_bytes)

    return Response({"detections": detections})


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
