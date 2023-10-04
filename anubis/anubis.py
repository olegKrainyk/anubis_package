import math
import timeit

from .consts import FOCAL_LENGTH, RADIUS, SENSOR_WIDTH, probable_heights
from typing import List, Optional

def get_event_pos(*, # force keyword call
                  classification: str, 
                  bearing_center: float, 
                  source_lat: float, 
                  source_lon: float, 
                  sensor_width_px: int,
                  sensor_height_px: int,
                  target_center_x: int,
                  target_center_y: Optional[int] = None,
                  target_width_px: Optional[int] = None,
                  target_height_px: int,
                  altitude: float,
                  focal_length: Optional[float] = None, 
                  sensor_width: Optional[float] = None) -> List[float]:
    
    """Calculates the geographical position of an event given camera params.
    
    Args:
        classification (str): The classification of the object (e.g., "car", "person").
        bearing_center (float): The bearing of the camera.
        source_lat (float): The latitude of the camera in degrees.
        source_lon (float): The longitude of the camera in degrees.
        sensor_width_px (int): The width of the video in pixels.
        sensor_height_px (int): Height of the video in pixels
        target_center_x (int): The x-coordinate of the target center in the sensor.
        target_center_y (int): The y-coordinate of the target center in the sensor.  Not currently used.
        target_width_px (int): The width of the target in pixels.  Not currently used.
        target_height_px (int): The height of the target in pixels. 
        altitude (float): The altitude of the source.
        focal_length (float, optional): The focal length in mm. Defaults to None.
        sensor_width (float, optional): The sensor width in mm. Defaults to None.

    Returns:
        List[float]: The estimated position of the event [latitude, longitude].

    TODO target_center_y and target_width_px are currently not used change to not default to None if used
    """

    if focal_length is None:
        focal_length = FOCAL_LENGTH
    
    if sensor_width is None:
        sensor_width = SENSOR_WIDTH 
    
    sensor_height = sensor_width * (sensor_height_px/sensor_width_px)

    #  sensor_height_px height of the video 

    # get bearing from two points (for future UI uasge)

    bearing_center_deg = (bearing_center * 180 / math.pi + 360) % 360

    # Get probable height, use 1 meter as default if not in probable_heights
    probable_height = probable_heights.get(classification, 1.0)

    if altitude > 40:
        probable_height *= 2
    
    height_on_sensor = (sensor_height * target_height_px)/sensor_height_px

    field_of_view = math.degrees(2 * math.atan((sensor_width / 2) / focal_length))

    distance_to_object = (probable_height * focal_length) / height_on_sensor   # (real height(m) * focal length(mm) )/hight on sensor

    target_bearing_deg = (bearing_center_deg - (field_of_view / 2)) + ((target_center_x) / (sensor_width_px / field_of_view))
    target_bearing = math.radians(target_bearing_deg)

    dr = distance_to_object / RADIUS
    lat_delta = dr * math.cos(target_bearing)
    target_lat = source_lat + lat_delta
    delta = math.log(math.tan(target_lat/2 + math.pi / 4) / math.tan(source_lat / 2 + math.pi/4))
    q = (lat_delta/delta) if abs(delta) > 10e-12 else math.cos(source_lat)
    lon_delta = dr * math.sin(target_bearing) / q
    target_lon = source_lon + lon_delta

    return([target_lat, target_lon])

def get_event_local_pos(*, # force keyword call
                  classification: str, 
                  bearing_center: float,
                  sensor_width_px: int,
                  sensor_height_px: int,
                  target_center_x: int,
                  target_center_y: int,
                  target_height_px: int,
                  focal_length: Optional[float] = None, 
                  sensor_width: Optional[float] = None) -> List[float]:
    
    """Calculates the geographical position of an event given camera params.
    
    Args:
        classification (str): The classification of the object (e.g., "car", "person").
        bearing_center (float): The bearing of the camera.
        sensor_width_px (int): The width of the video in pixels.
        sensor_height_px (int): Height of the video in pixels
        target_center_x (int): The x-coordinate of the target center in the sensor.
        target_center_y (int): The y-coordinate of the target center in the sensor.  Not currently used.
        target_height_px (int): The height of the target in pixels.
        focal_length (float, optional): The focal length in mm. Defaults to None.
        sensor_width (float, optional): The sensor width in mm. Defaults to None.

    Returns:
        List[float]: The estimated local position of the event [X, Y, Z].

    TODO target_width_px is currently not used change to not default to None if used
    """

    if focal_length is None:
        focal_length = FOCAL_LENGTH
    
    if sensor_width is None:
        sensor_width = SENSOR_WIDTH 
    
    sensor_height = sensor_width * (sensor_height_px / sensor_width_px)

    #  sensor_height_px height of the video

    # get bearing from two points (for future UI uasge)

    bearing_center_deg = (bearing_center * 180 / math.pi + 360) % 360

    # Get probable height, use 1 meter as default if not in probable_heights
    probable_height = probable_heights.get(classification, 1.0)

    height_on_sensor = (sensor_height * target_height_px) / sensor_height_px

    field_of_view = math.degrees(2 * math.atan((sensor_width / 2) / focal_length))

    distance_to_object = (probable_height * focal_length) / height_on_sensor

    target_bearing_deg = (bearing_center_deg - (field_of_view / 2)) + (
                (target_center_x) / (sensor_width_px / field_of_view))
    target_bearing = math.radians(target_bearing_deg)

    # calculate X and Y
    targetX = distance_to_object * math.cos(target_bearing)
    targetY = distance_to_object * math.sin(target_bearing)

    # calculate meters per pixel of object
    zconst = ((sensor_height_px / target_height_px) * probable_height)/sensor_height_px

    # check whether object height should be positive or negative
    # calculate Z
    if((sensor_height_px / 2) < target_center_y):
        targetZ = (sensor_height_px - target_center_y) * zconst
    else:
        targetZ = ((sensor_height_px/2)-target_center_y) * zconst * -1

    return([targetX, targetY, targetZ])


def does_classifications_have_probable_heights(*, classification: str) -> bool:
    """Checks if a given classification has associated probable heights allowing us to see if a event is worthy
    of being processed. If probable heights is tweaked doesn't force us to hard code.
    Args:
        classification (str): The classification of an event to check.

    Returns:
        bool: True if the classification has associated probable heights, False otherwise.
    """
    return classification in probable_heights