from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import tensorflow as tf
import tempfile
import os
from .utils import *

# Carga del modelo una sola vez al iniciar el servidor
MODEL_PATH = "audio_model.h5"
model = tf.keras.models.load_model(MODEL_PATH)

# Etiquetas de las clases
LABELS = ["ambulance", "car_horn", "firetruck", "police"]

import datetime


from django.utils import timezone

from detections.models import AudioDetection, SoundType, Location


class DetectionCriticalSoundAPIView(APIView):
    def post(self, request):
        audio_file = request.FILES.get("audio")
        if not audio_file:
            return Response(
                {
                    "error": "No se proporcionó ningún archivo de audio.",
                    "timestamp": timezone.now().isoformat(),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Crear archivo temporal sin borrarlo automáticamente
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            for chunk in audio_file.chunks():
                temp_audio.write(chunk)
            temp_audio.close()

            # Procesar el archivo temporal
            audio_tensor = wav_a_tensor(temp_audio.name)
            prediction = model.predict(audio_tensor)
            predicted_label = LABELS[np.argmax(prediction)]

            location = Location.objects.create(
                user=request.user,  # Usuario autenticado
                latitud=request.data.get("latitud"),  # Cambiar por la latitud real
                longitud=request.data.get("longitud"),  # Cambiar por la longitud real
                date=timezone.now(),
            )

            # Guardar en la base de datos
            audio_detection = AudioDetection.objects.create(
                user=request.user,  # Usuario autenticado
                sound_type=SoundType.objects.get(id=np.argmax(prediction)),
                location=Location.objects.get(id=Location.objects.latest("id").id),
                detection_date=timezone.now(),
            )

            # Eliminar archivo temporal manualmente
            os.remove(temp_audio.name)

            return Response(
                {
                    # "prediction_id": np.argmax(prediction),
                    "prediction": predicted_label,
                    # "audio_detection_id": audio_detection.id,  # Retornar ID de la nueva detección
                    # "detection_date": audio_detection.detection_date.isoformat(),  # Retornar fecha y hora
                    "audio_detection_id": audio_detection.id,
                    "location_id": location.id,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "error": f"Error interno: {str(e)}",
                    "timestamp": timezone.now().isoformat(),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
