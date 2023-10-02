# Define constants
RADIUS = 6371000  # Earth radius in meters

FOCAL_LENGTH = 22 # in mm

SENSOR_WIDTH = 7  # in mm

# Probable height of objects in meters

probable_heights = {
    "person": 1.7,
    "car": 1.6,
    "motorcycle": 1.0,
    "truck": 1.8,
    "airplane": 15.0,
    "traffic light": 0.6,
    "boat": 30.0
}