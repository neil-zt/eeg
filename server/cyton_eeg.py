from model.Frame import Frame
from model.Stream import Stream
from model.MNEDriver import MNEDriver
from model.Server import Server


if __name__ == '__main__':
    # Running the FastAPI server
    server = Server(
        host="localhost", 
        port=8000,
        num_files=6,
    )

    frame = Frame(
        channels=["Fp1"],
        channel_types=["eeg"],
        sample_rate=250,
        max_cache_samples=250*3,
        window_size_samples=250*3,
        output_directory="./server/results", 
        server=server)
    
    frame.wrap(pipeline=[          
        MNEDriver.record_data,
        MNEDriver.plot_psds_topomap,
        (MNEDriver.plot_data, {"scalings":1e3, "duration": 30}),
        MNEDriver.plot_psd,
        (MNEDriver.savgol_filter, {"window_length": 51, "polyorder": 3}),
        (MNEDriver.plot_data, {"scalings":1e3}),
        MNEDriver.plot_psd,
        (MNEDriver.notch_filter, {"freqs": [60, 120]}),
        # (MNEDriver.filter, {"l_freq": 0.5, "h_freq": 45}), 
        (MNEDriver.plot_data, {"scalings":1e3, "duration": 30}),
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


