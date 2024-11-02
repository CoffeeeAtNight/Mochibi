import time
from gtts import gTTS
from pydub import AudioSegment

def convert_text_to_speech(text) -> str:
    unique_id = str(time.time())
    OUTPUT_FILENAME = "mochibi-tts"
    mp3_file = OUTPUT_FILENAME + "-" + unique_id + ".mp3"
    wav_file = OUTPUT_FILENAME + "-" + unique_id + ".wav"
    
    mp3_file_path = "/tmp/" + mp3_file
    wav_file_path = "/tmp/" + wav_file

    # Generate speech in .mp3 format
    tts = gTTS(text=text, lang='en')
    tts.save(mp3_file_path)
    print(f"MP3 audio saved to {mp3_file_path}")

    # Convert .mp3 to .wav
    audio = AudioSegment.from_mp3(mp3_file_path)
    audio.export(wav_file_path, format="wav")
    print(f"Converted WAV audio saved to {wav_file_path}")
    
    return wav_file_path
