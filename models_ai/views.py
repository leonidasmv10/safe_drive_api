from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
import tensorflow as tf
from rest_framework import generics
from .utils import *


class DetectionCriticalSoundAPIView(APIView):

    def post(self, request):
        print("Datos recibidos:", request.data)
        model = tf.keras.models.load_model("audio_model.h5")

        audio_predict_path = "audio_test.wav"

        image_tensor = wav_a_tensor(audio_predict_path)
        # print(image_tensor.shape)
        pred = model.predict(image_tensor)
        pred_clase = np.argmax(pred, axis=1)[0]

        labels = ["ambulance", "car_horn", "firetruck", "police"]
        # print(f"Predicción: {labels[pred_clase]}")

        return Response(
            {"message": request.data.get("audio_base64"), "pred": labels[pred_clase]},
            status=status.HTTP_201_CREATED,
        )
