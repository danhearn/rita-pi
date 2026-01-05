# Rita Pill Dispenser - rita-pi

The following two steps will allow you to setup the PI on a new wifi network and run the test environment program:

## Connect to New WiFi Network:

1. On Android or iOS download the `BTBerryWifi` app from the app store. 

2. Turn on the raspberry pi. 

3. On the BTBerryWiFi app scan for devices and select `rita`.

4. Login to your chosen wifi network.

## To run the program:

1. open terminal on the raspberry pi either using a screen keyboard and mouse, through SSH, or Raspberry Pi Connect (ask Dan for login details). 
2. paste this into the terminal and press enter
   ```bash
      bash ~/Documents/GitHub/rita-pi/start-rita.sh
   ```

The program will start. Navitgate to https://rita-pi-five.vercel.app/ to control the device. 
   
# Prototype Documentation

## Features

-  **Fingerprint Authentication**: Secure access using UART capacitive fingerprint sensor
-  **Automated Dispensing**: 3 stepper motors controlling 15-segment pill dispensers
-  **Hand Detection**: Infrared sensor confirms pill was taken
-  **HTTP Polling Client**: Connects to hosted backend to receive commands
-  **Network Agnostic**: Works across any WiFi network without IP configuration

## Hardware Components

- Raspberry Pi (any model with GPIO)
- UART Capacitive Fingerprint Reader
- IR Obstacle Detection Sensor
- 3x Stepper Motors with Adafruit Motor HAT
- 15-segment rotating pill dispensers

See [HARDWARE_SETUP.md](HARDWARE_SETUP.md) for detailed wiring instructions.

## Installation


### 1. Enable Required Interfaces

```bash
sudo raspi-config
# Enable I2C: Interface Options → I2C → Enable
# Enable Serial: Interface Options → Serial → Disable login shell, Enable serial port
```

### 2. Install Dependencies

Python version 3.11 currently only supported 

```bash
cd /home/rita/Documents/GitHub/rita-pi
pip3 install -r requirements.txt
```

### 3. Test Hardware Components

```bash
# Test infrared sensor
python3 tests/infrared_sensor_test.py

# Test fingerprint sensor
python3 tests/UART-Fignerprint-RaspberryPi/main.py
```

## Usage

### Running the Polling Client (Production)

The device connects to your hosted backend and polls for commands:

```bash
python3 polling_client.py <backend-url> <device-id> [poll-interval]
```

**Arguments:**
- `backend-url`: Your hosted backend URL [(testing-app)](https://rita-pi-five.vercel.app/)
- `device-id`: Unique identifier for this device (e.g., pi-001)
- `poll-interval`: How often to check for commands in seconds (default: 5)

The client will:
- Poll your backend every 5 seconds for new commands
- Execute commands (unlock, dispense, register fingerprint, etc.)
- Send status updates back to your backend
- Send heartbeat every 60 seconds

### Backend Requirements

Your hosted backend needs to implement 3 endpoints. See [BACKEND_API.md](BACKEND_API.md) for full details:

1. **GET /api/devices/{device_id}/commands** - Device polls for commands
2. **POST /api/devices/{device_id}/status** - Device sends status updates
3. **POST /api/devices/{device_id}/heartbeat** - Device sends periodic heartbeat

### Available Commands

Commands your backend can send to the device:

- `unlock` - Wait for fingerprint to unlock device
- `lock` - Lock the device
- `dispense` - Dispense pill from motor and segment
- `register_fingerprint` - Register new fingerprint
- `check_hand` - Check if hand is detected

## Project Structure

```
rita-pi/
├── hardware/
│   ├── fingerprint_sensor.py  # Fingerprint sensor interface
│   ├── infrared_sensor.py     # IR sensor interface
│   └── stepper_motor.py       # Motor controller
├── tests/
│   ├── infrared_sensor_test.py
│   └── UART-Fignerprint-RaspberryPi/
├── api.py                     # FastAPI server
├── main.py                    # Main control loop
├── requirements.txt
├── HARDWARE_SETUP.md          # Detailed hardware guide
└── README.md
```
