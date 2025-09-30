import bpy
from bpy.props import BoolProperty, EnumProperty, PointerProperty
from bpy.types import PropertyGroup


class StrokePanelProperty(PropertyGroup):
    keep_original: BoolProperty(
        name='Keep Original',
        description='When turned on, stroke will not be removed '
                    'after converting into curve. Otherwise '
                    'the active frame will be removed after conversion.',
        default=True,
    )

    convert_method: EnumProperty(
        name='Convert Method',
        description='Property to define which operator suited for curve conversion/trajectory animation',
        items=(
            ('AUTO', 'Automatic', 'Automatic operation, use each point if there is only single stroke, otherwise use intersections'),
            ('POINTS', 'Points', 'Use each points. Note: Only first stroke/curve will be used, any subsequent stroke/curve will be ignored'),
            ('INTERSECTION', 'Intersection', 'Calculate vector point where stroke intersection meets, as well including starting and ending points'),
        ),
        default='AUTO',
    )

    target: EnumProperty(
        name='Target',
        description='Target used for operator for this panel. Can be used to override annotation tool over grease pencil',
        items=(
            ('AUTO', 'Automatic', 'Automatic detection. If no Grease Pencil or curve object is selected, then assumes using annotation'),
            ('ANNOTATION', 'Annotation', ''),
            ('GPENCIL', 'Grease Pencil', 'Will always prioritize selected Grease Pencil object. If there are none, then the active grease pencil from `Active Grease Pencil` property will be used'),
            ('CURVE', 'Curve', ''),
        ),
        default='AUTO',
    )

    self_intersect_method: EnumProperty(
        name='Self Intersection Method',
        description='Property to define how strokes will be intersected',
        items=(
            ('ADD', 'Keep Original Points', 'Intersection line will be added in addition to the original points'),
            ('REPLACE', 'Replace with Intersection', 'All points are removed, except for the starting, intersection, and ending points'),
        ),
        default='REPLACE',
    )

def register():
    bpy.types.Scene.TrajectAnim_stroke_props = PointerProperty(type=StrokePanelProperty)

def unregister():
    del bpy.types.Scene.TrajectAnim_stroke_props