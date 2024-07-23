from model.Frame import Frame
from model.Stream import Stream
from model.MNEDriver import MNEDriver
from model.Server import Server


if __name__ == '__main__':

    frame = Frame(
        channels=["Fp1", "Fp2", "F3", "F4",                     # Although we are measuging ECG, the underlying 
                  "F7", "F8", "C3", "C4"],                      # packages work with EEG better, so pretend that 
        sample_rate=250,                                        # one of these channels represent our ECG data.
        max_cache_samples=5000,
        window_size_samples=5000,
        output_directory="./server/results",)
    
    frame.wrap(pipeline=[          
        MNEDriver.record_data,
        (MNEDriver.plot_data, {"scalings": 1e3, "duration": 20}),               # Adjust the scaling as needed
        MNEDriver.plot_psd,
        (MNEDriver.notch_filter, {"freqs": [60, 120]}),
        (MNEDriver.filter, {"l_freq": 0.5, "h_freq": 50}),      # Cutoff for HPF for ECG is usually set at 0.5 Hz.
        (MNEDriver.plot_data, {"scalings": 1e3, "duration": 20}),
        MNEDriver.plot_psd,
    ])

    stream = Stream(
        serial_port='COM5',
        board_type='Cyton', 
        read_pause=1, )
    stream.onload(pipeline=[
        # print, 
        frame.add_singal,])
    stream.start()

    # Running the FastAPI server
    server = Server(host="0.0.0.0", port=8000)
    server.run()


