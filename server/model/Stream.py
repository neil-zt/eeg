from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowError
import serial, threading, time
import numpy as np


class Stream:


    def __init__(
            self, 
            serial_port: int|None = None, 
            baud_rate: int|None = None,
            file_name: str|None = None,
            read_pause: float = 0.005,
            drop_last: int = 0,
            drop_first: int = 0,
            drop_header_rows: int = 0,
            board_type: str|None = None,
            ) -> None:
        
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.read_pause = read_pause
        self.drop_last = drop_last
        self.drop_first = drop_first
        self.drop_header_rows = drop_header_rows
        self.board_type = board_type
        
        if (file_name is not None and serial_port is not None) or (file_name is None and serial_port is None):
            raise ValueError("Exactly one of file_name or serial_port must be provided.")
        
        if serial_port is not None:
            if board_type is None:
                try:
                    self.serial = serial.Serial(self.serial_port, self.baud_rate)
                except Exception:
                    raise ValueError(f"Failed to connect to serial port {self.serial_port}. See README for trouble-shooting Exiting...")
            elif board_type == "Cyton":
                # Setup board parameters
                BoardShim.enable_dev_board_logger()
                self.board_params = BrainFlowInputParams()
                self.board_params.serial_port = self.serial_port  # Adjust this to your Cyton's serial port
                self.board_id = BoardIds.CYTON_BOARD.value

                # Initialize board
                self.board = BoardShim(self.board_id, self.board_params)
                self.board.prepare_session()

        else:
            self.file_name = file_name
            self.file = open(self.file_name, "r")


    def start(self):
        """
        Start a new thread to read the serial port.
        """
        if self.serial_port is not None:
            stream_method = None
            if self.board_type is None:
                stream_method = self.stream_general_serial
            elif self.board_type == "Cyton":
                stream_method = self.stream_cyton

            thread = threading.Thread(target=stream_method)
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

        
    def stream_cyton(self):
        """
        This function reads the serial port which is specifically connected to a
        Cyton board. The way it reads in data helps to ensure there are no skips 
        or duplicates. A pipeline must be provided that is a list of functions 
        to be called sequentially on the incoming signal.
        """
        self.board.start_stream()

        # Use a variable to track the last processed timestamp
        last_timestamp = 0

        while True:
            # Get all available data from the board
            try:
                data = self.board.get_board_data()  # This retrieves all data since the last call
            except BrainFlowError as e:
                print(f"Failed to retrieve data for this iteration. Continuing onto the next iteration.")
                continue
            
            if data.shape[1] > 0:
                # Get timestamps and find indices of new data since last_timestamp
                timestamps = data[BoardShim.get_timestamp_channel(self.board_id)]
                new_data_indices = timestamps > last_timestamp
                
                if np.any(new_data_indices):
                    # Update last processed timestamp
                    last_timestamp = timestamps[new_data_indices][-1]
                    
                    # Get new data
                    eeg_channels = BoardShim.get_eeg_channels(self.board_id)
                    new_data = data[eeg_channels][:, new_data_indices]
                
                    # Process new data
                    for i in range(new_data.shape[1]):
                        signals = ",".join([str(x) for x in new_data[:, i].tolist()])   # Make a comma-separated line of values
                        # print(signals, "\n")

                        # We have obtained the clean signal. Now we process
                        # the signal by running the pipeline provided. 
                        for processor in self.pipeline:
                            if type(processor) is tuple:
                                processor[0](signals, **processor[1])
                            else:
                                processor(signals)

                else:
                    print("No new data.")
            else:
                print("No data available.")
        
            # Sleep a little to prevent high CPU usage, adjust as necessary
            time.sleep(self.read_pause)


    def stream_general_serial(self):
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