from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import time, argparse


def main(serial_port, time_length):

    # Initialize parameters
    params = BrainFlowInputParams()
    params.serial_port = serial_port  # Adjust this to your Cyton's serial port
    board_id = BoardIds.CYTON_BOARD.value

    # Prepare the board
    BoardShim.enable_dev_board_logger()
    board = BoardShim(board_id, params)
    board.prepare_session()

    # Start streaming
    board.start_stream()
    BoardShim.log_message(1, 'Start streaming...')

    # Capture data for 10 seconds
    time.sleep(time_length)
    data = board.get_board_data()  # You can fetch data periodically or based on some triggers

    print(data)

    # Stop the stream
    board.stop_stream()
    board.release_session()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stream data from the Cyton board for a static amount of time.')
    parser.add_argument('serial_port', type=str, help='Name of the serial port you are streaming from.')
    parser.add_argument('time', type=float, help='The time length in seconds you are straming for.')
    args = parser.parse_args()

    main(args.serial_port, args.time)
