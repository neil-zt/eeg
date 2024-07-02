import serial, threading


class Stream:

    def __init__(
            self, 
            serial_port: int, 
            baud_rate: int,
            ) -> None:
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        try:
            self.serial = serial.Serial(self.serial_port, self.baud_rate)
        except Exception:
            raise ValueError(f"Failed to connect to serial port {self.serial_port}. See README for trouble-shooting Exiting...")

    def start(self):
        """
        Start a new thread to read the serial port.
        """
        thread = threading.Thread(target=self.stream)
        thread.daemon = True
        thread.start()

    def stream(self):
        """
        This function reads the serial port and processes the incoming data. The
        way it reads in data helps to ensure there are no skips or duplicates. A
        pipeline must be provided that is a list of functions to be called 
        sequentially on the incoming signal.
        """
        global latest_signal
        last_series_num = 0

        # Reads in the data while eliminating skips and duplicates
        while True:
            if self.serial.in_waiting > 0:
                packets = self.serial.readline().decode('utf-8').strip().split("||")
                if len(packets) == 0:
                    continue
                for packet in packets:
                    if packet == "":
                        continue
                    [series_num, signals] = packet.split("|")
                    if int(series_num) == last_series_num:
                        continue
                    last_series_num = int(series_num)

                    # We have obtained the clean signal. Now we process
                    # the signal by running the pipeline provided. 
                    for processor in self.pipeline:
                        processor(signals)

    def onload(self, pipeline: list[callable]) -> None:
        self.pipeline = pipeline