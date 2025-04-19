import json
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import librosa
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from channels.db import database_sync_to_async
import struct
from django.contrib.auth import get_user_model

from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken  # Añade esta importación


# Usar los mismos modelos que en tu vista existente
MODEL_PATH = "audio_model.h5"
model = tf.keras.models.load_model(MODEL_PATH)
LABELS = ["ambulance", "car_horn", "firetruck", "police", "siren", "traffic", "unknown"]
yamnet_model = hub.load("https://tfhub.dev/google/yamnet/1")


class AudioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Autenticar al usuario usando token
        query_string = self.scope["query_string"].decode()

        # Verificar si hay un token en la consulta
        if "token=" not in query_string:
            print("No se proporcionó token en la consulta")
            await self.close(code=4003)
            return

        token = query_string.split("token=")[1].split("&")[0]
        self.user = await self.get_user_from_token(token)

        if not self.user:
            print("Autenticación fallida, token inválido o expirado")
            await self.close(code=4001)
            return

        print(f"Usuario autenticado: {self.user.username}")

        # Inicializar variables
        self.session_id = None
        self.is_streaming = False
        self.frame_counter = 0
        self.sample_rate = 48000  # Valor por defecto
        self.frame_time = 500  # ms por defecto
        self.audio_buffer = []

        await self.accept()
        print(f"Conexión WebSocket aceptada para {self.user.username}")

    @database_sync_to_async
    def get_user_from_token(self, token_key):
        try:
            # Decodificar JWT
            token = AccessToken(token_key)
            user_id = token.payload.get("user_id")
            User = get_user_model()
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError) as e:
            print(f"Error de token JWT: {str(e)}")
            return None
        except Exception as e:
            print(f"Error inesperado en autenticación: {str(e)}")
            return None

    async def disconnect(self, close_code):
        print(f"WebSocket desconectado, código: {close_code}")
        self.is_streaming = False

    async def receive(self, text_data=None, bytes_data=None):
        # Recibir datos binarios (audio)
        if bytes_data:
            await self.process_audio_frame(bytes_data)
            return

        # Recibir datos de texto (comandos/metadatos)
        if text_data:
            try:
                data = json.loads(text_data)
                # print(f"Datos de texto recibidos: {text_data[:100]}...")

                if data.get("type") == "config":
                    # Configuración inicial
                    self.sample_rate = data.get("sampleRate", 48000)
                    self.frame_time = data.get("frameTime", 500)
                    print(
                        f"Configuración actualizada: sampleRate={self.sample_rate}, frameTime={self.frame_time}"
                    )

                    await self.send(
                        text_data=json.dumps(
                            {"type": "config_response", "status": "ok"}
                        )
                    )

                elif data.get("type") == "start_streaming":
                    # Iniciar una nueva sesión de streaming
                    self.is_streaming = True
                    self.session_id = data.get("session_id")
                    self.frame_counter = 0
                    self.audio_buffer = []  # Limpiar buffer
                    print(f"Iniciando streaming, session_id: {self.session_id}")

                    await self.send(
                        text_data=json.dumps(
                            {
                                "type": "streaming_status",
                                "status": "started",
                                "session_id": self.session_id,
                            }
                        )
                    )

                elif data.get("type") == "end_streaming":
                    self.is_streaming = False
                    print(
                        f"Finalizando streaming, frames procesados: {self.frame_counter}"
                    )

                    # Procesar el buffer restante
                    if len(self.audio_buffer) > 0:
                        combined_audio = np.concatenate(self.audio_buffer)
                        await self.analyze_audio(combined_audio)
                        self.audio_buffer = []

                    await self.send(
                        text_data=json.dumps(
                            {
                                "type": "streaming_status",
                                "status": "ended",
                                "frames_processed": self.frame_counter,
                            }
                        )
                    )

                elif data.get("type") == "audio_frame":
                    # Metadatos que preceden a un frame de audio
                    self.frame_counter = data.get("frame_id", self.frame_counter)
                    # print(
                    #     f"Metadatos de frame recibidos, frame_id: {self.frame_counter}"
                    # )

            except json.JSONDecodeError:
                print(f"Error: JSON inválido: {text_data}")
            except Exception as e:
                print(f"Error procesando mensaje de texto: {str(e)}")

    async def process_audio_frame(self, bytes_data):
        if not self.is_streaming:
            print("Frame de audio recibido pero streaming está inactivo")
            return

        try:
            # Convertir bytes a Int16Array
            samples = len(bytes_data) // 2  # 2 bytes por muestra (Int16)
            int16_data = struct.unpack(f"{samples}h", bytes_data)
            # print(
            #     f"Frame de audio recibido: {len(bytes_data)} bytes, {samples} muestras"
            # )

            # Convertir de Int16 a Float32 para procesamiento
            float32_data = np.array(int16_data, dtype=np.float32) / 32767.0

            # Añadir al buffer acumulativo
            self.audio_buffer.append(float32_data)

            # Calcular duración actual del buffer
            # En process_audio_frame
            buffer_duration = (
                sum(len(chunk) for chunk in self.audio_buffer) / self.sample_rate
            )
            # print(f"Buffer acumulado: {buffer_duration:.2f} segundos")

            # Reducir el umbral para pruebas
            if buffer_duration >= 0.5:  # 0.5 segundos en lugar de 1.0
                # print("Procesando buffer de audio acumulado...")
                # resto del código...

                combined_audio = np.concatenate(self.audio_buffer)

                # Analizar el audio
                start_time = timezone.now()
                results = await self.analyze_audio(combined_audio)
                end_time = timezone.now()

                # Calcular tiempo de procesamiento
                processing_time = (end_time - start_time).total_seconds() * 1000  # ms
                # print(
                #     f"Análisis completado en {processing_time:.2f}ms. Resultado: {results['top_label']} ({results['top_score']:.2f})"
                # )

                # Enviar resultados al cliente
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "detection_result",
                            "timestamp": timezone.now().isoformat(),
                            "frame_id": self.frame_counter,
                            # "result": results["top_label"],
                            # "score": results["top_score"],
                            # "is_critical": results["is_critical"],
                            "all_results": results["all_results"],
                            "processing_time": processing_time,
                        }
                    )
                )

                # Mantener solo el último chunk para continuidad
                last_chunk = self.audio_buffer[-1]
                self.audio_buffer = [last_chunk]
                # print("Buffer reiniciado, manteniendo último chunk")

        except Exception as e:
            print(f"Error procesando frame de audio: {str(e)}")

    async def analyze_audio(self, audio_data):
        # Ejecutar el modelo en un thread separado
        results = await self.run_audio_model(audio_data)
        return results

    @database_sync_to_async
    def run_audio_model(self, audio_data):
        try:
            # Resample si es necesario (YAMNet espera 16kHz)
            if self.sample_rate != 16000:
                audio_resampled = librosa.resample(
                    audio_data, orig_sr=self.sample_rate, target_sr=16000
                )
            else:
                audio_resampled = audio_data

            # Procesar con YAMNet (igual que en tu API View)
            _, embeddings, _ = yamnet_model(audio_resampled)
            embedding_medio = tf.reduce_mean(embeddings, axis=0).numpy()

            # Predicción con el modelo
            predicciones = model.predict(np.array([embedding_medio]))[0]

            # Procesar resultados
            paired = list(zip(LABELS, predicciones))
            ordered = sorted(paired, key=lambda x: x[1], reverse=True)

            resultados_ordenados = [
                {"label": label, "score": float(f"{score:.4f}")}
                for label, score in ordered
            ]

            # Determinar si es un sonido crítico
            # critical_sounds = ["ambulance", "police", "siren", "firetruck"]
            # top_label = ordered[0][0]
            # top_score = ordered[0][1]
            # is_critical = top_label in critical_sounds and top_score > 0.6

            # Opcional: guardar en la base de datos
            # detection_id = await self.save_detection(results)

            return {
                # "top_label": top_label,
                # "top_score": float(f"{top_score:.4f}"),
                # "is_critical": is_critical,
                "all_results": resultados_ordenados,
            }
        except Exception as e:
            print(f"Error en análisis de audio: {str(e)}")
            return {
                # "top_label": "error",
                # "top_score": 0.0,
                # "is_critical": False,
                "all_results": [{"label": "error", "score": 0.0}],
            }
