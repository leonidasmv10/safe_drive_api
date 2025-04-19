from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import tensorflow_hub as hub
import tensorflow as tf
import tempfile
import os
from .utils import *
from django.utils import timezone
from detections.models import AudioDetection, SoundType, Location
import datetime
import shutil

# Carga del modelo una sola vez al iniciar el servidor
MODEL_PATH = "critical_sound_detector_model.h5"
model = tf.keras.models.load_model(MODEL_PATH)

# Etiquetas de las clases
LABELS = ["car_horn", "siren", "unknown"]

# Cargar el modelo desde TensorFlow Hub
yamnet_model = hub.load("https://tfhub.dev/google/yamnet/1")


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
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            for chunk in audio_file.chunks():
                temp_audio.write(chunk)

            # Ruta destino donde quieres guardar el archivo
            dest_path = "C:\\Users\\yordy\\Documents\\dev\\bootcamp\\inteligencia_artificial\\fundacion_esplai\\safe_drive\\safe_drive_models\\audio_test.wav"

            temp_audio.close()

            audio, _ = librosa.load(temp_audio.name, sr=16000)
            _, embeddings, _ = yamnet_model(audio)
            embedding_medio = tf.reduce_mean(embeddings, axis=0).numpy()

            predicciones = model.predict(np.array([embedding_medio]))[0]

            paired = list(zip(LABELS, predicciones))

            # Ordenar por la precisión de mayor a menor
            ordered = sorted(paired, key=lambda x: x[1], reverse=True)

            # audio_tensor = wav_a_tensor(temp_audio.name)
            # prediction = model.predict(audio_tensor)
            # predicted_label = LABELS[np.argmax(prediction)]

            # location = Location.objects.create(
            #     user=request.user,
            #     latitud=request.data.get("latitud"),
            #     longitud=request.data.get("longitud"),
            #     date=timezone.now(),
            # )

            # audio_detection = AudioDetection.objects.create(
            #     user=request.user,
            #     sound_type=SoundType.objects.get(id=np.argmax(prediction)),
            #     location=Location.objects.get(id=Location.objects.latest("id").id),
            #     detection_date=timezone.now(),
            # )

            # shutil.copy2(temp_audio.name, dest_path)

            os.remove(temp_audio.name)

            resultados_ordenados = [
                {"label": label, "score": float(f"{score:.4f}")}
                for label, score in ordered
            ]

            return Response(
                {
                    # "prediction_id": np.argmax(prediction),
                    # "prediction": predicted_label,
                    "results": resultados_ordenados,
                    # "audio_detection_id": audio_detection.id,  # Retornar ID de la nueva detección
                    # "detection_date": audio_detection.detection_date.isoformat(),  # Retornar fecha y hora
                    # "audio_detection_id": audio_detection.id,
                    # "location_id": location.id,
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
