# Backend API Endpoints Guide

Your hosted backend needs these 3 simple endpoints for the Pi to connect to:

## 1. Get Commands (Polled by Pi)
```
GET /api/devices/{device_id}/commands
```

**Response when there's a command:**
```json
{
  "command": "dispense",
  "params": {
    "motor_id": 1,
    "segment": 5
  }
}
```

**Response when no commands:**
```json
{
  "command": null
}
```

**Available commands:**
- `"unlock"` - Wait for fingerprint to unlock
- `"lock"` - Lock the device
- `"dispense"` - Dispense pill (params: motor_id, segment)
- `"register_fingerprint"` - Register new fingerprint
- `"check_hand"` - Check if hand is present

## 2. Receive Status (Sent by Pi)
```
POST /api/devices/{device_id}/status
```

**Request body:**
```json
{
  "device_id": "pi-001",
  "status_type": "pill_taken",
  "timestamp": "2025-12-30T14:30:00",
  "data": {
    "motor_id": 1,
    "segment": 5,
    "taken": true
  }
}
```

**Status types you'll receive:**
- `"unlocked"` - Device unlocked (includes user_id)
- `"unlock_failed"` - Fingerprint verification failed
- `"locked"` - Device locked
- `"pill_taken"` - Pill dispensed and taken (or not)
- `"fingerprint_registered"` - New fingerprint added
- `"registration_failed"` - Fingerprint registration failed
- `"hand_check"` - Hand detection result
- `"error"` - Any error occurred

## 3. Heartbeat (Sent by Pi every 60s)
```
POST /api/devices/{device_id}/heartbeat
```

**Request body:**
```json
{
  "device_id": "pi-001",
  "timestamp": "2025-12-30T14:30:00",
  "ip_address": "192.168.1.50",
  "locked": true,
  "fingerprint_count": 3
}
```

---

## Usage on Raspberry Pi

**Run the polling client:**
```bash
python3 polling_client.py https://your-app.com pi-001 5
```

Arguments:
1. Your backend URL
2. Device ID (unique identifier)
3. Poll interval in seconds (optional, default: 5)

**Example workflow:**

1. User opens your app/website
2. App tells backend: "dispense pill from motor 1, segment 5"
3. Backend stores this command in queue/database
4. Pi polls: `GET /api/devices/pi-001/commands`
5. Backend responds with the dispense command
6. Pi dispenses pill and waits for hand
7. Pi sends status: `POST /api/devices/pi-001/status` (pill_taken: true)
8. Backend updates UI: "Pill taken ✓"

---

## Run Alongside FastAPI (Optional)

You can run both the polling client AND the local FastAPI server:

**Terminal 1 (Local API for debugging):**
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

**Terminal 2 (Polling client):**
```bash
python3 polling_client.py https://your-app.com pi-001
```

This lets you test locally with the API while also being connected to your backend.
