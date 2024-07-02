import numpy as np
import mne

class MNEDriver:

    def __init__(
            self, 
            sample_rate: int,
            channels: list[str],
            channel_data_list: list[list[float]],
            ) -> None:
        
        self.channel_data_list = np.array(channel_data_list)
        self.sample_rate = sample_rate
        self.channels = channels
        
        if len(self.channels) != len(self.channel_data_list):
            raise ValueError("The number of channels must match the number of channel data lists.")

