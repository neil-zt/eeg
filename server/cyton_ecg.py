from model.Frame import Frame
from model.Stream import Stream
from model.MNEDriver import MNEDriver
from model.Server import Server


if __name__ == '__main__':

    frame = Frame(
        channels=["Fp1"],                                       # The MNE package work with EEG better, so pretend that 
        channel_types=["eeg"],                                  # Fp1 is the EEG channel we're analyzing
        sample_rate=250,                                        # one of these channels represent our ECG data.
        max_cache_samples=2500,
        window_size_samples=2500,
        output_directory="./server/results",)
    
    frame.wrap(pipeline=[          
        MNEDriver.record_data,
        (MNEDriver.plot_data, {"scalings": 4e4}),               # Adjust the scaling as needed
        MNEDriver.plot_psd,
        (MNEDriver.notch_filter, {"freqs": [60, 120]}),
        (MNEDriver.filter, {"l_freq": 0.5, "h_freq": 50}),      # Cutoff for HPF for ECG is usually set at 0.5 Hz.
        (MNEDriver.plot_data, {"scalings": 4e4}),
        MNEDriver.plot_psd,
        (MNEDriver.savgol_filter, {"window_length": 50, "polyorder": 3}),
        (MNEDriver.plot_data, {"scalings": 4e4}),
        MNEDriver.plot_psd,
        MNEDriver.moving_average_smoothening,
        (MNEDriver.plot_data, {"scalings": 4e4}),
        MNEDriver.plot_psd,
        MNEDriver.record_data,
    ])

    stream = Stream(
        serial_port='COM5',
        board_type='Cyton', 
        read_pause=1, )
    stream.onload(pipeline=[
        print, 
        frame.add_singal,])
    stream.start()

    # Running the FastAPI server
    server = Server(host="0.0.0.0", port=8000)
    server.run()


