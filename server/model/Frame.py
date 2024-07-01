class Frame:
    """
    The Frame class is the top-level data structure that holds all incoming EEG data. 
    At its core, it uses a deque to store incoming signal values, hold the values for
    a fixed period of time, and then delete the oldest values. For every specified 
    period, the Frame processes the stored signal values and makes the statistics 
    available to an external observer (usually an API).
    """

    def __init__(self) -> None:
        pass