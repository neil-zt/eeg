# EEG Software 

The EEG Software repository contains everything (so far) that is needed to (1) Record signals through our Arduino-compatible development board, and (2) Dynamically stream EEG signals either from an Arduino serial connection or a static file, and analyze and visualize the data accordingly. Code for these two objectives are separated into two root-level directories: 

- (1) [Arduino Code](/board/)
- (2) [Python DSP Code](/server/)

The Arduino code is self-explanatory and will not be elaborated in this document. The below documentation explains how the Python directory shall be used or set up. 

## Setup and Configuration 

### Get the Repository

You can get the repository by downloading it, or cloning it via `git clone`. 

### Python Virtual Environment (Optional)

If you would like, you can also create a Python virtual environment so that this repository does not stain your original environment. Do so by following Python's [official documentation](https://docs.python.org/3/library/venv.html). It is recommended that you put the virtual environment inside the `/server/` directory. 

### Installing Required Dependencies 

The required depenencies used here are listed inside `/server/requirements.txt`. This file is the standard dependency file for Python. To install all the dependencies, simply run: 

```sh
pip install -r server/requirements.txt
```

You are good to go after installing the dependencies. 

## Systems Descriptions 

![EEG Software Systems Graph](/asset/systems.png)

Inspired by MVC paradigms commonly used in servers, in this Python system there are several classes, each called a model and representing a system block in the above diagram. Descriptions of each model (class) and its functionalities are as follows: 

- **Server Control**: The `Server` Class
    - Responds to external requests and keeps all processes running.
- **Stream Control**: The `Stream` Class
    - Receives signals from a serial port, be it USB or Bluetooth. 
    - Reads signals from a static file containing prerecorded signals. 
- **Data Frame Control**: The `Frame` Class
    - Turns realtime high-frequency data into packets of information. 
    - Caches and auto-removes the signals recorded. 
- **MNE Driver**: The `MNEDriver` Class
    - Helps the `Frame` Class invoke APIs of the MNE package. 


## Data Formats 

### Streaming from Arduino

The communication between Arduino and the Python server through the serial port must follow, at least under the current implementation, the format `||<serial>|<comma-separated-channel-values>`. For example, a snippet of the serial message may look like:

```
||36|0.01,0.034,0.07,0.11, ...
||37|0.01,0.034,0.07,0.11, ...
||38|0.01,0.034,0.07,0.11, ...
||39|0.01,0.034,0.07,0.11, ...
```

The `<serial>` number shall be an integer. It can be a repeating integer, meaning that, for example, it can go `1, 2, 3, ..., 98, 99, 100, 1, 2, 3, ...`. Such implementation allows the Python program to wait for any skips and smoothens any mismatches between reading and receiving frequencies. Examples of Arduino code to produce this format have been provided in the `/board` directory. 


### Reading from Static Files 

This Python program reads in only `.csv` files. If you encounter other file types for EEG signals such as the European data format `.edf`, you can use the provided tools such as `server/tools/edf_to_csv.py`, as explained later. Either way, the `.csv` file must by in the following format, in which each channel exists in exactly one column. 

```
0.01,0.034,0.07,0.11, ...
0.01,0.034,0.07,0.11, ...
0.01,0.034,0.07,0.11, ...
0.01,0.034,0.07,0.11, ...
```

If there are header rows, header columns, or tailing columns, you can drop them automatically, which will also be described later. 

## Usage 

### Streaming from Arduino 

The example script for straming from Arduino can be found in `/server/realtime.py`. Below is a walkthrough of the configurations used there. First, we create a `Frame` object that is supposed to hold signals from multiple channels. Particularly note that `window_size_samples` defines how many datapoints shall be packed into a single window and analyzed together.  

```python
frame = Frame(
    channels=["Fp1", "Fp2", "F3", "F4", "F7", "F8", "C3", "C4"],
    sample_rate=125,
    max_cache_samples=125,
    window_size_samples=60,
    output_directory="./server/results", )
```

Then, we define how the `frame` processes the data. In this case, for every `125` signals received, the frame invokes the following processes: (1) Plot the data, (2) Plot the power spectral density, (3) Filter the data, (4) Plot the power spectral density, and (5) Filter the data. Notice that parameters can be passed in as a dictionary binded in the same tuple with the function, as in `(MNEDriver.filter, {"l_freq": 15, "h_freq": 45})`. 

```python
frame.wrap(pipeline=[ 
    MNEDriver.plot_data,
    MNEDriver.plot_psd,
    (MNEDriver.filter, {"l_freq": 15, "h_freq": 45}),
    MNEDriver.plot_data,
    MNEDriver.plot_psd,
])
```

Afterwards, we create a `Stream` object by passing in where we intend to read the stream from. Methods to get the serial port name have been documented in the [appendix](#other-guides). 

```python
stream = Stream(
    serial_port='/dev/tty.usbserial-2110',
    baud_rate=9600, )
```

Then, similar to how we defined the pipeline of processing before, we can define the pipeline of what to do to the signals read in. In our system, we want to add that new signal to the `frame`; as an example, we want to print that signal out. We first add the methods to the pipelines, and then start the stream. 

```python
stream.onload(pipeline=[ print, frame.add_singal ])
stream.start()
```

Lastly, we start the server using the below code. *Note* that depending on the environment, the code might terminate immediately after you start the program if you do not start the server. This is because we are running the stream on another thread, and if we do not start the server, the main thread ends immediately, causing the alternate thread to also end. 

```python
server = Server(host="0.0.0.0", port=8000)
server.run()
```

## Appendix

### Common Errors 

- **Concurrent Serial Read**
    The serial port can only be read by one process at a time. Make sure that:
    - No two or more instances of the server are running.
    - The **Serial Monitor** panel in the Arduino IDE is closed.

### Other Guides 

- **Searching for Serial Port Name**
    You can view the port name in the Arduino IDE, or using the following methods:
    - **Windows**: Open the Device Manager, and look for the port name under `Ports (COM & LPT)`.
    - **Linux**: `ls /dev/tty*`
    - **Mac**: `ls /dev/tty.*`
