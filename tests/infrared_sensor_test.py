import RPi.GPIO as GPIO
import time
import board

from adafruit_motorkit import MotorKit

INFRARED_SENSOR = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(INFRARED_SENSOR, GPIO.IN)

kit = MotorKit(i2c=board.I2C())

try:
    while True:
        infrared_val = GPIO.input(INFRARED_SENSOR)
        if infrared_val == 0:
            print('HAND! triggered!!')
            kit.stepper2.onestep()
            time.sleep(0.01)
        else:
            print('No hand')
            kit.stepper1.onestep()
            time.sleep(0.01)
except KeyboardInterrupt:
    print("Exiting program")
finally:
    GPIO.cleanup()