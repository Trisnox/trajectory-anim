import bpy
from mathutils import Color


# 5.0 RNA types related to annotation are renamed, while grease pencil only have some renamed
# https://developer.blender.org/docs/release_notes/5.0/python_api/#annotations-grease-pencil
def is_using_5_0():
    return bpy.app.version >= (5, 0, 0)

# annotation type: GreasePencil / Annotation
def get_active_annotation_frame(context: bpy.types.Context = None, annotation = None):
    """
        Function to return active frame of an annotation, and create one in case it's empty.
    """
    if not annotation and not context.annotation_data:
        annotation = context.blend_data.annotations.new('Annotations')
        active_layer = annotation.layers.new('Note', set_active=True)
        active_layer.color = Color((0.38, 0.612, 0.78))
        active_layer.thickness = 3

        if is_using_5_0():
            context.scene.annotation = annotation
        else:
            context.scene.greasepencil = annotation

    elif not annotation:
        active_layer = context.active_annotation_layer
    else:
        active_layer_index = annotation.layers.active_index
        active_layer = annotation.layers[active_layer_index]
        
    active_frame = active_layer.active_frame

    return active_layer, active_frame

# Unlike grease pencil, annotation strokes can be accessed through frame.strokes, so there is no need for get_stroke function
