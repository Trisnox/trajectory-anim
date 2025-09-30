import bpy
from ..functions import intersection
from ..functions import curve as curve_func
from ..functions import gpencil as gpencil_func


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
