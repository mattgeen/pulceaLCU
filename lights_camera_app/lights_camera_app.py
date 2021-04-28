# Functions for the Pulcea lights and camera unit (LCU)

# The GUI 
from guizero import App, Text, TextBox, PushButton, Slider

# GPIO servo for motor and light control
from gpiozero import Servo, AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
import time

# For the camera
import os
import pygame, sys

from pygame.locals import *
import pygame.camera

from datetime import datetime

# I2C for the pressure meter
import ms5837
    
def set_light_intensity(perc):
    set_perc = float(perc)
    print("light perc", set_perc)
    lights_s.value = set_perc / 100.
    
def set_motor_angle(angle):
    set_angle = float(angle)
    print("motor angle", set_angle)
    motor_s.angle = set_angle     # This wakes up the servo
    time.sleep(0.1)
    motor_s.angle = set_angle     # Do it again, to make sure the angle is set
    motor_s.detach()              # Stop the servo, so that it doesn't jitter
    
def take_picture():
    print("take picture")
    #take a picture
    image = cam.get_image()
    
    #setup window
    windowSurfaceObj = pygame.display.set_mode((pic_width,pic_height),1,16)
    pygame.display.set_caption('Camera')

    #display the picture
    catSurfaceObj = image
    windowSurfaceObj.blit(catSurfaceObj,(0,0))
    pygame.display.update()

    #save picture
    now = datetime.now() # current date and time
    date_time = now.strftime("%Y%m%d_%H%M%S")
    
    # Folder to store pictures
    pictures_folder = "/home/pi/Pictures/"
    filename = pictures_folder + date_time + ".jpg"
    print("saving file", filename)
    pygame.image.save(windowSurfaceObj, filename)
    
def get_pressure():
    pressure_sensor.read(ms5837.OSR_8192)   # get the raw pressure and temperature
    pressure = pressure_sensor.pressure() # Get pressure in default units (millibar)
    temperature = pressure_sensor.temperature() # Get temperature in default units (Centigrade)
    depth = pressure_sensor.depth()
    print("pressure %.2f" % pressure, "  temperature %.2f" % temperature, "  depth %.2f" % depth)
    depth_text_value.value = "%.2f" %depth + " m"
    
#def start_camera():
# #   cam = pygame.camera.Camera("/dev/video0",(pic_width,pic_height))
 #   cam.start() 
    
    
def close():
    lights_s.detach()
    motor_s.detach()
    cam.stop()
    app.destroy()

# Motor servo on GPIO 17

motor_s = AngularServo(17, initial_angle=0, min_angle=-20, max_angle=20, min_pulse_width=1100/1000000,
                      max_pulse_width=1900/1000000)

# Lights on GPIO pin 27
lights_s = Servo(27, min_pulse_width = 1100/1000000, max_pulse_width = 1900/1000000)
lights_s.value=-1

set_light_intensity(-100)
set_motor_angle(0)

#initialise pygame for tje camera
pygame.init()
pygame.camera.init()
pic_width = 640
pic_height = 480
cam = pygame.camera.Camera("/dev/video0",(pic_width,pic_height))
cam.start()
#start_camera()

# initialise the pressure sensor
pressure_sensor = ms5837.MS5837()       # Use defaults (MS5837-30BA device on I2C bus 1)
pressure_sensor.init()
pressure_sensor.setFluidDensity(ms5837.DENSITY_SALTWATER) # Use predefined saltwater density

app = App(title="Lights and camera control", layout="grid", width=450, height=300)

lights_message = Text(app, text="light intensity, %", grid=[0,0], align="left")
light_intensity = Slider(app, command=set_light_intensity, start=-100., end=100., width=200, grid=[1,0])

motor_message = Text(app, text="motor angle, degrees", grid=[0,1], align="left")
motor_angle = Slider(app, command=set_motor_angle, start=-20., end=20., width=200, grid=[1,1])

null_message = Text(app, text=" ", grid=[1,3])

picture_button = PushButton(app, text="Take still image", command=take_picture, grid=[1,4])

pressure_button = PushButton(app, text="Read depth", command=get_pressure, grid=[0,5])
#depth_text = Text(app, text="Depth", grid=[1,5], align="left")
depth_text_value = Text(app, text="0", grid=[1,5], align="left")

null_message2 = Text(app, text=" ", grid=[1,6])

stop_button = PushButton(app, text="Stop", command=close, grid=[1,7])

app.on_close(close)

app.display()

