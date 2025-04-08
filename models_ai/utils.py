import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from io import BytesIO
from PIL import Image


def wav_a_tensor(wav_path, target_size=(128, 128)):
    # Cargar audio
    y, sr = librosa.load(wav_path, sr=None)

    # Crear espectrograma Mel
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    S_dB = librosa.power_to_db(S, ref=np.max)

    # Dibujar el espectrograma en memoria
    fig = plt.figure(
        figsize=(4, 4), dpi=100
    )  # esto genera 400x400 pero luego redimensionamos
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    fig.add_axes(ax)
    librosa.display.specshow(S_dB, sr=sr, cmap="magma")

    # Guardar en buffer en memoria
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    buf.seek(0)

    # Convertir imagen desde el buffer
    image = Image.open(buf).convert("RGB")
    image = image.resize(target_size)
    image = np.array(image).astype(np.float32) / 255.0
    image_tensor = tf.expand_dims(image, axis=0)

    return image_tensor
