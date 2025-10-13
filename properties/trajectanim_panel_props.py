import bpy
from bpy.props import BoolProperty, EnumProperty, IntProperty, FloatProperty, StringProperty, CollectionProperty, PointerProperty
from bpy.types import PropertyGroup
from math import radians


class TargetProperty(PropertyGroup):
    object: PointerProperty(
        name='Object',
        description='',
        type=bpy.types.Object
    )

    name: StringProperty()
    icon: StringProperty()
    bone_name: StringProperty()


class TargetCollection(PropertyGroup):
    objects: CollectionProperty(type=TargetProperty)
    
    active_index: IntProperty(
        name='Active Index',
        description='',
        default=0
    )


class TrajectAnimPanelProperty(PropertyGroup):
    position_orientation: EnumProperty(
        name='Position Transformation Orientation',
        description='Property to define how transformation are applied',
        items=(
            ('GLOBAL', 'Global', 'Use global axis to orient position'),
            ('LOCAL', 'Local', "Use local axis to orient position"),
        ),
        default='GLOBAL',
    )

    rotation_orientation: EnumProperty(
        name='Rotation Transformation Orientation',
        description='Property to define how transformation are applied',
        items=(
            ('GLOBAL', 'Global', 'Use global axis to orient position'),
            ('LOCAL', 'Local', "Use local axis to orient position"),
        ),
        default='GLOBAL',
    )

    rotation_center: EnumProperty(
        name='Rotation Origin',
        description='Property to define the center origin for rotation. Does not affect Rotate Along Path',
        items=(
            ('OBJECT', 'Object', 'Use active object or first item from list as the rotation center'),
            ('CURSOR', '3D Cursor', "Use 3d cursor as the rotation center"),
        ),
        default='CURSOR',
    )

    delete_after_animate: BoolProperty(
        name='Delete After',
        description='When turned on, annotation/grease pencil current keyframe or curve object will be removed after applying animation',
        default=False,
    )

    rotate_along_path: BoolProperty(
        name='Rotate Along Path',
        description='When turned on, target animation will rotate along trajectory path',
        default=False,
    )

    reverse_path: BoolProperty(
        name='Reverse Path',
        description='When turned on, trajectory path will be reversed',
        default=False,
    )

    relative_path: BoolProperty(
        name='Relative to Path',
        description='When turned on, position will be relative to their current position and the trajectory. ' \
                    'Otherwise the position will snap to the trajectory position.',
        default=True,
    )

    initial_rotation: BoolProperty(
        name='Initial Rotation',
        description='When turned on, initial rotation will be added in addition to the trajectory rotation path. ' \
                    'Otherwise the rotation will be set to whatever is given based off the settings.',
        default=True,
    )

    target_behaviour: EnumProperty(
        name='Targets',
        description='Property to define the behaviour of defining target object/bone',
        items=(
            ('LIST', 'List', 'Only animate whatever is listed on the list'),
            ('SELECTED', 'Selected', 'Use selected objects as their target. Grease pencil and curves are excluded from this'),
        ),
        default='SELECTED',
    )

    timing: EnumProperty(
        name='Timing',
        description='Property to define the timing of animation',
        items=(
            ('POINTS', 'Points', 'Timing will be defined by total points of the stroke or the intersections'),
            ('DURATION', 'Duration', 'Timing will be defined by total frames, which is defined by user. ' \
                                     'If there is less duration than the amounts of points/intersection, ' \
                                     'then some points will be skipped to fit the total duration.'),
        ),
        default='POINTS',
    )

    duration: IntProperty(
        name='Duration',
        description='Maximum duration an animation should have. If stroke has more points than duration ' \
                    'set on this property, some frames will be skipped to fit this total duration. Otherwise ' \
                    'animation will be stretched.',
        min=2,
        default=10,
    )

    frame_step: IntProperty(
        name='Frame Step',
        description='Number of frames to skip after each frame',
        min=1,
        default=1,
    )

    interpolation: EnumProperty(
        name='Interpolation',
        description='Interpolation used for the keyframes',
        items=(
            ('CONSTANT', 'Constant', '', 'IPO_CONSTANT', 1),
            ('LINEAR', 'Linear', '', 'IPO_LINEAR', 2),
            ('BEZIER', 'Bezier', '', 'IPO_BEZIER', 3),
        ),
        default='LINEAR',
    )

    auto_axis: BoolProperty(
        name='Auto track and up axis',
        description='Determine track and up axis automatically',
        default=True,
    )

    auto_fix_rotation: BoolProperty(
        name='Fix Rotation',
        description='When enabled, script will attempt to fix rotation based off the track axis direction. ' \
                    'This is to ensure object always facing forward the path. Only works if Rotate Along Path is enabled.',
        default=True,
    )

    only_rotate_up: BoolProperty(
        name='Only rotate up (if rotate along path is enabled)',
        description='When enabled, disable any other rotation than the up axis. Only works when animating position ' \
                    'with Rotate Along Path enabled. Use this to prevent object twisting/flipping while following the path. ' \
                    'Only works if Rotate Along Path is enabled',
        default=True,
    )
    
    previous_axis: StringProperty(default='None')

    smooth_flips: BoolProperty(
        name='Smooth Flips',
        description='When enabled, the script will attempt to fix rotation that cause flip by negating the rotation.',
        default=True,
    )

    flip_threshold: FloatProperty(
        name='Angle Threshold',
        description='Threshold to detect flips. If rotation equal or higher than this angle, negate the rotation.',
        subtype='ANGLE',
        min=0.0,
        max=radians(360),
        default=radians(300),
    )

    map_to_zero: BoolProperty(
        name='Map to Zero',
        description='When enabled, rotation will not go over 360 degrees, and instead mapped to 0. ' \
                    'Only applicable for object with euler rotation.',
        default=True,
    )


