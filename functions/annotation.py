import bpy


def get_active_annotation_frame(context: bpy.types.Context = None, annotation: bpy.types.GreasePencil = None):
    """
        Function to return active frame of an annotation
    """
    if not annotation:
        active_layer = context.active_annotation_layer
    else:
        active_layer_index = annotation.layers.active_index
        active_layer = annotation.layers[active_layer_index]
        
    active_frame = active_layer.active_frame

    return active_layer, active_frame

# Unlike grease pencil, annotation strokes can be accessed through frame.strokes, so there is no need for get_stroke function
# They are also read-only, and there is no such function to add/remove strokes, so there's not much we can do about annotations
# https://docs.blender.org/api/current/bpy.types.GPencilFrame.html#bpy.types.GPencilFrame
