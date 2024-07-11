from model.Frame import Frame
from model.Stream import Stream
from model.MNEDriver import MNEDriver
from model.Server import Server
from model.Noise import Noise
from model.Metrics import Metrics


if __name__ == '__main__':

    recorder = Metrics()

    frame = Frame(
        channels=["Fp1", "Fp2", "F5", "F6", "Fz", "T7", "Cz", 
                  "T8", "P7", "P3", "Pz", "P4", "P8", "O1", "Oz", "O2"],
        sample_rate=512,
        max_cache_samples=1024,
        window_size_samples=512,
        output_directory="./server/results", )
    
    frame.wrap(pipeline=[ 

        # We first plot the clean data and the PSD of it.
        # We also take a snapshot of the data for later comparison. 
        (MNEDriver.plot_data, {"scalings": 30}),
        MNEDriver.plot_psd,
        (Metrics.take_snapshot, {"metrics": recorder, 
                                 "name": "original"}),

        # Now we add noise to the data. 
        (Noise.add_noise, {"scale": 0.001, 
                           "sin_frequency": 60}),

        # We take another snapshot of the data with noise.
        (MNEDriver.plot_data, {"scalings": 30}),
        MNEDriver.plot_psd,
        (Metrics.take_snapshot, {"metrics": recorder, 
                                 "name": "noisy"}),

        # See the correlation and clear the snapshots.
        (Metrics.record_pearson_correlation, {"metrics": recorder, 
                                              "snapshots": ["original", "noisy"],
                                              "cascade_output": True}),

        # Use a notch filter to remove the noise. 
        (MNEDriver.notch_filter, {"freqs": [60]}),

        # We plot the data and the PSD, and take a snapshot of the data.
        (MNEDriver.plot_data, {"scalings": 30}),
        MNEDriver.plot_psd,
        (Metrics.take_snapshot, {"metrics": recorder, 
                                 "name": "filtered"}),

        # We see the correlation, and clear the snapshots. 
        (Metrics.record_pearson_correlation, {"metrics": recorder, 
                                              "snapshots": ["original", "filtered"],
                                              "cascade_output": True}),
        (Metrics.clear_snapshots, {"metrics": recorder}),
    ])

    stream = Stream(
        file_name="./server/sample_data/eeg-alpha-waves/subject_11.csv",
        read_pause=0.00,
        drop_last=2,
        drop_first=1,
    )
    stream.onload(pipeline=[frame.add_singal,])
    stream.start()

    # Running the FastAPI server
    server = Server(host="0.0.0.0", port=8000)
    server.run()
