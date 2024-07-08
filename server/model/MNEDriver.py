import numpy as np
import mne, os, json
from mne.preprocessing import ICA

class MNEDriver:

    def __init__(
            self, 
            sample_rate: int,
            channels: list[str],
            channel_data_lists: list[list[float]],
            output_destination: str,
            signal_serial: int,
            montage: str = "standard_1020",
            ) -> None:
        
        self.channel_data_lists = np.array(channel_data_lists)
        self.sample_rate = sample_rate
        self.channels = channels
        self.output_destination = output_destination
        
        if len(self.channels) != len(self.channel_data_lists):
            raise ValueError("The number of channels must match the number of channel data lists.")
        
        self.num_channels = len(self.channels)
        self.num_samples = len(self.channel_data_lists[0])
        
        self.mne_info = mne.create_info(
            ch_names=self.channels,
            sfreq=self.sample_rate,
            ch_types=["eeg"]*self.num_channels,
        )
        self.mne_raw = mne.io.RawArray(self.channel_data_lists, self.mne_info)
        self.signal_serial = signal_serial

        self.montage = montage
        self.mne_raw.set_montage(mne.channels.make_standard_montage(self.montage))
        self.sequence = 0

    def get_path_name(self, file_name: str) -> str:
        dir_path = os.path.join(self.output_destination, f"{self.signal_serial}")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_name = self.get_file_name(file_name)
        return os.path.join(dir_path, file_name)
    
    def get_file_name(self, file_name: str):
        file_name = f"{self.sequence}-{file_name}"
        return file_name
    
    def write_json(self, file_name, data):
        with open(self.get_path_name(file_name), "w") as file:
            json.dump(data, file)
    
    @staticmethod
    def record_data(mne_driver, *args, **kwargs):
        raw_dict = {channel: list(data) for channel, data 
                    in zip(mne_driver.channels, mne_driver.channel_data_lists)}
        mne_driver.write_json("data.json", raw_dict)

    @staticmethod
    def plot_psd(mne_driver, *args, **kwargs):
        psd_fig = mne_driver.mne_raw.plot_psd(*args, **kwargs)
        if mne_driver.output_destination is not None:
            psd_fig.savefig(mne_driver.get_path_name("psd.png"))
        mne_driver.sequence += 1
        return mne_driver
    
    @staticmethod
    def plot_data(mne_driver, *args, **kwargs):
        data_fig = mne_driver.mne_raw.plot(*args, **kwargs)
        if mne_driver.output_destination is not None:
            data_fig.savefig(mne_driver.get_path_name("data.png"))
        mne_driver.sequence += 1
        return mne_driver
    
    @staticmethod
    def filter(mne_driver, *args, **kwargs):
        mne_driver.mne_raw.filter(*args, **kwargs)
        mne_driver.sequence += 1
        return mne_driver
    
    @staticmethod
    def ica(mne_driver, *args, **kwargs):
        
        return mne_driver

