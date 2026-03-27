from flask import Flask, request, jsonify, render_template
import socket
import serial
import csv
import time, traceback
import threading
import datetime
import cv2
import gpiod
from gpiod.line import Edge
import board
import neopixel_spi as neopixel
import os

# Read Arduino Serial interface
def read():
    try:
        data = ser.readline()
        return data
    except:
        print("Error collecting data, perhaps empty buffer?")

#Main App Variables
app = Flask(__name__)
hostname = socket.gethostname()
ipAddress = socket.gethostbyname(hostname)

IMG_FOLDER = os.path.join("static", "IMG")
app.config["UPLOAD_FOLDER"] = IMG_FOLDER

# Initialize LED Vairables
NUM_PIXELS = 16
PIXEL_ORDER = neopixel.RGBW
WHITE = 0xFFFFFF
OFF = 0x000000
DELAY = 0.1

# Create SPI connection to NeoPixel with proper parameters
spi = board.SPI()
pixels = neopixel.NeoPixel_SPI(spi, NUM_PIXELS, pixel_order=PIXEL_ORDER, auto_write=False)

arduino_port = "/dev/ttyACM0" #serial port of arduino
baud = 9600 #arduino baud rate 9600
fileName = "httpControlTest.csv" #name of CSV file generated
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
file = open(fileName, "a")
print("Created File")

# Storage for messages
about = [
    {
        "board": "raspberry pi 5",
        "name": "Fridge Freshness Detector",
        "class": "Senior Design"
    }
]

# Read Arduino Serial interface
def read():
    try:
        data = ser.readline()
        return data
    except:
        print("Error collecting data, perhaps empty buffer?")

#Collect data from serial buffer, store in csv
def arduino_output():
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

def every(delay, task):
    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))
        try:
            task()
        except Exception:
            traceback.print_exc()
        next_time += (time.time() - next_time)

def cameraTrigger():
    # Open the default camera (index 0)
    cap = cv2.VideoCapture(0)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    pixels.fill(WHITE)
    pixels.show()
    ret, frame = cap.read()
    # If the frame was read successfully, display it
    if ret:
    # Display the frame in a window named 'Webcam Feed'
        cv2.imwrite('./static/IMG/http_test_image.png', frame)
        time.sleep(0.1)
        pixels.fill(OFF)
        pixels.show()
    else:
        print("Failed to capture image.")
    cap.release()

@app.route("/")
def home():
    try:
        return "Please input a command into the URL.", 200
    except:
        return "", 404

@app.route("/about")
def about():
    try:
        return jsonify(about), 200
    except:
        return "", 404
    
@app.route("/motorfridge")
def motor_fridge():
        ser.write(bytes(motorFridge, 'utf-8'))
        return "Running Fridge Motor", 200
@app.route("/motorroom")
def motor_room():
    try:
        ser.write(bytes(motorRoom, 'utf-8'))
        return "Running Room Motor", 200
    except:
        return "", 404

@app.route("/motorstop")
def motor_stop():
    try:
        ser.write(bytes(motorStop, 'utf-8'))
        return "Stopping all motors", 200
    except:
        return "", 404
    
@app.route("/camera")
def camera():
    try:
        cameraTrigger()
        test_image = os.path.join(app.config["UPLOAD_FOLDER"], "http_test_image.png")
        return render_template("index.html", user_image=test_image), 200
    except Exception:
        traceback.print_exc()
        return "", 404

threading.Thread(target=lambda: every((15), arduino_output)).start()

if __name__ == "__main__":
    HOST = '0.0.0.0' # Use '0.0.0.0' to make the server accessible externally
    PORT = 5000  # Set your desired port number
    app.run(host=HOST, port=PORT, debug=True)
