import bpy
import numpy as np
from ..functions import intersection
from ..functions import annotation as annotation_func, curve as curve_func, gpencil as gpencil_func


def convert_gpencil_to_curve(context: bpy.types.Context):
    stroke_props = context.scene.TrajectAnim_stroke_props

    gpencil = context.grease_pencil
    active_frame = gpencil_func.get_active_gpencil_frame(gpencil)
    strokes = gpencil_func.get_strokes(active_frame)

    convert_method = stroke_props.convert_method
    if convert_method == 'POINTS' or (convert_method == 'AUTO' and len(strokes) == 1):
        points = [vector for vector in strokes[0]]
    else:
        points, _ = intersection.find_stroke_intersection(strokes[0], strokes[1:])

    curve_name = 'gpencil_frame_' + str(active_frame.frame_number)
    curve_object = curve_func.create_poly_curve(curve_name, points)
    context.collection.objects.link(curve_object)

    if not stroke_props.keep_original:
        bpy.ops.grease_pencil.active_frame_delete()

    if context.mode == 'OBJECT':
        bpy.ops.object.select_all(action='DESELECT')
        curve_object.select_set(True)
        context.view_layer.objects.active = curve_object

    return True

def convert_gpencil_to_annotation(context: bpy.types.Context):
    active_layer, active_frame = annotation_func.get_active_annotation_frame(context)
    current_frame = context.scene.frame_current
    stroke_props = context.scene.TrajectAnim_stroke_props

    if active_frame and active_frame.frame_number == current_frame:
        def draw(self, context):
            self.layout.label(text='Keyframe already exist on this frame')

        context.window_manager.popup_menu(draw, title='KEYFRAME ALREADY EXIST', icon='INFO')
        return False

    gpencil = context.grease_pencil
    active_frame = gpencil_func.get_active_gpencil_frame(gpencil)
    strokes = gpencil_func.get_strokes(active_frame)

    convert_method = stroke_props.convert_method
    if convert_method == 'POINTS' or (convert_method == 'AUTO' and len(strokes) == 1):
        points = [vector for vector in strokes[0]]
    else:
        points, _ = intersection.find_stroke_intersection(strokes[0], strokes[1:])

    active_frame = active_layer.frames.new(current_frame)
    
    stroke = active_frame.strokes.new()
    stroke.points.add(len(points))

    coords = np.zeros(len(points) * 3, dtype=np.float64)
    stroke.points.foreach_get('co', coords)
    points_array = np.array([(vector.x, vector.y, vector.z) for vector in points])
    points_x, points_y, points_z = points_array.T
    coords[0::3] = points_x
    coords[1::3] = points_y
    coords[2::3] = points_z
    stroke.points.foreach_set('co', coords)

    if not stroke_props.keep_original:
        bpy.ops.grease_pencil.active_frame_delete()


from bpy.types import Operator


class GpencilToCurve(Operator):
    """Convert grease pencil strokes into curve"""
    bl_idname = "trajectanim.gpencil_to_curve"
    bl_label = "Convert grease pencil strokes into curve"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        gpencil = context.grease_pencil
        return gpencil is not None

    def execute(self, context):
        result = convert_gpencil_to_curve(context)
        if not result:
            self.report({'INFO'}, 'Nothing to convert')
        else:
            self.report({'INFO'}, 'Successfully convert grease pencil into curve')

        return {'FINISHED'}


class GpencilToAnnotation(Operator):
    """Convert grease pencil strokes into annotation"""
    bl_idname = "trajectanim.gpencil_to_annotation"
    bl_label = "Convert grease pencil strokes into annotation"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        gpencil = context.grease_pencil
        return gpencil is not None

    def execute(self, context):
        result = convert_gpencil_to_annotation(context)
        if not result:
            self.report({'INFO'}, 'Nothing to convert')
        else:
            self.report({'INFO'}, 'Successfully convert grease pencil into annotation')

        return {'FINISHED'}
