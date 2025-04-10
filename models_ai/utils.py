import librosa
import librosa.display

import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from io import BytesIO
from PIL import Image


def wav_a_tensor(wav_path, target_size=(128, 128)):
    """
    Convierte un archivo .wav en un tensor de imagen (espectrograma Mel) listo para el modelo.
    """
    try:
        # Cargar audio sin cambiar la frecuencia de muestreo original
        y, sr = librosa.load(wav_path, sr=None)

        # Crear espectrograma Mel y convertir a escala logarítmica
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
        S_dB = librosa.power_to_db(S, ref=np.max)

        # Crear figura sin ejes para guardar el espectrograma como imagen
        fig = plt.figure(figsize=(4, 4), dpi=100)
        ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
        ax.set_axis_off()
        fig.add_axes(ax)
        librosa.display.specshow(S_dB, sr=sr, cmap="magma")

        # Guardar figura en buffer de memoria
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
        plt.close(fig)
        buf.seek(0)

        # Leer imagen del buffer, redimensionar y normalizar
        image = Image.open(buf).convert("RGB")
        image = image.resize(target_size)
        image = np.array(image).astype(np.float32) / 255.0

        # Convertir a tensor y añadir dimensión batch
        image_tensor = tf.expand_dims(image, axis=0)
        return image_tensor

    except Exception as e:
        print(f"[ERROR en wav_a_tensor] {e}")
        raise e
