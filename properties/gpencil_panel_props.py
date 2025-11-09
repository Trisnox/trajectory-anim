import bpy
from bpy.props import EnumProperty, PointerProperty
from bpy.types import PropertyGroup


# 5.0 RNA types related to annotation are renamed, while grease pencil only have some renamed
# https://developer.blender.org/docs/release_notes/5.0/python_api/#annotations-grease-pencil
def is_using_5_0():
    return bpy.app.version >= (5, 0, 0)

def get_type():
    if is_using_5_0():
        return bpy.types.GreasePencil
    return bpy.types.GreasePencilv3

class AnnotationPanelProperty(PropertyGroup):
    active_gpencil: PointerProperty(
        name='Active Grease Pencil',
        description='Grease Pencil datablock to work with',
        type=get_type(),
    )

    intersection_method: EnumProperty(
        name='Intersection Method',
        description='Intersection method to use',
        items=(
            ('REPLACE', 'Replace', 'Remove all points aside from starting, ending, and intersection'),
            ('ADD', 'Add', 'Add points on intersections, as well keeping the original points'),
        ),
        default='ADD',
    )

def register():
    bpy.types.Scene.TrajectAnim_gpencil_props = PointerProperty(type=AnnotationPanelProperty)

def unregister():
    del bpy.types.Scene.TrajectAnim_gpencil_props
