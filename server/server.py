import serial
import time
import threading
import uvicorn
from fastapi import FastAPI

print("here")

# Configure serial port
SERIAL_PORT = '/dev/tty.usbserial-2110'  # Update this to your serial port
BAUD_RATE = 9600
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Global variable to store the latest signal
latest_signal = None

def read_serial():
    global latest_signal
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(f"Received: {line}")
            latest_signal = line
            time.sleep(0.008)  # The 8 millisecond delay as in Arduino code

def start_reading_thread():
    """
    Start a new thread to read the serial port.
    """
    thread = threading.Thread(target=read_serial)
    thread.daemon = True
    thread.start()

# Configure API endpoint
app = FastAPI()

@app.get("/latest_signal")
def get_latest_signal():
    return {"latest_signal": latest_signal}

print("Starting the reading thread...")
start_reading_thread()
uvicorn.run(app, host="0.0.0.0", port=8080)