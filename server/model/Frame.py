from collections import deque

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
            ) -> None:
        
        self.channels = channels                            # List of channel names
        self.sample_rate = sample_rate                      # Number of samples per second
        self.channel_data = {                               # Dictionary of channels and their data
                channel: deque(maxlen=max_cache_samples) 
            for channel in channels}
        self.clock = 0                                      # Incremented for every new signal
        self.packaged = []                                  # List of packaged signals (produces of wrap)
        self.pipeline = []                                  # List of functions to process signals
        self.window_size_samples = window_size_samples      # Number of samples per window

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

    def do_wrap(self) -> None:
        """
        Perform the processing of the signal values, as defined by Frame.wrap(pipeline).
        """
        for processor in self.pipeline:
            processor(self.channel_data)

