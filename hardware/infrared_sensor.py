"""
Infrared Sensor Module
Simple interface for IR obstacle detection sensor
"""

import RPi.GPIO as GPIO
import time


class InfraredSensor:
    """Interface for infrared hand detection sensor"""
    
    def __init__(self, gpio_pin=25):
        """
        Initialize infrared sensor
        
        Args:
            gpio_pin: GPIO pin number (BCM mode) where sensor is connected
        """
        self.gpio_pin = gpio_pin
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.gpio_pin, GPIO.IN)
    
    def is_hand_detected(self):
        """
        Check if hand is currently detected
        
        Returns:
            bool: True if hand detected, False otherwise
        """
        # Sensor is active LOW (outputs 0 when object detected)
        return GPIO.input(self.gpio_pin) == 0
    
    def wait_for_hand(self, timeout=10):
        """
        Wait for hand to be detected
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if hand detected within timeout, False otherwise
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.is_hand_detected():
                return True
            time.sleep(0.1)
        
        return False
    
    def wait_for_hand_removal(self, timeout=10):
        """
        Wait for hand to be removed
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if hand removed within timeout, False otherwise
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self.is_hand_detected():
                return True
            time.sleep(0.1)
        
        return False
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        GPIO.cleanup()
