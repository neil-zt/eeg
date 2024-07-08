import serial, threading, time


class Stream:

    def __init__(
            self, 
            serial_port: int = None, 
            baud_rate: int = None,
            file_name: str = None,
            read_pause: float = 0.001,
            drop_last: int = 0,
            drop_first: int = 0,
            drop_header_rows: int = 0,
            ) -> None:
        
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.read_pause = read_pause
        self.drop_last = drop_last
        self.drop_first = drop_first
        self.drop_header_rows = drop_header_rows
        
        if (file_name is not None and serial_port is not None) \
                or (file_name is None and serial_port is None):
            raise ValueError("Exactly one of file_name or serial_port must be provided.")
        else:
            if serial_port is not None:
                try:
                    self.serial = serial.Serial(self.serial_port, self.baud_rate)
                except Exception:
                    raise ValueError(f"Failed to connect to serial port {self.serial_port}. See README for trouble-shooting Exiting...")
            else:
                self.file_name = file_name
                self.file = open(self.file_name, "r")

    def start(self):
        """
        Start a new thread to read the serial port.
        """
        if self.serial_port is not None:
            thread = threading.Thread(target=self.stream)
            thread.daemon = True
            thread.start()
        else:
            self.read()
    
    def read(self):
        """
        Read the file as if it were a stream, one signal at a time.
        """
        i = 0
        for line in self.file:
            if i < self.drop_header_rows:
                continue
            signals = ",".join(line.split(",")[self.drop_first:-self.drop_last])
            for processor in self.pipeline:
                if type(processor) is tuple:
                    processor[0](signals, **processor[1])
                else:
                    processor(signals)
            time.sleep(self.read_pause)
            i += 1
        
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
                        if type(processor) is tuple:
                            processor[0](signals, **processor[1])
                        else:
                            processor(signals)

    def onload(self, pipeline: list[callable]) -> None:
        self.pipeline = pipeline