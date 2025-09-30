import bpy
import numpy as np
from ..functions import intersection
from ..functions import gpencil as gpencil_func


def self_intersect(context: bpy.types.Context):
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
        strokes = intersect_points_all
    else:
        strokes = intersect_points_only

    drawing.add_strokes([len(strokes)])
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
    points_array = np.array([(vector.x, vector.y, vector.z)
                            for vector in strokes])
    points_x, points_y, points_z = points_array.T
    coords[0::3] = points_x
    coords[1::3] = points_y
    coords[2::3] = points_z
    position.foreach_set('vector', coords)
    
    if radius:
        stroke_thickness = bpy.data.brushes['Pencil'].unprojected_radius
        coords = np.full((point_length, 1), stroke_thickness, dtype=np.float64)
        radius.foreach_set('value', coords)

    if opacity:
        coords = np.full((point_length, 1), 1.0, dtype=np.float64)
        opacity.foreach_set('value', coords)

    return True


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
        return active_gpencil

    def execute(self, context):
        result = self_intersect(context)
        if result is False:
            self.report({'INFO'}, 'No intersections were made')

        self.report({'INFO'}, 'Successfully intersect stroke')
        
        return {'FINISHED'}
