import RPi.GPIO as GPIO

# Pin Definitions (Pi 5 GPIO)
L_IN1, L_IN2 = 17, 27
R_IN3, R_IN4 = 23, 24
# Optional: If using PWM for manual speed control
L_EN, R_EN = 12, 13 

def setup_motors():
    GPIO.setmode(GPIO.BCM)
    for pin in [L_IN1, L_IN2, R_IN3, R_IN4, L_EN, R_EN]:
        GPIO.setup(pin, GPIO.OUT)
    
    # Set manual speed (60% power)
    global left_pwm, right_pwm
    left_pwm = GPIO.PWM(L_EN, 1000)
    right_pwm = GPIO.PWM(R_EN, 1000)
    left_pwm.start(60)
    right_pwm.start(60)

def move_forward():
    GPIO.output(L_IN1, True); GPIO.output(L_IN2, False)
    GPIO.output(R_IN3, True); GPIO.output(R_IN4, False)

def turn_left():
    # Left motor OFF, Right motor ON
    GPIO.output(L_IN1, False); GPIO.output(L_IN2, False)
    GPIO.output(R_IN3, True);  GPIO.output(R_IN4, False)

def turn_right():
    # Left motor ON, Right motor OFF
    GPIO.output(L_IN1, True);  GPIO.output(L_IN2, False)
    GPIO.output(R_IN3, False); GPIO.output(R_IN4, False)

def stop():
    GPIO.output(L_IN1, False); GPIO.output(L_IN2, False)
    GPIO.output(R_IN3, False); GPIO.output(R_IN4, False)

def cleanup():
    stop()
    GPIO.cleanup()
