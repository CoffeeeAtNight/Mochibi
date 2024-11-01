import speech_recognition as sr

def convert_speech_to_text(filePathToAudio) -> str:
  """
  Convert audio data to text
  """
  r = sr.Recognizer()
  with sr.AudioFile(filePathToAudio) as source:
    audio_data = r.record(source)
    text = r.recognize_google(audio_data)

  return text