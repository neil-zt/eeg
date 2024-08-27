"""
This configuration works best for ECG signal measurements using 
the Cyton board in conjunction with the negative-impedance amplifying
board. Additional electrodes can be used, although measurements
under coupling conditions do not perform well just yet. 
"""


from model.Frame import Frame
from model.Stream import Stream
from model.MNEDriver import MNEDriver
from model.Server import Server


if __name__ == '__main__':
    # Running the FastAPI server
    server = Server(
        host="localhost", 
        port=8000,
        num_files=10,
    )

    frame = Frame(
        channels=["Fp1"],                                       # The MNE package work with EEG better, so pretend that 
        channel_types=["eeg"],                                  # Fp1 is the EEG channel we're analyzing
        sample_rate=250,                                        # one of these channels represent our ECG data.
        max_cache_samples=1000,
        window_size_samples=1000,
        output_directory="./server/results", 
        server=server)
    
    frame.wrap(pipeline=[          
        MNEDriver.record_data,
        (MNEDriver.plot_data, {"scalings":2e3}),                # Adjust the scaling as needed
        MNEDriver.plot_psd,
        (MNEDriver.notch_filter, {"freqs": [60, 120]}),
        (MNEDriver.filter, {"l_freq": 0.5, "h_freq": 35}),      # Cutoff for HPF for ECG is usually set at 0.5 Hz.
        (MNEDriver.plot_data, {"scalings":2e3}),
        MNEDriver.plot_psd,
        (MNEDriver.savgol_filter, {"window_length": 51, "polyorder": 3}),
        (MNEDriver.plot_data, {"scalings":2e3}),
        MNEDriver.plot_psd,
        MNEDriver.moving_average_smoothening,
        (MNEDriver.plot_data, {"scalings":2e3}),
        MNEDriver.plot_psd,
        MNEDriver.record_data,
    ])

    stream = Stream(
        serial_port='COM5',
        board_type='Cyton', 
        read_pause=1, )
    stream.onload(pipeline=[
        frame.add_singal,])
    stream.start()

    server.run()


