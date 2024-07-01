# EEG Software 

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