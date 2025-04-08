from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
import tensorflow as tf
from rest_framework import generics
import tempfile
import os
from .utils import *

# Carga del modelo una sola vez al iniciar el servidor
MODEL_PATH = "audio_model.h5"
model = tf.keras.models.load_model(MODEL_PATH)

# Etiquetas de las clases
LABELS = ["ambulance", "car_horn", "firetruck", "police"]


class DetectionCriticalSoundAPIView(APIView):
    def post(self, request):
        audio_file = request.FILES.get("audio")
        if not audio_file:
            return Response(
                {"error": "No se proporcionó ningún archivo de audio."},
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

            # Eliminar archivo temporal manualmente
            os.remove(temp_audio.name)

            return Response(
                {"message": "Predicción exitosa", "prediction": predicted_label},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"error": f"Error interno: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
