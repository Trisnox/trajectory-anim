import bpy
from bpy.props import EnumProperty, PointerProperty
from bpy.types import PropertyGroup


class AnnotationPanelProperty(PropertyGroup):
    active_gpencil: PointerProperty(
        name='Active Grease Pencil',
        description='Grease Pencil datablock to work with',
        type=bpy.types.GreasePencilv3,
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
