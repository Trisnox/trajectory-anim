import bpy
import numpy as np
from mathutils import Vector


def create_poly_curve(name: str, points: list[Vector]) -> bpy.types.Object:
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new(type='POLY')

    # I honestly don't understand foreach_set/get because the documentation never explains what it contains nor what argument it expects
    # and the error log doesn't tell much either
    # But in this case, each points represent [x, y, z, w], which expects an array with multiples of 4
    # I don't know why is there 4th coord in there for whatever reason
    point_length = len(points)
    spline.points.add(point_length - 1)
    coords = np.zeros(point_length * 4, dtype=np.float64)
    spline.points.foreach_get('co', coords)
    points_array = np.array([(vector.x, vector.y, vector.z) for vector in points])
    points_x, points_y, points_z = points_array.T
    coords[0::4] = points_x
    coords[1::4] = points_y
    coords[2::4] = points_z
    spline.points.foreach_set('co', coords)
    
    curve_object = bpy.data.objects.new(name, curve_data)
    return curve_object