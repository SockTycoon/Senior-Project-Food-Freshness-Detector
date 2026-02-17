#-----------------------------------------------------------
# Designer: Alex Willis
#
# Usage: Program transmits and receives  Arduino serial
#        messages over USB. Program sends 4 commands to 
#        Arduino to control function. Recieves comma-separated
#        sensor data and parses that data to be stored in a .csv
#        file.
#-----------------------------------------------------------

import serial
import csv
import time, traceback
import threading
from apscheduler.schedulers.background import BackgroundScheduler
import sched
from datetime import timedelta

arduino_port = "/dev/ttyACM0" #serial port of arduino
baud = 9600 #arduino baud rate 9600
fileName = "dataTest9.csv" #name of CSV file generated
sensor_data = []

# Arduino control variables, to be sent over serial
motorFridge = '1\n'
motorRoom = '2\n'
motorStop = '3\n'
senseData = '4\n'
senseStop = '5\n'

# Variable initialization
samples = 10
print_labels = False
line = 0
start = True
pumpDelayFridge = 5
senseDelay = 15
pumpDelayRoom = 40
delayFridgePump = 60
delaySensorTime = 300
delayCleanTime = 300
delayMotorStop = 60
totalTime = pumpDelayRoom + delayFridgePump + delaySensorTime + delayCleanTime + delayMotorStop

# Open serial connection to Arduino
ser = serial.Serial(arduino_port, baud)
print("Connected to Arduino port: " + arduino_port)
file = open(fileName, "a")
print("Created File")

# Scheduler Initialization
s = BackgroundScheduler()
schedule = sched.scheduler(time.time, time.sleep)

# Read Arduino Serial interface
def read():
    data = ser.readline()
    return data

# Functions to quickly command Arduino via serial commands
def motor_fridge():
    ser.write(bytes(motorFridge, 'utf-8'))
    return
def motor_room():
    ser.write(bytes(motorRoom, 'utf-8'))
    return
def motor_stop():
    ser.write(bytes(motorStop, 'utf-8'))
    return
def collect_data():
    ser.write(bytes(senseData, 'utf-8'))
    return

# Scheduled job to be repeated indefinitely
def scheduled_job():
    print("Pumping Air From Fridge")
    ser.write(bytes(motorFridge, 'utf-8'))
    time.sleep(delayFridgePump) #1 minute
    print("Gathering Sensor Data")
    ser.write(bytes(senseData, 'utf-8'))
    time.sleep(delaySensorTime) #15 minutes
    print("Sensing Complete")
    ser.write(bytes(senseStop, 'utf-8'))
    time.sleep(15)
    print("Pumping Air From Room")
    ser.write(bytes(motorRoom, 'utf-8'))
    time.sleep(delayCleanTime) #40 minutes
    print("Stopping All Motors")
    ser.write(bytes(motorStop, 'utf-8'))
    time.sleep(delayMotorStop) #3 minutes & 45 seconds
# Attempts to execute scheduled_job() every hour
def every(delay, task):
    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))
        try:
            task()
        except Exception:
            traceback.print_exc()
        next_time += (time.time() - next_time)

#Creates a separate thread to run every() independent of While loop
threading.Thread(target=lambda: every((totalTime+10), scheduled_job)).start()

while True:

    getData = read()
    dataString = getData.decode('utf-8')
    data = dataString[0:][:-2]
    print(data)

    readings = data.split(",")
    print(readings)

    with open(fileName, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(sensor_data)
    sensor_data.append(readings)
