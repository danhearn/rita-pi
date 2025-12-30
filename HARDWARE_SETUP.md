# Hardware Setup Guide - IoT Pill Dispenser

## Components Required

### 1. Raspberry Pi (any model with GPIO pins)
- Recommended: Raspberry Pi 4 Model B

### 2. Fingerprint Sensor
- **Model**: UART Capacitive Fingerprint Reader
- **Connections**:
  - VCC → 3.3V or 5V
  - GND → Ground
  - TX → RX (GPIO 15, /dev/serial0)
  - RX → TX (GPIO 14, /dev/serial0)
  - WAKE → GPIO 23
  - RST → GPIO 24

### 3. Infrared Sensor
- **Model**: IR obstacle detection sensor
- **Connections**:
  - VCC → 5V
  - GND → Ground
  - OUT → GPIO 25

### 4. Stepper Motors (3x)
- **Model**: Compatible with Adafruit MotorKit
- **Interface**: I2C Motor HAT
- **Connections**: 
  - Motor 1 → Stepper Port 1 (for segment dispenser 1)
  - Motor 2 → Stepper Port 2 (for segment dispenser 2)
  - Motor 3 → Stepper Port 3 (for segment dispenser 3)
  - I2C SDA → GPIO 2
  - I2C SCL → GPIO 3
  - VCC → 5V (motor power supply)
  - GND → Ground

## GPIO Pin Summary

| Component | GPIO Pin | BCM Number | Purpose |
|-----------|----------|------------|---------|
| Fingerprint WAKE | Pin 16 | GPIO 23 | Wake signal |
| Fingerprint RST | Pin 18 | GPIO 24 | Reset |
| Infrared Sensor | Pin 22 | GPIO 25 | Detection signal |
| I2C SDA | Pin 3 | GPIO 2 | Motor control |
| I2C SCL | Pin 5 | GPIO 3 | Motor control |

## Software Requirements

```bash
# Enable I2C and Serial on Raspberry Pi
sudo raspi-config
# Navigate to Interface Options → I2C → Enable
# Navigate to Interface Options → Serial → Disable login shell, Enable serial port

# Install Python dependencies
pip3 install -r requirements.txt
```

## Hardware Notes

### Stepper Motor Configuration
- Each motor controls a rotating segment dispenser with 15 compartments
- 1 full rotation = 360 degrees
- Each segment = 360/15 = 24 degrees
- Steps per segment depends on motor (typically 200 steps/rotation for 1.8° stepper)
- Steps for one segment ≈ 200/15 ≈ 13-14 steps

### Infrared Sensor
- Active LOW (outputs 0 when hand detected)
- Detection range: typically 2-30cm (adjustable with potentiometer)
- Position sensor below pill dispenser outlet

### Fingerprint Sensor
- Can store up to 1000 fingerprints
- IDs 1-3 are typically reserved as "master users"
- Automatic wake-up feature available in sleep mode

## Power Considerations

- Stepper motors require adequate power supply (external power recommended)
- Total current draw can exceed 2A with all motors running
- Use separate power supply for motors if needed
- Ensure common ground between Raspberry Pi and motor power supply

## Testing Individual Components

```bash
# Test infrared sensor
python3 tests/infrared_sensor_test.py

# Test fingerprint sensor
python3 tests/UART-Fignerprint-RaspberryPi/main.py
```
