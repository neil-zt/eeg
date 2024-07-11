import numpy as np
from model.MNEDriver import MNEDriver
# from MNEDriver import MNEDriver

class Noise:

    def __init__(self) -> None:
        raise TypeError("The Noise class is a static class, and cannot be initialized.")
    
    @staticmethod
    def add_noise(mne_driver: MNEDriver, **kwargs) -> None:
        """
        Add noise to the EEG data.
        """
        scale = kwargs.get("scale", 0.1)        # The magnitude of the noise w.r.t. the average magnitude of the signal
        magnitude = mne_driver.get_average_signal() * scale
        sample_rate = mne_driver.sample_rate
        num_samples = mne_driver.num_samples

        noises = np.zeros(num_samples)
        sin_frequency = kwargs.get("sin_frequency", None)
        if sin_frequency:
            noises += Noise.sin(sin_frequency, magnitude, sample_rate, num_samples)

        channel_data_lists = mne_driver.channel_data_lists
        for i in range(mne_driver.num_channels):
            channel_data_lists[i] += noises
        mne_driver.re_init(channel_data_lists)


    @staticmethod
    def sin(frequency, magnitude, sample_rate, num_samples) -> np.ndarray:
        """
        Add power line interference to the EEG data.
        """
        t = np.arange(num_samples) / sample_rate
        return magnitude * np.sin(2 * np.pi * frequency * t)
    



