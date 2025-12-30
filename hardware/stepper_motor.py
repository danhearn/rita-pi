"""
Stepper Motor Module
Interface for controlling pill dispenser stepper motors
"""

import time
import board
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper


class StepperMotorController:
    """Controller for 3 stepper motors managing pill dispensers"""
    
    # Each dispenser has 15 segments
    SEGMENTS_PER_ROTATION = 15
    
    # Typical stepper motor: 200 steps per rotation (1.8° per step)
    # Using DOUBLE stepping for better torque
    STEPS_PER_ROTATION = 200
    
    def __init__(self):
        """Initialize motor controller"""
        self.kit = MotorKit(i2c=board.I2C())
        
        # Map motor IDs to MotorKit stepper objects
        self.motors = {
            1: self.kit.stepper1,
            2: self.kit.stepper2
        }
        
        # Track current position of each motor (which segment is at dispensing position)
        self.current_segment = {
            1: 0,
            2: 0
        }
    
    def _calculate_steps_for_segments(self, num_segments):
        """Calculate number of steps needed to rotate by given segments"""
        degrees = (360 / self.SEGMENTS_PER_ROTATION) * num_segments
        steps = int((degrees / 360) * self.STEPS_PER_ROTATION)
        return steps
    
    def dispense_pill(self, motor_id, segment_number):
        """
        Rotate motor to dispense pill from specific segment
        
        Args:
            motor_id: Motor number (1, 2, or 3)
            segment_number: Segment to dispense from (0-14)
            
        Returns:
            dict with 'success' (bool) and 'message' (str)
        """
        if motor_id not in self.motors:
            return {"success": False, "message": f"Invalid motor ID: {motor_id}"}
        
        if segment_number < 0 or segment_number >= self.SEGMENTS_PER_ROTATION:
            return {
                "success": False, 
                "message": f"Invalid segment: {segment_number}. Must be 0-{self.SEGMENTS_PER_ROTATION-1}"
            }
        
        motor = self.motors[motor_id]
        current = self.current_segment[motor_id]
        
        # Calculate how many segments to rotate
        segments_to_rotate = (segment_number - current) % self.SEGMENTS_PER_ROTATION
        
        if segments_to_rotate == 0:
            return {
                "success": True,
                "message": f"Motor {motor_id}: Segment {segment_number} already at dispense position"
            }
        
        # Calculate steps
        steps = self._calculate_steps_for_segments(segments_to_rotate)
        
        # Rotate motor
        try:
            for _ in range(steps):
                motor.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
                time.sleep(0.01)
            
            # Release motor to save power and reduce heat
            motor.release()
            
            # Update current position
            self.current_segment[motor_id] = segment_number
            
            return {
                "success": True,
                "message": f"Motor {motor_id}: Dispensed from segment {segment_number}",
                "motor_id": motor_id,
                "segment": segment_number
            }
        
        except Exception as e:
            return {"success": False, "message": f"Motor error: {str(e)}"}
    
    def rotate_segments(self, motor_id, num_segments, direction="forward"):
        """
        Rotate motor by specified number of segments
        
        Args:
            motor_id: Motor number (1, 2, or 3)
            num_segments: Number of segments to rotate
            direction: "forward" or "backward"
            
        Returns:
            dict with 'success' (bool) and 'message' (str)
        """
        if motor_id not in self.motors:
            return {"success": False, "message": f"Invalid motor ID: {motor_id}"}
        
        motor = self.motors[motor_id]
        steps = self._calculate_steps_for_segments(num_segments)
        
        step_direction = stepper.FORWARD if direction == "forward" else stepper.BACKWARD
        
        try:
            for _ in range(steps):
                motor.onestep(direction=step_direction, style=stepper.DOUBLE)
                time.sleep(0.01)
            
            motor.release()
            
            # Update position
            if direction == "forward":
                self.current_segment[motor_id] = (
                    self.current_segment[motor_id] + num_segments
                ) % self.SEGMENTS_PER_ROTATION
            else:
                self.current_segment[motor_id] = (
                    self.current_segment[motor_id] - num_segments
                ) % self.SEGMENTS_PER_ROTATION
            
            return {
                "success": True,
                "message": f"Motor {motor_id}: Rotated {num_segments} segments {direction}"
            }
        
        except Exception as e:
            return {"success": False, "message": f"Motor error: {str(e)}"}
    
    def release_all(self):
        """Release all motors to save power"""
        for motor in self.motors.values():
            motor.release()
    
    def get_status(self):
        """Get current status of all motors"""
        return {
            "motors": {
                motor_id: {
                    "current_segment": self.current_segment[motor_id]
                }
                for motor_id in self.motors.keys()
            }
        }
