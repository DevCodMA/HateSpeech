import speech_recognition as sr
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from pydub.effects import low_pass_filter, high_pass_filter

#Convert Speech into Text
def pySTT(audio_path, filter=None, lp_frequency=1000, hp_frequency=1000, min_silence_threshold=-30, input_type=1, mic=0, API=0):

    recognizer = sr.Recognizer()

    # For reducing noises
    recognizer.energy_threshold = min_silence_threshold

    # recognizer.dynamic_energy_adjustment_damping
    # recognizer.dynamic_energy_ratio
    # recognizer.phrase_threshold
    
    # Input is a file
    if input_type == 1:

        if filter != None:

            # Filtering audio with low pass filter 
            if filter == "LOW":
                audio = AudioSegment.from_wav(audio_path)
                filtered_audio = low_pass_filter(audio, lp_frequency)
                filtered_audio.export(r"Processed_file/audio.wav", format="wav")
            
            # Filtering audio with high pass filter
            if filter == "HIGH":
                audio = AudioSegment.from_wav(audio_path)
                filtered_audio = high_pass_filter(audio, hp_frequency)
                filtered_audio.export(r"Processed_file/audio.wav", format="wav")
            
            # Filtering audio with both filters
            if filter == "BOTH":
                audio = AudioSegment.from_wav(audio_path)
                filtered_audio = high_pass_filter(audio, hp_frequency)
                filtered_audio.export(r"Processed_file/audio.wav", format="wav")

                audio = AudioSegment.from_wav(r"Processed_file/audio.wav")
                filtered_audio = low_pass_filter(audio, lp_frequency)
                filtered_audio.export(r"Processed_file/audio.wav", format="wav")

        
        with sr.AudioFile(r"Processed_file/audio.wav") as source:
            audio = recognizer.record(source)

    # Input is microphone
    else:
        # List all the supported microphones in this device
        microphones = sr.Microphone.list_microphones()
        mic = microphones[mic]

        with mic as source:
            audio = recognizer().listen(source)
    

    # Convert the speech into text with different apis
    if API == 0:
        text = recognizer.recognize_google(audio)
    elif API == 1:
        text = recognizer.recognize_sphinx(audio)
    elif API == 2:
        text = recognizer.recognize_whisper(audio)
    
    return text


def video_to_audio(video_file):
    # Load the video clip
    video_clip = VideoFileClip(video_file)

    # Extract the audio
    audio_clip = video_clip.audio

    # Save the file
    audio_clip.write_audiofile(r"Processed_file/audio.wav")