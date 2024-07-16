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

You are good to go after installing the dependencies. However, if during installation any error occurs, it is recommended that you install the dependencies one by one. In that case, you can run either one of `server/noise.py`, `server/realtime.py`, or `server/static.py` and see which dependencies are missing.

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

Two additional models are provided to facilitate the development process:

- **Noise Generator**: The `Noise` Class
    - Generates random noise signals for testing purposes.
- **Metrics**: The `Metrics` Class
    - Calculates metrics to assess the performance of the system, such as a recording's correlation to the ground truth. 


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

The example script for streaming from Arduino can be found in `/server/realtime.py`. Below is a walkthrough of the configurations used there. First, we create a `Frame` object that is supposed to hold signals from multiple channels. Particularly note that `window_size_samples` defines how many datapoints shall be packed into a single window and analyzed together.  

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

### Reading from Static Files 

If you wish to read in a static file instead of streaming realtime data, the only item that has to be changed is how we define the `Stream` instance. Other details remain the same as in the case of straming from Arduino. 

```python
stream = Stream(
    file_name="./server/sample_data/eeg-alpha-waves/subject_11.csv",
    read_pause=0.00,
    drop_last=2,
    drop_first=1, )
```

Here, the parameter `read_pause` is the time paused between reading in two consecutive signals. This parameter exists for scenarios where we want to simulate real time data, but from a static, fixed file. Additionally, `drop_last` and `drop_first` allow us to disregard the first or last columns of a `.csv` file. 

### Generating Noise and Using Metrics

For testing purposes, you can generate noise signals using the `Noise` class, and evaluate your system using the ``Metrics`` class. The following code snippets are from the `server/noise.py` file. We have previously seen that you can use `Frame.wrap` to define a pipeline of processing. During the pipeline, you can add the noise signals to the frame. Simply add the method to the pipeline as below:

```python
frame.wrap(pipeline=[ 
    (MNEDriver.plot_data, {"scalings": 30}),
    (Noise.add_noise, {"scale": 0.001, "sin_frequency": 60}),
    (MNEDriver.plot_data, {"scalings": 30}),
    (MNEDriver.notch_filter, {"freqs": [60]}),
    (MNEDriver.plot_data, {"scalings": 30}),
])
```

In this example, we define that during each pipeline cycle, we first plot out the EEG signals, then add noise to the signals, and then plot out the signals again. Later, we apply a notch filter to try filtering out the noise we just added, and plot the signals again. During this process, you may want to record the signals at specific stages of the pipeline. To do so, you can use the `Metrics.take_snapshot` method, adding it to the pipeline:

```python
recorder = Metrics()
frame.wrap(pipeline=[ 
    (MNEDriver.plot_data, {"scalings": 30}),
    (Metrics.take_snapshot, {"metrics": recorder, "name": "original"}),

    (Noise.add_noise, {"scale": 0.001, "sin_frequency": 60}),
    (MNEDriver.plot_data, {"scalings": 30}),
    (Metrics.take_snapshot, {"metrics": recorder, "name": "noisy"}),

    (MNEDriver.notch_filter, {"freqs": [60]}),
    (MNEDriver.plot_data, {"scalings": 30}),
    (Metrics.take_snapshot, {"metrics": recorder, "name": "filtered"}),


    (Metrics.record_pearson_correlation, {"metrics": recorder, 
                                            "snapshots": ["original", "noisy"],
                                            "cascade_output": True}),
    (Metrics.record_pearson_correlation, {"metrics": recorder, 
                                            "snapshots": ["original", "filtered"],
                                            "cascade_output": True}),
])
```

When taking snapshots, you can specify the name of it. For example, the snapshot of the original data is named `original`, the snapshot of the noisy data is named `noisy`, and the snapshot of the filtered data is named `filtered`. After taking the snapshots, you can calculate the Pearson correlation between among the snapshots, as seem in the last two lines of the pipeline. The `cascade_output` parameter allows you to write out the correlation results as they are calculated.


### Tools 

Additional tools have also been provided to facilitate the development process. These tools are written in Python and are located in the `/server/tools/` directory. Below are the instructions on how to use them. These instructions assume that we are already inside the tools directory with `cd server/tools`. Also note that depending on your Python configuration, the prefix command `python3` might by `python` or something else. 

- **EDF to CSV** `edf_to_csv.py`
    This tool converts the EDF `.edf` EEG signal file into a `.csv` file. 
    ```sh
    python3 edf_to_csv.py <source-file-path> <destination-file-path>
    ```

- **OpenSignals to CSV** `opensignals_to_csv.py`
    This tool converts the OpenSignals `.txt` EEG signal file into a `.csv` file. 
    ```sh
    python3 opensignals_to_csv.py <source-file-path> <destination-file-path>
    ```
    

## Appendix

### Common Errors 

- **Concurrent Serial Read**
    The serial port can only be read by one process at a time. Make sure that:
    - No two or more instances of the server are running.
    - The **Serial Monitor** panel in the Arduino IDE is closed.

### Searching for Serial Port Name

You can view the port name in the Arduino IDE, or using the following methods:
- **Windows**: Open the Device Manager, and look for the port name under `Ports (COM & LPT)`.
- **Linux**: `ls /dev/tty*`
- **Mac**: `ls /dev/tty.*`

### Reading OpenSignals Data 

OpenSignals devices output files in the `.txt` format. You may want to convert it to a `.csv` file which this system can process using a tool provided in this repository, as outlined above in the [Tools](#tools) section. If you would like to read the data yourself, use any text editor to open the file, and observe something similar to this:

```txt
# OpenSignals Text File Format. Version 1
# <--Some-JSON-->
# EndOfHeader
0   0   18  ...
1   0   20  ...
2   0   49  ...
3   0   32  ...
...
```

The header rows are prefixed with `#`, and the data rows are tab-separated. If you extend the JSON header (the second line in the above example), you may see something like the below JSON. Particularly note that the `column` key describes what each column in the data rows represent. For details, visit OpenSignals' [official documentation](https://support.pluxbiosignals.com/knowledge-base/opensignals-sensor-file-specifications-txt-format/).

```json
{
  "00:07:80:8C:08:EB": {
    "sampling rate": 1000,
    "resolution": [
      16
    ],
    "channels": [
      3
    ],
    "sensor": [
      "EDA"
    ],
    "label": [
      "CH3"
    ],
    "column": [
      "nSeq",
      "DI",
      "CH3"
    ]
  }
}
```
