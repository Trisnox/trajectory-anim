import bpy
import numpy as np
from ..functions import gpencil as gpencil_func


def convert_curve_to_gpencil(context: bpy.types.Context):
    scene = context.scene
    gpencil_props = scene.TrajectAnim_gpencil_props
    stroke_props = scene.TrajectAnim_stroke_props
    active_gpencil = gpencil_props.active_gpencil
    active_object = context.active_object

    if not active_gpencil:
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass

        bpy.ops.object.select_all(action='DESELECT')
        active_object.select_set(True)
        context.view_layer.objects.active = active_object

        bpy.ops.object.convert(target='GREASEPENCIL', keep_original=stroke_props.keep_original)
        gpencil_props.active_gpencil = context.active_object.data

        return True


    current_frame = context.scene.frame_current
    active_frame = gpencil_func.get_active_gpencil_frame(active_gpencil)

    if active_frame and active_frame.frame_number == current_frame:
        def draw(self, context):
            self.layout.label(text='Keyframe already exist on this frame')

        context.window_manager.popup_menu(draw, title='KEYFRAME ALREADY EXIST', icon='INFO')
        return False
    
    curve_data = active_object.data
    splines = curve_data.splines

    if len(splines) >= 2:
        def draw(self, context):
            self.layout.label(text='This curve contain more than one splines. Only active spline is converted')

        context.window_manager.popup_menu(draw, title='MULTIPLE SPLINES DETECTED', icon='INFO')

    # Honestly using bezier is pointless, because the animation will ended up moving in linear between points
    points_source = splines.active.points
    if not points_source:
        points_source = splines.active.bezier_points

    points = [vector.co for vector in points_source]

    active_frame = active_gpencil.layers.active.frames.new(current_frame)

    drawing = active_frame.drawing
    drawing.add_strokes([len(points)])
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
    points_array = np.array([(vector.x, vector.y, vector.z) for vector in points])
    points_x, points_y, points_z = points_array.T
    coords[0::3] = points_x
    coords[1::3] = points_y
    coords[2::3] = points_z
    position.foreach_set('vector', coords)
    
    if radius:
        stroke_thickness = bpy.data.brushes.get('Pencil', None)
        stroke_thickness = stroke_thickness.unprojected_radius if stroke_thickness else 0.5
        coords = np.full((point_length, 1), stroke_thickness, dtype=np.float64)
        radius.foreach_set('value', coords)

    if opacity:
        coords = np.full((point_length, 1), 1.0, dtype=np.float64)
        opacity.foreach_set('value', coords)

    if not stroke_props.keep_original:
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass

        bpy.data.curves.remove(curve_data, do_unlink=True)

    return True


from bpy.types import Operator


class GpencilToCurve(Operator):
    """Convert curve to grease pencil stroke. If Active Grease pencil is not set, then curve will be converted
using bpy.ops operator, otherwise curve will be converted into grease pencil directly into the whatever was
set on Active Grease Pencil prop. Keyframe will be added correspond to current frame on timeline"""
    bl_idname = "trajectanim.curve_to_gpencil"
    bl_label = "Convert curve into grease pencil"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        # Somehow context.curve raise AttributeError: 'Context' object has no attribute 'curve'
        # But it exist on documentation???
        # https://docs.blender.org/api/current/bpy.context.html#bpy.context.curve
        active_object = context.active_object
        return active_object and active_object.type == 'CURVE'

    def execute(self, context):
        result = convert_curve_to_gpencil(context)
        if not result:
            self.report({'INFO'}, 'Nothing to convert')
        else:
            self.report({'INFO'}, 'Successfully convert curve into grease pencil')

        return {'FINISHED'}
