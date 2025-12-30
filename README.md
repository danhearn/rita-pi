# IoT Pill Dispenser - rita-pi

A Raspberry Pi-based IoT pill dispenser with fingerprint authentication, automated dispensing, and hand detection.

## Features

- 🔐 **Fingerprint Authentication**: Secure access using UART capacitive fingerprint sensor
- 💊 **Automated Dispensing**: 3 stepper motors controlling 15-segment pill dispensers
- 👋 **Hand Detection**: Infrared sensor confirms pill was taken
- 🌐 **REST API**: FastAPI server for frontend integration
- 🎮 **Interactive Mode**: Command-line interface for testing

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

### Option 1: Interactive Mode (Testing)

Run the main script for interactive testing:

```bash
python3 main.py
```

Commands available:
- `1` - Verify Fingerprint (Unlock)
- `2` - Register New Fingerprint
- `3` - Dispense Pill
- `4` - Check Hand Detection
- `5` - Lock Device
- `6` - Show Status
- `0` - Exit

### Option 2: API Server (Production)

Start the FastAPI server:

```bash
# Development mode (with auto-reload)
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn api:app --host 0.0.0.0 --port 8000
```

API will be available at `http://<raspberry-pi-ip>:8000`

View API documentation at `http://<raspberry-pi-ip>:8000/docs`

### Option 3: Run Both (API + Monitoring)

Run API server in one terminal:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

Run monitoring script in another:
```bash
python3 main.py --monitor
```

## API Endpoints

### Device Status
- `GET /` - Health check
- `GET /status` - Get full device status

### Fingerprint Management
- `POST /fingerprint/register` - Register new fingerprint
- `GET /fingerprint/count` - Get registered fingerprint count
- `DELETE /fingerprint/clear-all` - Clear all fingerprints

### Device Control
- `POST /unlock` - Unlock device with fingerprint
- `POST /lock` - Lock device
- `POST /dispense` - Dispense pill (requires unlock)
  ```json
  {
    "motor_id": 1,
    "segment": 5
  }
  ```

### Hand Detection
- `GET /check-hand` - Check if hand is detected
- `POST /wait-for-pill-taken` - Wait for hand detection (with timeout)

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

## Example Frontend Integration

```javascript
// Unlock device
const unlock = async () => {
  const response = await fetch('http://raspberry-pi:8000/unlock', {
    method: 'POST'
  });
  const data = await response.json();
  console.log(data.message);
};

// Dispense pill
const dispensePill = async (motorId, segment) => {
  const response = await fetch('http://raspberry-pi:8000/dispense', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ motor_id: motorId, segment: segment })
  });
  return await response.json();
};

// Wait for pill to be taken
const waitForPill = async () => {
  const response = await fetch('http://raspberry-pi:8000/wait-for-pill-taken?timeout=30', {
    method: 'POST'
  });
  return await response.json();
};
```

## Typical Workflow

1. **Frontend** sends reminder to user to take pill
2. **User** places finger on sensor
3. **Frontend** calls `/unlock` endpoint
4. **Backend** verifies fingerprint and unlocks device
5. **Frontend** calls `/dispense` with motor and segment
6. **Backend** rotates motor to dispense pill
7. **Frontend** calls `/wait-for-pill-taken`
8. **Backend** monitors IR sensor for hand detection
9. **Frontend** receives confirmation and updates UI

## Troubleshooting

### Fingerprint sensor not responding
- Check serial port: `ls -l /dev/serial0`
- Verify UART is enabled in raspi-config
- Check wiring connections

### Motors not moving
- Verify I2C is enabled: `sudo i2cdetect -y 1`
- Check motor power supply
- Ensure Motor HAT is properly seated

### IR sensor always detecting
- Adjust sensor sensitivity with onboard potentiometer
- Check sensor orientation and distance

## License

MIT

## Author

Rita