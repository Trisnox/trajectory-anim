import bpy
from bpy.props import BoolProperty, PointerProperty
from bpy.types import PropertyGroup


class AnnotationPanelProperty(PropertyGroup):
    all_layers: BoolProperty(
        name='All Layers',
        description='Insert blank keyframe will also apply to other layers as well, instead of only the active ones',
        default=False,
    )

def register():
    bpy.types.Scene.TrajectAnim_annotation_props = PointerProperty(type=AnnotationPanelProperty)

def unregister():
    del bpy.types.Scene.TrajectAnim_annotation_props
