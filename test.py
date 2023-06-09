
import tensorflow as tf
model = tf.keras.models.load_model(r'data\hate_speech_detection_model3.h5')
model.summary()