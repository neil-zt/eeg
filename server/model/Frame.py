from collections import deque
from datetime import datetime
import multiprocessing, os, json
from model.MNEDriver import MNEDriver
from model.Server import Server
from datetime import datetime

class Frame:
    """
    The Frame class is the top-level data structure that holds all incoming EEG data. 
    At its core, it uses a deque to store incoming signal values, hold the values for
    a fixed period of time, and then delete the oldest values. For every specified 
    period, the Frame processes the stored signal values and makes the statistics 
    available to an external observer (usually an API).
    """

    def __init__(
            self, 
            channels: str,
            sample_rate: int, 
            max_cache_samples: int,
            window_size_samples: int,
            output_directory: str,
            montage: str = "standard_1020",
            channel_types: list[str]|None = None,
            server: Server|None = None
            ) -> None:
        
        self.sample_rate = sample_rate                      # Number of samples per second
        self.channels = channels                            # List of channel names
        self.channel_data = {                               # Dictionary of channels and their data
                channel: deque(maxlen=max_cache_samples) 
            for channel in channels}
        self.clock = 0                                      # Incremented for every new signal
        self.pipeline = []                                  # List of functions to process signals
        self.window_size_samples = window_size_samples      # Number of samples per window
        self.timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.output_directory = output_directory            # Directory to store results
        self.output_destination = os.path.join(self.output_directory, self.timestamp)
        self.montage = montage
        self.channel_types = channel_types
        self.last_window_begin_time = None

        os.makedirs(self.output_destination, exist_ok=True)
        if server is not None:
            server.inject_output_destination_name(self.output_destination)

    def add_singal(self, signals: str) -> None:
        """
        Add new signals to the frame. If max_cache_seconds is reached, the oldest signals
        are removed. The signals shall be comma-separated values from different channels.
        """
        signals =signals.strip(",")
        signals_list = signals.split(",")
        if len(signals_list) < len(self.channels):
            raise ValueError("The number of signals must >= the number of channels.")
        for i, _ in enumerate(self.channels):
            self.channel_data[self.channels[i]].append(signals_list[i])

        if self.clock % self.window_size_samples == 0:
            current_time = str(datetime.now().time())
            self.last_window_begin_time = current_time

        if (self.clock + 1) % self.window_size_samples == 0:
            self.do_wrap(window_begin_time=str(self.last_window_begin_time))        # Force string copying
        self.clock += 1

    def wrap(self, pipeline: list[callable]) -> None:
        """
        For every window_size_samples, the Frame processes the latest signal values, 
        performs analyses, and makes the results available to an external observer.
        """
        self.pipeline = pipeline

    def _process_wrap_pipeline(self, channel_lists, window_begin_time:str|None = None) -> None:
        mne_driver = MNEDriver(
            sample_rate=self.sample_rate,
            channels=self.channels,
            channel_types=self.channel_types,
            channel_data_lists=channel_lists,
            output_destination=self.output_destination,
            signal_serial=self.clock,
            montage=self.montage,
            window_begin_time=window_begin_time
        )

        for processor in self.pipeline:
            # print(window_begin_time)
            if type(processor) is tuple:
                if processor[1].get("cascade_output", False):
                    processor[1]["output_destination"] = self.output_destination
                    processor[1]["signal_serial"] = self.clock
                processor[0](mne_driver, **processor[1])
            else:
                processor(mne_driver)
        
    def do_wrap(self, window_begin_time:str|None = None) -> None:
        """
        Perform the processing of the signal values, as defined by Frame.wrap(pipeline).
        This function will now spawn a new process and run the pipeline in that process,
        allowing parallel computation.
        """
        channel_lists = [list(self.channel_data[channel])[-self.window_size_samples:] 
                         for channel in self.channels]

        # Create a new process targeting the process_pipeline method
        process = multiprocessing.Process(
            target=self._process_wrap_pipeline,
            args=(channel_lists, window_begin_time))
        process.start()     # Start the process
        # process.join()    # Shouldn't need this for now


