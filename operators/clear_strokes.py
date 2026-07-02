import bpy
from ..functions import annotation as annotation_func


# 5.2 has update regarding annotation, they now have function to modify strokes and points
# https://developer.blender.org/docs/release_notes/5.2/python_api/#annotations
def is_using_5_2():
    return bpy.app.version >= (5, 2, 0)


def clear_strokes(context: bpy.types.Context, remove_all: bool = False):
    scene = context.scene
    stroke_props = scene.TrajectAnim_stroke_props
    stroke_mode = stroke_props.target

    if stroke_mode == 'AUTO':
        active_object = context.active_object
        if active_object and active_object.type == 'GREASEPENCIL':
            stroke_mode = 'GPENCIL'
        elif active_object and active_object.type == 'CURVE':
            stroke_mode = 'CURVE'
        else:
            stroke_mode = 'ANNOTATION'

    if is_using_5_2() and stroke_mode == 'ANNOTATION':
        _, active_frame = annotation_func.get_active_annotation_frame(context=context)
        strokes = active_frame.strokes

        if len(strokes) == 0:
            return False

        if not remove_all:
            for stroke in strokes[1:]:
                strokes.remove(stroke)
        else:
            for stroke in strokes:
                strokes.remove(stroke)

    elif stroke_mode == 'GPENCIL':
        active_gpencil = context.grease_pencil
        active_frame = active_gpencil.layers.active.current_frame()

        if not active_frame:
            return False

        drawing = active_frame.drawing

        stroke_index = [index.value for index in drawing.curve_offsets[1:]]
        if len(stroke_index) == 1:
            return False
        
        if not remove_all:
            indices = list(range(1, len(stroke_index)))
            drawing.remove_strokes(indices=indices)
        else:
            drawing.remove_strokes()
    
    
    return True


from bpy.types import Operator


class ClearExcessStroke(Operator):
    """Remove excess strokes, use this to remove all but the first stroke"""
    bl_idname = "trajectanim.clear_excess_strokes"
    bl_label = "Remove excess strokes"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        active_gpencil = context.grease_pencil
        annotation = context.annotation_data
        return active_gpencil or annotation

    def execute(self, context):
        result = clear_strokes(context)
        if result is False:
            self.report({'INFO'}, 'No strokes to clear')

        self.report({'INFO'}, 'Successfully remove excess strokes')
        
        return {'FINISHED'}
    

class ClearAllStrokes(Operator):
    """Remove all strokes, but keep the keyframe"""
    bl_idname = "trajectanim.clear_all_strokes"
    bl_label = "Remove all strokes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        active_gpencil = context.grease_pencil
        annotation = context.annotation_data
        return active_gpencil or annotation

    def execute(self, context):
        result = clear_strokes(context, True)
        if result is False:
            self.report({'INFO'}, 'No strokes to clear')

        self.report({'INFO'}, 'Successfully remove all strokes')

        return {'FINISHED'}
