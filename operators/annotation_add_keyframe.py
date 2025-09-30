import bpy


def annotation_add_blank_keyframe(context: bpy.types.Context):
    scene = context.scene
    annotation_props = scene.TrajectAnim_annotation_props
    annotation = context.annotation_data
    
    layers = []

    if annotation_props.all_layers is True:
        layers = [layer for layer in annotation.layers]
    else:
        active_layer_index = annotation.layers.active_index
        active_layer = annotation.layers[active_layer_index]
        layers.append(active_layer)

    for layer in layers:
        layer.frames.new(scene.frame_current)

    return True, len(layers)


from bpy.types import Operator


class ClearExcessStroke(Operator):
    """Add blank keyframe to annotation. Useful to hide stroke on certain keyframes"""
    bl_idname = "trajectanim.annotation_add_blank_keyframe"
    bl_label = "Annotation Add Blank Keyframe"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        annotation = context.annotation_data
        return annotation

    def execute(self, context):
        result, num = annotation_add_blank_keyframe(context)

        self.report({'INFO'}, f'Successfully added blank keyframe to {num} layers')
        
        return {'FINISHED'}