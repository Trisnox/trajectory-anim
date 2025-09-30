import bpy
from mathutils import Vector


def get_active_gpencil_frame(gpencil: bpy.types.GreasePencilv3) -> bpy.types.GreasePencilFrame:
    """
        Function to return active frame of a grease pencil
    """
    active_layer = gpencil.layers.active
    if not active_layer:
        active_layer = gpencil.layers[0]
        gpencil.layers.active = active_layer

    active_frame = active_layer.current_frame()

    return active_frame


# drawing.stroke is much more convenient, but they are not recommended performance wise
# https://docs.blender.org/api/current/bpy.types.GreasePencilDrawing.html#bpy.types.GreasePencilDrawing.strokes
def get_strokes(frame: bpy.types.GreasePencilFrame) -> list[Vector]:
    drawing = frame.drawing
    for attribute in drawing.attributes:
        if attribute.name == 'position':
            position = attribute.data
            break
    
    # drawing.curve_offsets first item always have value of 0, so it's guaranteed that the first two item is the first stroke
    stroke_index = [index.value for index in drawing.curve_offsets]
    strokes = []
    for index in range(len(stroke_index) - 1):
        offset_start, offset_end = stroke_index[index], stroke_index[index+1]
        strokes.append([attr.vector for attr in position[offset_start:offset_end]])

    return strokes
