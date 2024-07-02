from collections import deque
from datetime import datetime
import multiprocessing, os, json

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
        self.output_directory = output_directory             # Directory to store results
        self.output_destination = os.path.join(self.output_directory, self.timestamp)
        os.makedirs(self.output_destination, exist_ok=True)

    def add_singal(self, signals: str) -> None:
        """
        Add new signals to the frame. If max_cache_seconds is reached, the oldest signals
        are removed. The signals shall be comma-separated values from different channels.
        """
        for i, signal in enumerate(signals.split(",")):
            if i >= len(self.channels):
                break
            if signal == "":
                continue
            self.channel_data[self.channels[i]].append(signal)

        if (self.clock + 1) % self.window_size_samples == 0:
            self.do_wrap()
        self.clock += 1

    def wrap(self, pipeline: list[callable]) -> None:
        """
        For every window_size_samples, the Frame processes the latest signal values, 
        performs analyses, and makes the results available to an external observer.
        """
        self.pipeline = pipeline

    def _process_wrap_pipeline(self, channel_lists) -> None:
        results = {}
        results["raw"] = {channel: list(data) for channel, data in zip(self.channels, channel_lists)}
        for processor in self.pipeline:
            processor(self.channel_data)
        
        self.write_packaged_data(results)

    def do_wrap(self) -> None:
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
            args=(channel_lists,))
        process.start()     # Start the process
        # process.join()    # Shouldn't need this for now

    def write_packaged_data(self, data: dict):
        """
        After each wrap, write the processed data to a file in json format where 
        both the analyzed and raw data are packaged. 
        """
        with open(os.path.join(self.output_destination, f"{self.clock}.json"), "w") as file:
            file.write(json.dumps(data))


