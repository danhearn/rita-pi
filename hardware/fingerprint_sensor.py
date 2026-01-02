"""
Fingerprint Sensor Module
Simplified interface for UART Capacitive Fingerprint Reader
"""

import serial
import time
import RPi.GPIO as GPIO
from hardware.audio_alerts import AudioPlayer

# Response codes
ACK_SUCCESS = 0x00
ACK_FAIL = 0x01
ACK_FULL = 0x04
ACK_NO_USER = 0x05
ACK_TIMEOUT = 0x08
ACK_GO_OUT = 0x0F

# Command codes
CMD_HEAD = 0xF5
CMD_TAIL = 0xF5
CMD_ADD_1 = 0x01
CMD_ADD_3 = 0x03
CMD_MATCH = 0x0C
CMD_DEL_ALL = 0x05
CMD_USER_CNT = 0x09
CMD_COM_LEV = 0x28

USER_MAX_CNT = 1000

# GPIO Pins
FINGER_WAKE_PIN = 23
FINGER_RST_PIN = 24


class FingerprintSensor:
    """Interface for fingerprint sensor operations"""
    
    def __init__(self, serial_port="/dev/serial0", baudrate=19200):
        """Initialize fingerprint sensor"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(FINGER_WAKE_PIN, GPIO.OUT, initial=GPIO.HIGH)  # Keep wake pin HIGH
        GPIO.setup(FINGER_RST_PIN, GPIO.OUT, initial=GPIO.HIGH)
        
        self.ser = serial.Serial(serial_port, baudrate)
        self.g_rx_buf = []
        
        # Reset module
        self._reset_module()
        
        # Set compare level to 5 (moderate - may need tuning)
        self._set_compare_level(5)
        
        self.audio_player = AudioPlayer()
    
    def _reset_module(self):
        """Reset the fingerprint module"""
        GPIO.output(FINGER_RST_PIN, GPIO.LOW)
        time.sleep(0.25)
        GPIO.output(FINGER_RST_PIN, GPIO.HIGH)
        time.sleep(0.25)
    
    def _tx_and_rx_cmd(self, command_buf, rx_bytes_need, timeout):
        """Send command and receive response"""
        checksum = 0
        tx_buf = bytearray()
        
        tx_buf.append(CMD_HEAD)
        for byte in command_buf:
            tx_buf.append(byte)
            checksum ^= byte
        
        tx_buf.append(checksum)
        tx_buf.append(CMD_TAIL)
        
        self.ser.reset_input_buffer()
        self.ser.write(tx_buf)
        
        self.g_rx_buf = []
        start = time.time()
        
        while time.time() - start < timeout and len(self.g_rx_buf) < rx_bytes_need:
            if self.ser.in_waiting:
                self.g_rx_buf.extend(self.ser.read(self.ser.in_waiting))
        
        if len(self.g_rx_buf) != rx_bytes_need:
            return ACK_TIMEOUT
        if self.g_rx_buf[0] != CMD_HEAD or self.g_rx_buf[-1] != CMD_TAIL:
            return ACK_FAIL
        if self.g_rx_buf[1] != command_buf[0]:
            return ACK_FAIL
        
        checksum = 0
        for i in range(1, 6):
            checksum ^= self.g_rx_buf[i]
        
        if checksum != self.g_rx_buf[6]:
            return ACK_FAIL
        
        return ACK_SUCCESS
    
    def _set_compare_level(self, level):
        """Set compare level (0-9, higher is stricter)"""
        command_buf = [CMD_COM_LEV, 0, level, 0, 0]
        r = self._tx_and_rx_cmd(command_buf, 8, 1)
        
        if r == ACK_TIMEOUT:
            return ACK_TIMEOUT
        if r == ACK_SUCCESS and self.g_rx_buf[4] == ACK_SUCCESS:
            return self.g_rx_buf[3]
        else:
            return 0xFF
    
    def get_user_count(self):
        """Get number of registered fingerprints"""
        command_buf = [CMD_USER_CNT, 0, 0, 0, 0]
        r = self._tx_and_rx_cmd(command_buf, 8, 0.1)
        
        if r == ACK_TIMEOUT:
            return -1
        if r == ACK_SUCCESS and self.g_rx_buf[4] == ACK_SUCCESS:
            return self.g_rx_buf[3]
        else:
            return -1
    
    def add_user(self):
        """
        Register a new fingerprint
        Returns: dict with 'success' (bool) and 'message' (str)
        """
        user_count = self.get_user_count()
        
        if user_count >= USER_MAX_CNT:
            self.audio_player.play_sound("warning")
            return {"success": False, "message": "Fingerprint library is full"}
        
        command_buf = [CMD_ADD_1, 0, user_count + 1, 3, 0]
        r = self._tx_and_rx_cmd(command_buf, 8, 6)
        
        if r == ACK_TIMEOUT:
            self.audio_player.play_sound("warning")
            return {"success": False, "message": "Timeout waiting for first scan"}
        
        if r == ACK_SUCCESS and self.g_rx_buf[4] == ACK_SUCCESS:
            # First scan successful, do second scan
            command_buf[0] = CMD_ADD_3
            r = self._tx_and_rx_cmd(command_buf, 8, 6)
            
            if r == ACK_TIMEOUT:
                self.audio_player.play_sound("warning")
                return {"success": False, "message": "Timeout waiting for second scan"}
            
            if r == ACK_SUCCESS and self.g_rx_buf[4] == ACK_SUCCESS:
                self.audio_player.play_sound("success")
                return {
                    "success": True, 
                    "message": f"Fingerprint registered successfully (ID: {user_count + 1})",
                    "user_id": user_count + 1
                }
            else:
                self.audio_player.play_sound("warning")
                return {"success": False, "message": "Second scan failed"}
        else:
            self.audio_player.play_sound("warning")
            return {"success": False, "message": "First scan failed - ensure finger is centered on sensor"}
    
    def verify_user(self):
        """
        Verify fingerprint against database
        Returns: dict with 'success' (bool), 'message' (str), and 'user_id' (int) if successful
        """
        command_buf = [CMD_MATCH, 0, 0, 0, 0]
        r = self._tx_and_rx_cmd(command_buf, 8, 5)
        
        if r == ACK_TIMEOUT:
            self.audio_player.play_sound("warning")
            return {"success": False, "message": "Timeout - no finger detected"}
        
        status = self.g_rx_buf[4] if len(self.g_rx_buf) > 4 else 0xFF
        
        # Check for error codes FIRST
        if status == ACK_NO_USER:
            self.audio_player.play_sound("warning")
            return {"success": False, "message": "Fingerprint not found in database"}
        elif status == ACK_GO_OUT:
            self.audio_player.play_sound("warning")
            return {"success": False, "message": "Finger not centered properly - please try again"}
        elif status == 0x00:
            self.audio_player.play_sound("warning")
            return {"success": False, "message": "No fingerprint detected"}
        
        # Only accept valid user IDs (0x01-0xFE)
        if 0x01 <= status <= 0xFE:
            self.audio_player.play_sound("success")
            return {
                "success": True,
                "message": "Fingerprint verified",
                "user_id": status
            }
        
        self.audio_player.play_sound("warning")
        return {"success": False, "message": "Verification failed"}
    
    def clear_all_users(self):
        """Clear all registered fingerprints"""
        command_buf = [CMD_DEL_ALL, 0, 0, 0, 0]
        r = self._tx_and_rx_cmd(command_buf, 8, 5)
        
        if r == ACK_TIMEOUT:
            self.audio_player.play_sound("warning")
            return {"success": False, "message": "Timeout"}
        if r == ACK_SUCCESS and self.g_rx_buf[4] == ACK_SUCCESS:
            self.audio_player.play_sound("success")
            return {"success": True, "message": "All fingerprints cleared"}
        else:
            self.audio_player.play_sound("warning")
            return {"success": False, "message": "Failed to clear fingerprints"}
    
    def cleanup(self):
        """Cleanup resources"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        GPIO.cleanup()
