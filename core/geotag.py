from math import atan2, cos, radians, sin, sqrt

from exif import Image
from werkzeug.datastructures import FileStorage


def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees


def extract_coords(file: FileStorage):
    image = Image(file)
    coords = (
        decimal_coords(
            image.gps_latitude,
            image.gps_latitude_ref,
        ),
        decimal_coords(
            image.gps_longitude,
            image.gps_longitude_ref,
        ),
    )
    return coords


def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = 6371 * c
    return distance


def within_radius(pointA, pointB, radius):
    distance = haversine_distance(pointA[0], pointA[1], pointB[0], pointB[1])
    return distance <= radius
