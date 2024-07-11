import numpy as np
import os, json
from model.MNEDriver import MNEDriver

class Metrics:

    """
    The Metrics class can be used to calculate and assess the performance of 
    the signal processing pipeline. During the processing pipeline, we can 
    take snapshots of the current signal values, and later compare them with
    another snapshot, thereby calculating the performance of the pipeline.
    """

    def __init__(self) -> None:
        self.snapshots: dict[str, np.ndarray]  = dict()

    @staticmethod
    def take_snapshot(mne_driver, metrics, name, **kwargs) -> None:
        """
        Take a snapshot of the current signal values.
        """
        metrics.snapshots[name] = mne_driver.channel_data_lists.copy()

    @staticmethod
    def clear_snapshots(mne_driver, metrics, **kwargs) -> None:
        """
        Clear all the snapshots.
        """
        metrics.snapshots = dict()

    @staticmethod
    def get_path_name(file_name: str, output_destination: str, signal_serial: int) -> str:
        dir_path = os.path.join(output_destination, f"{signal_serial}")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return os.path.join(dir_path, file_name)
    
    @staticmethod
    def write_json(file_name: str, output_destination: str, signal_serial: int, data) -> None:
        with open(Metrics.get_path_name(file_name, output_destination, signal_serial), "w") as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def record_pearson_correlation(mne_driver: MNEDriver, metrics, snapshots, output_destination=None, signal_serial=None, **kwargs) -> None:
        """
        Record the Pearson correlation between two snapshots.
        """
        
        if len(snapshots) != 2:
            raise ValueError("The number of snapshots must be 2.")
        snapshot1, snapshot2 = metrics.snapshots[snapshots[0]], metrics.snapshots[snapshots[1]]

        for i in range(len(snapshot1)):
            if len(snapshot1[i]) != len(snapshot2[i]):
                raise ValueError("The number of samples in the snapshots must be equal.")

        # Calculate a correlation coefficient for each channel
        pearson_correlations = dict()
        for i in range(len(snapshot1)):
            pearson_correlations[mne_driver.channels[i]] = np.corrcoef(snapshot1[i], snapshot2[i])[0, 1]

        Metrics.write_json(f"pearson-{snapshots[0]}-{snapshots[1]}.json", 
                           output_destination, signal_serial, pearson_correlations)

    