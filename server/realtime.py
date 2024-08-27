from model.Frame import Frame
from model.Stream import Stream
from model.MNEDriver import MNEDriver
from model.Server import Server


if __name__ == '__main__':

    frame = Frame(
        channels=["Fp1", "Fp2", "F3", "F4", 
                  "F7", "F8", "C3", "C4"],
        sample_rate=125,
        max_cache_samples=125,
        window_size_samples=60,
        output_directory="./server/results",)
    
    frame.wrap(pipeline=[ 
        # MNEDriver.record_data,
        MNEDriver.plot_data,
        MNEDriver.plot_psd,
        (MNEDriver.filter, {"l_freq": 15, "h_freq": 45}),
        MNEDriver.plot_data,
        MNEDriver.plot_psd,
    ])

    stream = Stream(
        serial_port='COM5',
        baud_rate=9600,)
    stream.onload(pipeline=[
        print, 
        frame.add_singal,])
    stream.start()

    # Running the FastAPI server
    server = Server(host="0.0.0.0", port=8000)
    server.run()


