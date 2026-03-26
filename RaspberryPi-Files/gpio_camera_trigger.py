#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: 2023 Kent Gibson <warthog618@gmail.com>

"""Minimal example of watching for rising edges on a single line."""
import cv2
import pandas as pd
import time
import datetime
import gpiod
from gpiod.line import Edge
import board
import neopixel_spi as neopixel
from ultralytics import YOLO

model = YOLO('yolo11n.pt', task="detect")

# Initialize LED Vairables
NUM_PIXELS = 16
PIXEL_ORDER = neopixel.RGBW
WHITE = 0xFFFFFF
OFF = 0x000000
DELAY = 0.1

# Create SPI connection to NeoPixel with proper parameters
spi = board.SPI()
pixels = neopixel.NeoPixel_SPI(spi, NUM_PIXELS, pixel_order=PIXEL_ORDER, auto_write=False)

# Define model inference function
def get_model_results(results):
    all_detections_data = []
    for result in results:
        boxes = result.boxes
        name = result.names
        for box in boxes:
            # Extract relevant information (e.g., class, confidence, bounding box coo>
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            namey = name[class_id]
            # Bounding box coordinates in xyxy format (top-left x, y; bottom-right x,>
            coords = box.xyxy[0].tolist() 

            detection_data = {
                'image_path': result.path,
                'class_id': class_id,
                'confidence': confidence,
                'class name':namey
            }
            all_detections_data.append(detection_data)
            df = pd.DataFrame(all_detections_data)
            df.to_csv('yolo_detections_manual.csv', index=False)
            print("Detections saved to yolo_detections_manual.csv")


# Loop to continuously read and display frames

def watch_line_falling(chip_path, line_offset):
    with gpiod.request_lines(
        chip_path,
        consumer="watch-line-falling",
        config={line_offset: gpiod.LineSettings(debounce_period=datetime.timedelta(milliseconds = 10), edge_detection=Edge.FALLING)},
    ) as request:
        while True:
            # Blocks until at least one event is available
            for event in request.read_edge_events():
                print(
                    "line: {}  type: Falling   event #{}".format(
                        event.line_offset, event.line_seqno
                    )
                )
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
                    cv2.imshow('Captured Image', frame)
                    cv2.imwrite('captured_image.png', frame)
                    results = model('captured_image.png')
                    get_model_results(results)
                    time.sleep(0.1)
                    cv2.waitKey(0)
                    pixels.fill(OFF)
                    pixels.show()
                    cv2.destroyWindow("Captured Image")
                else:
                    print("Failed to capture image.")
                cap.release()

if __name__ == "__main__":
    try:
        while True:
            watch_line_falling("/dev/gpiochip0", 4)
    except OSError as ex:
            print(ex, "\nCustomise the example configuration to suit your situation")
