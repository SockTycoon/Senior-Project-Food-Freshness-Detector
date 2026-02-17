import serial
import csv
import time, traceback
import threading
from apscheduler.schedulers.background import BackgroundScheduler
import sched
from celery import Celery
from datetime import timedelta

arduino_port = "/dev/ttyACM0" #serial port of arduino
baud = 9600 #arduino baud rate 9600
fileName = "dataTest7-Chicken.csv" #name of CSV file generated
sensor_data = []

motorFridge = '1\n'
motorRoom = '2\n'
motorStop = '3\n'
senseData = '4\n'

samples = 10
print_labels = False
line = 0
start = True
pumpDelayFridge = 5
senseDelay = 15
pumpDelayRoom = 40
initialRun = True

ser = serial.Serial(arduino_port, baud)
print("Connected to Arduino port: " + arduino_port)
file = open(fileName, "a")
print("Created File")

s = BackgroundScheduler()
schedule = sched.scheduler(time.time, time.sleep)

def read():
    #ser.write(bytes(x, 'utf-8'))
    #time.sleep(0.05)
    data = ser.readline()
    return data

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

def scheduled_job():
    print("Pumping Air From Fridge")
    ser.write(bytes(motorFridge, 'utf-8'))
    time.sleep(60)
    print("Gathering Sensor Data")
    ser.write(bytes(senseData, 'utf-8'))
    time.sleep(915)
    print("Sensing Complete")
    print("Pumping Air From Room")
    ser.write(bytes(motorRoom, 'utf-8'))
    time.sleep(2400)
    print("Stopping All Motors")
    ser.write(bytes(motorStop, 'utf-8'))
    time.sleep(225)
def every(delay, task):
    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))
        try:
            task()
        except Exception:
            traceback.print_exc()
        next_time += (time.time() - next_time)

threading.Thread(target=lambda: every((3600+10), scheduled_job)).start()

while True:
    

    #display serial data to terminal
    #s.add_job(collect_data, 'interval', seconds=30)
    #s.add_job(motor_room, 'interval', minutes=2)
    #s.add_job(motor_stop, 'interval', seconds=180)
    #schedule.enter(10, 1, scheduled_job)
    #schedule.enter(5,2, motor_room)
    #if(start):
    #    schedule.run()
    #    start = False

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

    while initialRun:
        scheduled_job()
        initialRun = False
    #print(sensor_data)
    #s.shutdown()
