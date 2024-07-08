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

## Data Formats 

### Streaming from Arduino

The communication between Arduino and the Python server through the serial port must follow, at least under the current implementation, the format `||<serial>|<comma-separated-channel-values>`. For example, a snippet of the signal may look like:

```
||36|0.01,0.034,0.07,0.11, ...
||37|0.01,0.034,0.07,0.11, ...
||38|0.01,0.034,0.07,0.11, ...
||39|0.01,0.034,0.07,0.11, ...
```

The `<serial>` number shall be an integer. It can be a repeating integer, meaning that, for example, it can go `1, 2, 3, ..., 98, 99, 100, 1, 2, 3, ...`. Such implementation allows the Python program to wait for any skips and smoothens any mismatches between reading and receiving frequencies. Examples of such code implementation have been provided in the `/board` directory. 


## Drafts 

### Notices 

1. **Update the `SERIAL_PORT` variable in `server.py`** 
    Depending on the serial port of the device, the variable has to be changed. You can view the port name in the Arduino IDE, or using the following methods:
    - **Windows**: Open the Device Manager, and look for the port name under `Ports (COM & LPT)`.
    - **Linux**:
        ```bash
        ls /dev/tty*
        ```
    - **Mac**:
        ```bash
        ls /dev/tty.*
        ```

2. **No Concurrent Read**
    The serial port can only be read by one process at a time. Make sure that:
    - No two or more instances of the server are running.
    - The **Serial Monitor** panel in the Arduino IDE is closed.