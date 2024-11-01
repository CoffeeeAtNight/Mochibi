#!/usr/bin/env python3
import asyncio
import websockets
import pyaudio
import wave
import time
# import RPi.GPIO as GPIO

# Settings
FORMAT = pyaudio.paInt16  # Format of sampling (16-bit PCM)
CHANNELS = 1              # Number of audio channels (1 for mono, 2 for stereo)
RATE = 44100              # Sampling rate (44.1kHz for CD quality)
CHUNK = 1024              # Number of frames per buffer
RECORD_SECONDS = 5        # Duration of recording
OUTPUT_FILENAME = "mochibi-audio"
X_PIN = 17  # X-axis pin
Y_PIN = 27  # Y-axis pin
BUTTON_PIN = 22  # Button pin

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(X_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(Y_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

async def send_file_in_chunks():
    """
    Send the given audio file in chunks over a WebSocket connection.

    The audio file is opened in binary read mode and read in chunks of
    chunk_size (default 1MB). Each chunk is sent over the WebSocket
    connection as a binary message. After all chunks have been sent,
    an "EOF" marker is sent to indicate the end of the file.

    :param audio_file_path: The path to the audio file to send
    :type audio_file_path: str
    """
    uri = "ws://localhost:7777/ws"
    chunk_size = 1024 * 1024  # 1 MB

    async with websockets.connect(uri) as websocket:
        with open("../../data/mochibi-audio.wav", "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                await websocket.send(chunk)
                print(f"Sent chunk of size: {len(chunk)}")

        await websocket.send("EOF")
        print("Sent EOF marker")

asyncio.run(send_file_in_chunks())

# def record_audio() -> str:
#     """
#     Record audio from the microphone and save it to a file.

#     This function uses PyAudio to record audio from the microphone.
#     It records audio for RECORD_SECONDS seconds, and saves it to a file
#     named OUTPUT_FILENAME.

#     After recording, it prints a message indicating that the recording
#     is finished, and saves the recorded audio to a file.

#     :return: None
#     """
#     audio = pyaudio.PyAudio()
#     print("\nRecording audio...")
#     unique_id = str(time.time())
#     unique_fileName = OUTPUT_FILENAME + "-" + unique_id + ".wav"
#     full_file_path = "/tmp/" + unique_fileName

#     stream = audio.open(format=FORMAT, channels=CHANNELS,
#                         rate=RATE, input=True,
#                         frames_per_buffer=CHUNK)

#     frames = []

#     # Record audio
#     for i in range(int(RATE / CHUNK * RECORD_SECONDS)):
#         data = stream.read(CHUNK)
#         frames.append(data)

#     print("Recording finished.")

#     # Stop and close the stream
#     stream.stop_stream()
#     stream.close()

#     # Save the recorded audio to a file
#     with wave.open(full_file_path, 'wb') as wf:
#         wf.setnchannels(CHANNELS)
#         wf.setsampwidth(audio.get_sample_size(FORMAT))
#         wf.setframerate(RATE)
#         wf.writeframes(b''.join(frames))

#     print(f"Audio recorded and saved as {OUTPUT_FILENAME}")
#     return full_file_path
    
    
# def main():
#     try:
#         while True:
#             # Read the X-axis
#             # if GPIO.input(X_PIN) == GPIO.LOW:
#             #     print("Joystick moved left")
#             # elif GPIO.input(X_PIN) == GPIO.HIGH:
#             #     print("Joystick moved right")
            
#             # # Read the Y-axis
#             # if GPIO.input(Y_PIN) == GPIO.LOW:
#             #     print("Joystick moved up")
#             # elif GPIO.input(Y_PIN) == GPIO.HIGH:
#             #     print("Joystick moved down")

#             # Check if button is pressed
#             if GPIO.input(BUTTON_PIN) == GPIO.LOW:
#                 audio_file_path = record_audio()
#                 asyncio.run(send_file_in_chunks(audio_file_path))
#             else:
#                 pass

#             time.sleep(0.1)
#     except KeyboardInterrupt:
#         GPIO.cleanup()
    
# if __name__ == "__main__":
#     main()