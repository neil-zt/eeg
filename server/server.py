import uvicorn
from fastapi import FastAPI
from model.Frame import Frame
from model.Stream import Stream
from model.MNEDriver import MNEDriver
    
app = FastAPI()
@app.get("/data")
def get_latest_signal():
    return {"latest_signal": ""}


if __name__ == '__main__':

    frame = Frame(
        channels=["Fp1", "Fp2", "F3", "F4", "F7", "F8", "C3", "C4"],
        sample_rate=125,
        max_cache_samples=125,
        window_size_samples=125,
        output_directory="./server/results",)
    
    frame.wrap(pipeline=[ 
        MNEDriver.record_raw,
        MNEDriver.compute_psd,
    ])

    stream = Stream(serial_port='/dev/tty.usbserial-2110', baud_rate=9600)
    stream.onload(pipeline=[ print, frame.add_singal ])
    stream.start()

    # Running the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8080)