from model.Frame import Frame
from model.Stream import Stream
from model.MNEDriver import MNEDriver
from model.Server import Server


if __name__ == '__main__':

    frame = Frame(
        channels=["Fp1", "Fp2", "F5", "F6", "Fz", "T7", "Cz", 
                  "T8", "P7", "P3", "Pz", "P4", "P8", "O1", "Oz", "O2"],
        sample_rate=512,
        max_cache_samples=1024,
        window_size_samples=512,
        output_directory="./server/results",)
    
    frame.wrap(pipeline=[ 
        # MNEDriver.record_data,
        (MNEDriver.plot_data, {"scalings": 30}),
        MNEDriver.plot_psd,
        (MNEDriver.filter, {"l_freq": 1.5, "h_freq": 80}),
        MNEDriver.plot_psd,
        (MNEDriver.plot_data, {"scalings": 30}),
        (MNEDriver.plot_psds_topomap, {"bands": {
            'Alpha (7.5-12 Hz)': (7.5, 12), 'Beta (12-30 Hz)': (12, 30), 'Gamma (30-45 Hz)': (30, 45)  }, }),
        MNEDriver.plot_evoked,
        MNEDriver.plot_topomap,
    ])

    stream = Stream(
        file_name="./server/sample_data/eeg-alpha-waves/subject_11.csv",
        read_pause=0.00,
        drop_last=2,
        drop_first=1,
    )
    stream.onload(pipeline=[
        frame.add_singal,])
    stream.start()

    # Running the FastAPI server
    server = Server(host="0.0.0.0", port=8000)
    server.run()
