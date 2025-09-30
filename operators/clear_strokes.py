import bpy


def clear_strokes(context: bpy.types.Context, remove_all: bool = False):
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
        drawing.remove_strokes() # passing None to indices cause error?
    
    
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
        return active_gpencil

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
        return active_gpencil

    def execute(self, context):
        result = clear_strokes(context, True)
        if result is False:
            self.report({'INFO'}, 'No strokes to clear')

        self.report({'INFO'}, 'Successfully remove all strokes')

        return {'FINISHED'}
