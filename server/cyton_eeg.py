from model.Frame import Frame
from model.Stream import Stream
from model.MNEDriver import MNEDriver
from model.Server import Server


if __name__ == '__main__':
    # Running the FastAPI server
    server = Server(
        host="localhost", 
        port=8000,
        num_files=2,
    )

    frame = Frame(
        channels=["Fp1"],
        channel_types=["eeg"],
        sample_rate=250,
        max_cache_samples=250*20,
        window_size_samples=250*20,
        output_directory="./server/results", 
        server=server)
    
    frame.wrap(pipeline=[          
        MNEDriver.record_data,
        (MNEDriver.plot_data, {"scalings":1e4}),
    ])

    stream = Stream(
        serial_port='COM5',
        board_type='Cyton', 
        read_pause=1, )
    stream.onload(pipeline=[
        frame.add_singal,])
    stream.start()

    server.run()