class MovementAxis(PropertyGroup):
    x: BoolProperty(default=True)
    y: BoolProperty(default=True)
    z: BoolProperty(default=True)


class RotationAxis(PropertyGroup):
    x: BoolProperty(default=True)
    y: BoolProperty(default=True)
    z: BoolProperty(default=True)


class PositionOffset(PropertyGroup):
    x: FloatProperty(
        name='Position Offset X',
        description='Position used to offset when using Animate Position.',
        subtype='DISTANCE',
        default=0.0,
    )

    y: FloatProperty(
        name='Position Offset Y',
        description='Position used to offset when using Animate Position.',
        subtype='DISTANCE',
        default=0.0,
    )

    z: FloatProperty(
        name='Position Offset Y',
        description='Position used to offset when using Animate Position.',
        subtype='DISTANCE',
        default=0.0,
    )
    

class RotationOffset(PropertyGroup):
    x: FloatProperty(
        name='Rotation Offset X',
        description='Rotation used to offset when using Rotate Along Path or Animate Position. Suppressed when ' \
                    'Auto Fix Rotation is enabled.',
        subtype='ANGLE',
        min=radians(-360),
        max=radians(360),
        default=0.0,
    )

    y: FloatProperty(
        name='Rotation Offset Y',
        description='Rotation used to offset when using Rotate Along Path or Animate Position Suppressed when '
                    'Auto Fix Rotation is enabled.',
        subtype='ANGLE',
        min=radians(-360),
        max=radians(360),
        default=0.0,
    )

    z: FloatProperty(
        name='Rotation Offset Y',
        description='Rotation used to offset when using Rotate Along Path or Animate Position Suppressed when '
                    'Auto Fix Rotation is enabled.',
        subtype='ANGLE',
        min=radians(-360),
        max=radians(360),
        default=0.0,
    )
    

class TrackAxis(PropertyGroup):
    axis: EnumProperty(
        name='Track Axis',
        description='',
        items=(
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', ''),
            ('-X', '-X', ''),
            ('-Y', '-Y', ''),
            ('-Z', '-Z', ''),
        ),
        default='Y',
    )

class UpAxis(PropertyGroup):
    axis: EnumProperty(
        name='Up Axis',
        description='',
        items=(
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', ''),
        ),
        default='Z',
    )


def register():
    bpy.types.Scene.TrajectAnim_main_props = PointerProperty(type=TrajectAnimPanelProperty)
    bpy.types.Scene.TrajectAnim_target = PointerProperty(type=TargetCollection)
    bpy.types.Scene.TrajectAnim_movement_axis = PointerProperty(type=MovementAxis)
    bpy.types.Scene.TrajectAnim_rotation_axis = PointerProperty(type=RotationAxis)
    bpy.types.Scene.TrajectAnim_position_offset = PointerProperty(type=PositionOffset)
    bpy.types.Scene.TrajectAnim_rotation_offset = PointerProperty(type=RotationOffset)
    bpy.types.Scene.TrajectAnim_track_axis = PointerProperty(type=TrackAxis)
    bpy.types.Scene.TrajectAnim_up_axis = PointerProperty(type=UpAxis)

def unregister():
    del bpy.types.Scene.TrajectAnim_up_axis
    del bpy.types.Scene.TrajectAnim_track_axis
    del bpy.types.Scene.TrajectAnim_rotation_offset
    del bpy.types.Scene.TrajectAnim_position_offset
    del bpy.types.Scene.TrajectAnim_rotation_axis
    del bpy.types.Scene.TrajectAnim_movement_axis
    del bpy.types.Scene.TrajectAnim_target
    del bpy.types.Scene.TrajectAnim_main_props