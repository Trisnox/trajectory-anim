import bpy
import numpy as np
from ..functions import intersection
from ..functions import gpencil as gpencil_func, annotation as annotation_func


# 5.2 has update regarding annotation, they now have function to modify strokes and points
# https://developer.blender.org/docs/release_notes/5.2/python_api/#annotations
def is_using_5_2():
    return bpy.app.version >= (5, 2, 0)


def intersect_annotation(context: bpy.types.Context):
    stroke_props = context.scene.TrajectAnim_stroke_props
    _, active_frame = annotation_func.get_active_annotation_frame(context)

    if not active_frame:
        return False

    strokes = []
    for stroke in active_frame.strokes:
        strokes += [[vector.co for vector in stroke.points]]

    intersect_points_only, intersect_points_all = intersection.find_stroke_intersection(strokes[0], strokes[1:])

    if stroke_props.self_intersect_method == 'ADD':
        intersect_strokes = intersect_points_all
    else:
        intersect_strokes = intersect_points_only
    
    for stroke in active_frame.strokes:
        active_frame.strokes.remove(stroke)

    new_stroke = active_frame.strokes.new()
    new_stroke.points.add(len(intersect_strokes))

    coords = np.zeros(len(intersect_strokes) * 3, dtype=np.float64)
    new_stroke.points.foreach_get('co', coords)
    points_array = np.array([(vector.x, vector.y, vector.z) for vector in intersect_strokes])
    points_x, points_y, points_z = points_array.T
    coords[0::3] = points_x
    coords[1::3] = points_y
    coords[2::3] = points_z
    new_stroke.points.foreach_set('co', coords)

    return True


def intersect_gpencil(context: bpy.types.Context):
    stroke_props = context.scene.TrajectAnim_stroke_props
    active_gpencil = context.grease_pencil
    active_frame = gpencil_func.get_active_gpencil_frame(active_gpencil)

    if not active_frame:
        return False
    
    drawing = active_frame.drawing
    strokes = gpencil_func.get_strokes(active_frame)

    intersect_points_only, intersect_points_all = intersection.find_stroke_intersection(strokes[0], strokes[1:])
    
    drawing.remove_strokes()
    if stroke_props.self_intersect_method == 'ADD':
        intersect_strokes = intersect_points_all
    else:
        intersect_strokes = intersect_points_only

    drawing.add_strokes([len(intersect_strokes)])
    radius = None
    position = None
    opacity = None
    for attribute in drawing.attributes:
        if attribute.name == 'radius':
            radius = attribute.data
        if attribute.name == 'position':
            position = attribute.data
        if attribute.name == 'opacity':
            opacity = attribute.data
        
        if all((radius, position, opacity)):
            break
    
    point_length = len(position)
    coords = np.zeros(point_length * 3, dtype=np.float64)
    position.foreach_get('vector', coords)
    points_array = np.array([(vector.x, vector.y, vector.z) for vector in intersect_strokes])
    points_x, points_y, points_z = points_array.T
    coords[0::3] = points_x
    coords[1::3] = points_y
    coords[2::3] = points_z
    position.foreach_set('vector', coords)
    
    if radius:
        stroke_thickness = bpy.data.brushes['Pencil'].unprojected_size
        coords = np.full((point_length, 1), stroke_thickness, dtype=np.float64)
        radius.foreach_set('value', coords)

    if opacity:
        coords = np.full((point_length, 1), 1.0, dtype=np.float64)
        opacity.foreach_set('value', coords)

    return True


def self_intersect(context: bpy.types.Context):
    stroke_props = context.scene.TrajectAnim_stroke_props
    stroke_mode = stroke_props.target

    if stroke_mode == 'AUTO':
        active_object = context.active_object
        if active_object and active_object.type == 'GREASEPENCIL':
            stroke_mode = 'GPENCIL'
        elif active_object and active_object.type == 'CURVE':
            stroke_mode = 'CURVE'
        else:
            stroke_mode = 'ANNOTATION'
    
    if stroke_mode == 'ANNOTATION' and is_using_5_2():
        return intersect_annotation(context)
    elif stroke_mode == 'GPENCIL':
        return intersect_gpencil(context)

    return False


from bpy.types import Operator


class SelfIntersect(Operator):
    """Intersect active stroke.
Replace the current stroke, depending on the option,
the new stroke will have points on the intersection.
This operator does not need to be called prior to applying animation"""
    bl_idname = "trajectanim.intersect_stroke"
    bl_label = "Intersect stroke"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        active_gpencil = context.grease_pencil
        annotation = context.annotation_data
        return active_gpencil or annotation

    def execute(self, context):
        result = self_intersect(context)
        if result is False:
            self.report({'INFO'}, 'No intersections were made')

        self.report({'INFO'}, 'Successfully intersect stroke')
        
        return {'FINISHED'}
