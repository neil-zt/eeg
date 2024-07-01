import serial
import time
import threading
import uvicorn
from fastapi import FastAPI
from model.Frame import Frame



# Global variable to store the latest signal
latest_signal = None

# Configure serial port
SERIAL_PORT = '/dev/tty.usbserial-2110'  # Update this to your serial port
BAUD_RATE = 9600
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
except Exception:
    print(f"Failed to connect to serial port {SERIAL_PORT}. See README for trouble-shooting Exiting...")
    exit(1)
    
app = FastAPI()
@app.get("/data")
def get_latest_signal():
    return {"latest_signal": latest_signal}


def start_stream_thread(**kwargs):
    """
    Start a new thread to read the serial port.
    """
    thread = threading.Thread(target=lambda: stream(**kwargs))
    thread.daemon = True
    thread.start()


def stream(**kwargs):
    """
    This function reads the serial port and processes the incoming data. The
    way it reads in data helps to ensure there are no skips or duplicates. A
    pipeline must be provided that is a list of functions to be called 
    sequentially on the incoming signal.
    """
    global latest_signal
    last_series_num = 0

    # Reads in the data while eliminating skips and duplicates
    while True:
        if ser.in_waiting > 0:
            packets = ser.readline().decode('utf-8').strip().split("||")
            if len(packets) == 0:
                continue
            for packet in packets:
                [series_num, signal] = packet.split("|")
                if int(series_num) == last_series_num:
                    continue
                last_series_num = int(series_num)

                # We have obtained the clean signal. Now we process
                # The signal by running the pipeline provided. 
                pipeline = kwargs["pipeline"]
                for processor in pipeline:
                    signal = processor(signal)


if __name__ == '__main__':

    frame = Frame()
    pipeline = [print]

    start_stream_thread(pipeline=pipeline)          # Running in another thread, hence async non-blocking
    uvicorn.run(app, host="0.0.0.0", port=8080)