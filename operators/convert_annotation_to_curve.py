import bpy
from mathutils import Vector
from ..functions import intersection
from ..functions import curve as curve_func
from ..functions import annotation as annotation_func


def convert_stroke(annotation: bpy.types.GPencilStroke) -> list[Vector]:
    position = []
    points = annotation.points
    for vector in points:
        position.append(vector.co)
    
    return position

def convert_intersection(annotation: list[bpy.types.GPencilStroke]) -> list[Vector]:
    source_stroke = [vector.co for vector in annotation[0].points]
    stroke_targets = []
    for stroke in annotation[1:]:
        stroke_targets.append([vector.co for vector in stroke.points])
    intersect_only, _ = intersection.find_stroke_intersection(source_stroke, stroke_targets)

    return intersect_only


def convert_annotation_to_curve(context: bpy.types.Context):
    stroke_props = context.scene.TrajectAnim_stroke_props

    _, active_frame = annotation_func.get_active_annotation_frame(context=context)
    strokes = active_frame.strokes

    convert_method = stroke_props.convert_method
    if convert_method == 'POINTS' or (convert_method == 'AUTO' and len(strokes) == 1):
        points = convert_stroke(strokes[0])
    else:
        points = convert_intersection(strokes)

    curve_name = 'annotation_frame_' + str(active_frame.frame_number)
    curve_object = curve_func.create_poly_curve(curve_name, points)
    context.collection.objects.link(curve_object)

    if not stroke_props.keep_original:
        bpy.ops.gpencil.annotation_active_frame_delete()

    if context.mode == 'OBJECT':
        bpy.ops.object.select_all(action='DESELECT')
        curve_object.select_set(True)
        context.view_layer.objects.active = curve_object

    return True


from bpy.types import Operator


class AnnotationToCurve(Operator):
    """Convert annotation strokes into curve"""
    bl_idname = "trajectanim.annotation_to_curve"
    bl_label = "Convert annotation strokes into curve"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        annotation = context.annotation_data
        return annotation

    def execute(self, context):
        result = convert_annotation_to_curve(context)
        if not result:
            self.report({'INFO'}, 'Nothing to convert')
        else:
            self.report({'INFO'}, 'Successfully convert annotation into curve')

        return {'FINISHED'}