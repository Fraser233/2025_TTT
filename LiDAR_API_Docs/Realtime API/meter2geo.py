import math


# Variables
SENSOR_POSITION_LAT = 45.503565  # <float> example: 45.503565
SENSOR_POSITION_LON = -73.587081  # <float> example: -73.587081
SENSOR_ROTATION = 120.5  # <float> example: 120.5
SENSOR_OFFSET_X = 0  # <float> example: 0
SENSOR_OFFSET_Y = 0  # <float> example: 0


def convertPixelToGeo(x, y):
    lat = SENSOR_POSITION_LAT
    lon = SENSOR_POSITION_LON


    cx = -x + SENSOR_OFFSET_X
    cy = -y + SENSOR_OFFSET_Y
    
    dn = cx*math.cos(SENSOR_ROTATION/180*math.pi)-cy * math.sin(SENSOR_ROTATION/180*math.pi)
    de = cy*math.cos(SENSOR_ROTATION/180*math.pi)+cx * math.sin(SENSOR_ROTATION/180*math.pi)

    # Earth’s radius, sphere
    R = 6378137


    # Coordinate offsets in radians
    dLat = dn/R
    dLon = de/(R*math.cos(math.pi*lat/180))

    # OffsetPosition, decimal degrees
    lat = lat + dLat * 180/math.pi
    lon = lon + dLon * 180/math.pi
    return lat, lon


if __name__ == "__main__":


    # Examples: 
    # give x =0 and y=0, it would return corresponding absolute Geo location
    print (convertPixelToGeo(0, 0))
    print (convertPixelToGeo(0, 1000))
    print (convertPixelToGeo(1000, 0))
    print (convertPixelToGeo(1000, 1000))
    print (convertPixelToGeo(674, 520))
    print (convertPixelToGeo(298, 681))
    print (convertPixelToGeo(264, 647))
    print (convertPixelToGeo(117, 317))

