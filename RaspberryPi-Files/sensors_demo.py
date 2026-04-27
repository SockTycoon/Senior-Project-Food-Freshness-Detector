import random
import serial
import csv
import time, traceback
import threading
import sched
from datetime import timedelta
from paho.mqtt import client as mqtt_client

broker = '10.100.138.163'
port = 1883
topic = "test/sensors"
threshold_lvl = 7600
low_value = True
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'
username = 'testUser'
password = 'pass'

arduino_port = "/dev/ttyACM0" #serial port of arduino
baud = 9600 #arduino baud rate 9600
sensor_data = []

# Arduino control variables, to be sent over serial
motorFridge = '1\n'
motorRoom = '2\n'
motorStop = '3\n'
senseData = '4\n'
senseStop = '5\n'

# Open serial connection to Arduino
ser = serial.Serial(arduino_port, baud)
print("Connected to Arduino port: " + arduino_port)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # client = mqtt_client.Client(client_id)
    client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, msg):
    result = client.publish(topic, msg)
        # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

# Read Arduino Serial interface
def read():
    data = ser.readline()
    return data

ser.write(bytes(senseStop, 'utf-8'))
time.sleep(10)
ser.write(bytes(senseData, 'utf-8'))
client = connect_mqtt()
client.loop_start()
while True:
    time.sleep(5)
    getData = read()
    dataString = getData.decode('utf-8')
    data = dataString[0:][:-2]

    readings = data.split(",")
    print(readings)
    print(readings[0])
    if readings[0] == "Ethanol":
        print("Headers")
    elif int(readings[0]) >= threshold_lvl and low_value:
        publish(client, readings[0] + '  High Ethanol Detected, Food has spoiled.')
        low_value = False
        print(low_value)
    elif int(readings[0]) <= threshold_lvl:
        print("Not past threshold.")
        low_value = True
    else:
        print("donothing else")
        print(low_value)
