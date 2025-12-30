"""
HTTP Polling Client for IoT Pill Dispenser
Connects to your hosted backend to receive commands and send status updates
"""

import time
import requests
import socket
from datetime import datetime
from typing import Optional

from hardware.fingerprint_sensor import FingerprintSensor
from hardware.infrared_sensor import InfraredSensor
from hardware.stepper_motor import StepperMotorController


class PollingClient:
    """Polls backend for commands and executes them"""
    
    def __init__(self, backend_url: str, device_id: str, poll_interval: int = 5):
        """
        Initialize polling client
        
        Args:
            backend_url: Your hosted backend URL (e.g., "https://your-app.com")
            device_id: Unique identifier for this device (e.g., "pi-001")
            poll_interval: How often to poll in seconds (default: 5)
        """
        self.backend_url = backend_url.rstrip('/')
        self.device_id = device_id
        self.poll_interval = poll_interval
        self.running = False
        
        # Initialize hardware
        print(f"Initializing device {device_id}...")
        self.fingerprint = FingerprintSensor()
        self.infrared = InfraredSensor()
        self.motors = StepperMotorController()
        print("✓ Hardware initialized")
        
        # Device state
        self.device_locked = True
    
    def get_local_ip(self):
        """Get device's local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "unknown"
    
    def poll_for_commands(self) -> Optional[dict]:
        """
        Poll backend for pending commands
        
        Expected backend endpoint: GET /api/devices/{device_id}/commands
        Expected response: 
            { "command": "dispense", "params": {...} } or { "command": null }
        """
        try:
            response = requests.get(
                f"{self.backend_url}/api/devices/{self.device_id}/commands",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data if data.get("command") else None
            
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Poll error: {e}")
            return None
    
    def send_status(self, status_type: str, data: dict):
        """
        Send status update to backend
        
        Backend endpoint: POST /api/devices/{device_id}/status
        """
        try:
            payload = {
                "device_id": self.device_id,
                "status_type": status_type,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            
            response = requests.post(
                f"{self.backend_url}/api/devices/{self.device_id}/status",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✓ Status sent: {status_type}")
            else:
                print(f"✗ Status failed: {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Send status error: {e}")
    
    def execute_command(self, command: dict):
        """Execute a command received from backend"""
        cmd = command.get("command")
        params = command.get("params", {})
        
        print(f"\n→ Executing: {cmd}")
        
        if cmd == "unlock":
            self._handle_unlock()
        
        elif cmd == "lock":
            self._handle_lock()
        
        elif cmd == "dispense":
            self._handle_dispense(params)
        
        elif cmd == "register_fingerprint":
            self._handle_register_fingerprint()
        
        elif cmd == "check_hand":
            self._handle_check_hand()
        
        else:
            print(f"✗ Unknown command: {cmd}")
            self.send_status("error", {"message": f"Unknown command: {cmd}"})
    
    def _handle_unlock(self):
        """Handle unlock command - wait for fingerprint"""
        print("Waiting for fingerprint...")
        result = self.fingerprint.verify_user()
        
        if result["success"]:
            self.device_locked = False
            print(f"✓ Unlocked (User {result['user_id']})")
            self.send_status("unlocked", {
                "user_id": result["user_id"],
                "message": result["message"]
            })
        else:
            print(f"✗ {result['message']}")
            self.send_status("unlock_failed", {"message": result["message"]})
    
    def _handle_lock(self):
        """Handle lock command"""
        self.device_locked = True
        print("✓ Locked")
        self.send_status("locked", {"message": "Device locked"})
    
    def _handle_dispense(self, params: dict):
        """Handle dispense command"""
        if self.device_locked:
            print("✗ Device is locked")
            self.send_status("error", {"message": "Device is locked"})
            return
        
        motor_id = params.get("motor_id")
        segment = params.get("segment")
        
        # Dispense pill
        result = self.motors.dispense_pill(motor_id, segment)
        
        if result["success"]:
            print(f"✓ Dispensed: Motor {motor_id}, Segment {segment}")
            
            # Wait for hand detection
            print("Waiting for hand...")
            hand_detected = self.infrared.wait_for_hand(timeout=30)
            
            if hand_detected:
                print("✓ Pill taken")
                self.send_status("pill_taken", {
                    "motor_id": motor_id,
                    "segment": segment,
                    "taken": True
                })
            else:
                print("⚠ No hand detected")
                self.send_status("pill_taken", {
                    "motor_id": motor_id,
                    "segment": segment,
                    "taken": False
                })
        else:
            print(f"✗ Dispense failed: {result['message']}")
            self.send_status("error", {"message": result["message"]})
    
    def _handle_register_fingerprint(self):
        """Handle fingerprint registration"""
        print("Registering fingerprint...")
        result = self.fingerprint.add_user()
        
        if result["success"]:
            print(f"✓ {result['message']}")
            self.send_status("fingerprint_registered", {
                "user_id": result["user_id"],
                "message": result["message"]
            })
        else:
            print(f"✗ {result['message']}")
            self.send_status("registration_failed", {"message": result["message"]})
    
    def _handle_check_hand(self):
        """Check if hand is detected"""
        detected = self.infrared.is_hand_detected()
        print(f"Hand detected: {detected}")
        self.send_status("hand_check", {"detected": detected})
    
    def send_heartbeat(self):
        """Send periodic heartbeat with device info"""
        try:
            payload = {
                "device_id": self.device_id,
                "timestamp": datetime.now().isoformat(),
                "ip_address": self.get_local_ip(),
                "locked": self.device_locked,
                "fingerprint_count": self.fingerprint.get_user_count()
            }
            
            requests.post(
                f"{self.backend_url}/api/devices/{self.device_id}/heartbeat",
                json=payload,
                timeout=5
            )
        
        except:
            pass  # Heartbeat failures are non-critical
    
    def start(self):
        """Start polling loop"""
        self.running = True
        print(f"\n{'='*50}")
        print(f"Polling Client Started")
        print(f"Backend: {self.backend_url}")
        print(f"Device ID: {self.device_id}")
        print(f"Poll Interval: {self.poll_interval}s")
        print(f"{'='*50}\n")
        
        # Send initial heartbeat
        self.send_heartbeat()
        
        heartbeat_counter = 0
        
        try:
            while self.running:
                # Poll for commands
                command = self.poll_for_commands()
                
                if command:
                    self.execute_command(command)
                
                # Send heartbeat every 60 seconds
                heartbeat_counter += 1
                if heartbeat_counter >= (60 / self.poll_interval):
                    self.send_heartbeat()
                    heartbeat_counter = 0
                
                # Wait before next poll
                time.sleep(self.poll_interval)
        
        except KeyboardInterrupt:
            print("\n\nShutting down...")
            self.stop()
    
    def stop(self):
        """Stop polling and cleanup"""
        self.running = False
        self.fingerprint.cleanup()
        self.infrared.cleanup()
        self.motors.release_all()
        print("✓ Cleanup complete")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python3 polling_client.py <backend_url> <device_id> [poll_interval]")
        print("Example: python3 polling_client.py https://your-app.com pi-001 5")
        sys.exit(1)
    
    backend_url = sys.argv[1]
    device_id = sys.argv[2]
    poll_interval = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    client = PollingClient(backend_url, device_id, poll_interval)
    client.start()
