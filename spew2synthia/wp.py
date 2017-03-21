from shapely import wkb
from shapely.geometry import Point
import codecs


def main():
    hex_string1 = Point(1.0, 2.0).wkb_hex
    hex_string2 = '0101000020E61000000A4B3CA06C9E55C05E10919A763B4040'
    print(to_long_lat_from_hex(hex_string1))
    print(to_long_lat_from_hex(hex_string2))


def to_long_lat_from_hex(hex_string):
    return point_to_long_lat(wkb_hex_to_point_coord(hex_string))


def point_to_long_lat(point):
    return str(point[0]) + ',' + str(point[1])


def wkb_hex_to_point_coord(hex_string):
    wk = wkb.loads(codecs.decode(hex_string, 'hex_codec'))
    return wk.coords[0]


# main()

