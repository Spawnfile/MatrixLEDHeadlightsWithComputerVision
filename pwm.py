import RPi.GPIO as GPIO 
from time import sleep 
import socket

print("Program Started..")

GPIO.setmode(GPIO.BCM) 
GPIO.setup(15, GPIO.OUT)
GPIO.setup(14, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

right = GPIO.PWM(14, 100)
mid = GPIO.PWM(15, 100) 
left = GPIO.PWM(18, 100) 
 
left.start(100) 
mid.start(100)
right.start(100) 
pause_time = 0.02 

ip = ""
port = 8888

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, port))

try:
    while True:
        data, addr = sock.recvfrom(1024)
        print("Receiving Message: {}".format(data.decode()))        
        name = data.decode()
        if name == "No_Detection":
            en_sol.start(100)
            orta.start(100)
            en_sag.start(100)
            print("There is No Detection")

        if name == "first_pwm":           
            en_sol.start(20)
            sleep(pause_time)
            print("Left Headlight Going Down")
            
        if name == "second_pwm":
            orta.start(20)
            sleep(pause_time)
            print("Middle Headlight Going Down")
            
        if name == "third_pwm":
            en_sag.start(20)
            sleep(pause_time)
            print("Right Headlight Going Down")     
        
except KeyboardInterrupt:
    GPIO.cleanup() 

en_sag.stop() 
orta.stop()
en_sol.stop()
GPIO.cleanup() 
 
