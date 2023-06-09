import tensorflow as tf
import string
import numpy as np
from nltk.stem import WordNetLemmatizer
import pickle

# Load the model
model = tf.keras.models.load_model(r'data\hate_speech_detection_model.h5')

# Tokenizer
with open(r"data\tokenizer.pkl", "rb") as file:
    tokenizer = pickle.load(file)

# Stop Words
with open(r"data\english", "rt") as file:
    stop_words = file.read()

punctuations_list = string.punctuation
def remove_punctuations(text):
    temp = str.maketrans('', '', punctuations_list)
    return text.translate(temp)

def remove_stopwords(text):
    imp_words = []
 
    # Storing the important words
    for word in str(text).split():
 
        if word not in stop_words:
            # Let's Lemmatize the word as well
            # before appending to the imp_words list.
            lemmatizer = WordNetLemmatizer()
            lemmatizer.lemmatize(word)
            imp_words.append(word)
 
    output = " ".join(imp_words)
 
    return output

def predict(message):
    # Preprocess the message
    message = message.lower()
    message = remove_punctuations(message)
    message = remove_stopwords(message)

    # Tokenize and pad the message
    tokenized_message = tokenizer.texts_to_sequences([message])
    padded_message = tf.keras.preprocessing.sequence.pad_sequences(tokenized_message, maxlen=100)

    # Make predictions
    predictions = model.predict(padded_message)
    predicted_class = np.argmax(predictions)

    # Map the predicted class to the corresponding label
    label_mapping = {0: 'Hate Speech', 1: 'Offensive', 2: 'Neutral'}
    predicted_label = label_mapping[predicted_class]

    return predicted_class, predicted_label, predictions[0], predictions[0][predicted_class]
