import asyncio
import websockets
import pyaudio
import wave
import time
import RPi.GPIO as GPIO

# Settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
OUTPUT_FILENAME = "mochibi-audio"
X_PIN = 17  # X-axis pin
Y_PIN = 27  # Y-axis pin
BUTTON_PIN = 22  # Button pin
CHUNK_SIZE = 1024 * 1024

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(X_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(Y_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

async def send_file_in_chunks(audio_file_path, websocket):
    with open(audio_file_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            await websocket.send(chunk)
            print(f"Sent chunk of size: {len(chunk)}")

    await websocket.send("EOF")
    print("Sent EOF marker")

async def open_websocket_connection():
    uri = "ws://192.168.178.55:7777/ws"
    websocket = await websockets.connect(uri)
    print("WebSocket connection established")
    return websocket

def record_audio() -> str:
    audio = pyaudio.PyAudio()
    print("\nRecording audio...")
    unique_id = str(time.time())
    unique_fileName = OUTPUT_FILENAME + "-" + unique_id + ".wav"
    full_file_path = "/tmp/" + unique_fileName

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    frames = []
    for i in range(int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording finished.")
    stream.stop_stream()
    stream.close()

    with wave.open(full_file_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    audio.terminate()
    print(f"Audio recorded and saved as {unique_fileName}")
    return full_file_path

def play_audio(file_path):
    """Play the audio file specified by file_path."""
    audio = pyaudio.PyAudio()
    print(f"Playing audio from {file_path}")
    try:
        wf = wave.open(file_path, 'rb')
    except wave.Error as e:
        print(f"Error opening audio file: {e}")
        return

    stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

    data = wf.readframes(CHUNK)
    while data:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    wf.close()
    audio.terminate()
    print(f"Finished playing {file_path}")

def write_binary_data_to_file(data) -> str:
    unique_id = str(time.time())
    unique_fileName = OUTPUT_FILENAME + "INPUT" + "-" + unique_id + ".wav"
    full_file_path = "/tmp/" + unique_fileName
    with open(full_file_path, "wb") as f:
        f.write(data)
    
    return full_file_path

async def handle_websocket_messages(websocket):
    """Handle incoming WebSocket messages."""
    complete_audio_data = bytearray()
    while True:
        try:
            message = await websocket.recv()
            if message == "EOF":
                print("Received EOF marker, preparing to play audio.")
                file_path = write_binary_data_to_file(complete_audio_data)
                print(f"Complete audio received, saved to {file_path}")
                await asyncio.sleep(0.1)  # Slight delay before playing
                play_audio(file_path)
                complete_audio_data.clear()
            else:
                complete_audio_data.extend(message)
                print(f"Received chunk of size {len(message)}")
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed, attempting to reconnect...")
            websocket = await open_websocket_connection()
            continue  # Resume listening with the new connection

async def monitor_button_press(websocket):
    """Monitor the button press and record audio when pressed."""
    while True:
        button_state = GPIO.input(BUTTON_PIN)
        print(f"Button state: {button_state}")

        if button_state == GPIO.LOW:
            print("Button pressed")
            audio_file_path = record_audio()
            await send_file_in_chunks(audio_file_path, websocket)
            await asyncio.sleep(0.5)  # Debounce delay

        await asyncio.sleep(0.1)

async def main():
    websocket = await open_websocket_connection()

    try:
        await asyncio.gather(
            handle_websocket_messages(websocket),
            monitor_button_press(websocket)
        )

    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        GPIO.cleanup()
        await websocket.close()

if __name__ == "__main__":
    asyncio.run(main())
