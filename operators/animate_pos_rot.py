import bpy
import numpy as np
from math import degrees, radians
from mathutils import Vector, Euler, Quaternion, Matrix
from ..functions import intersection
from ..functions import annotation as annotation_func
from ..functions import gpencil as gpencil_func


# 4.4 introduces slotted actions
# https://developer.blender.org/docs/release_notes/4.4/python_api/#slotted-actions
def is_using_newer_version():
    return bpy.app.version >= (4, 4, 0)


def convert_intersection(strokes: list) -> list[Vector]:
    source_stroke = strokes[0]
    stroke_targets = strokes[1:]
    intersect_only, _ = intersection.find_stroke_intersection(source_stroke, stroke_targets)

    return intersect_only


def get_action(object: bpy.types.Object, name: str):
    action = bpy.data.actions.get(name, None)
    if not action:
        action = bpy.data.actions.new(name=name)

    if not object.animation_data:
        object.animation_data_create()

    if is_using_newer_version():
        if not len(action.slots):
            slot = action.slots.new(id_type='OBJECT', name=name)
        else:
            slot = action.slots[0]

        if not action.layers:
            layer = action.layers.new('Layer')
            strip = layer.strips.new(type='KEYFRAME')
            channelbag = strip.channelbag(slot, ensure=True)

        object.animation_data.action = action
        object.animation_data.action_slot = slot
    else:
        object.animation_data.action = action

    return action


def auto_determine_axis(points: list[Vector]):
    if len(points) < 2:
        return 'Y', 'Z'
    
    points = np.array([(vector.x, vector.y, vector.z) for vector in points])
    directions = np.diff(points, axis=0)
    
    if len(directions) == 0:
        return 'Y', 'Z'
    
    mean_direction = np.mean(directions, axis=0)
    mean_norm = np.linalg.norm(mean_direction)
    if mean_norm > 0:
        mean_direction /= mean_norm
    
    abs_direction = np.abs(mean_direction)
    dominant_axis_idx = np.argmax(abs_direction)
    
    track_value = mean_direction[dominant_axis_idx]
    track_axis = ['X', 'Y', 'Z'][dominant_axis_idx]
    if (track_value < 0 and track_axis in ('Y', 'Z')) or (track_value >= 0 and track_axis == 'X'):
        track_axis = '-' + track_axis
    
    variances = np.var(directions, axis=0)
    up_axis_idx = np.argmin(variances)
    up_axis = ['X', 'Y', 'Z'][up_axis_idx]
    
    if up_axis_idx == dominant_axis_idx:
        sorted_indices = np.argsort(variances)
        for idx in sorted_indices:
            if idx != dominant_axis_idx:
                up_axis_idx = idx
                up_axis = ['X', 'Y', 'Z'][up_axis_idx]
                break

    return track_axis, up_axis

def get_rotation_difference(current_vector: Vector, next_vector: Vector, origin_offset: Vector, rotation_axis, previous_rotation: Quaternion):
    current_vector = origin_offset - current_vector.copy()
    next_vector = origin_offset - next_vector.copy()
    rotation_difference = current_vector.rotation_difference(next_vector)

    if not all((rotation_axis.x, rotation_axis.y, rotation_axis.z)):
        rotation_difference = rotation_difference.to_euler()
        if not rotation_axis.x:
            rotation_difference.x = 0.0
        if not rotation_axis.y:
            rotation_difference.y = 0.0
        if not rotation_axis.z:
            rotation_difference.z = 0.0
        rotation_difference = rotation_difference.to_quaternion()

    rotation_difference = rotation_difference @ previous_rotation
    
    return rotation_difference

# Gosh I love maths because I don't understand any of them
# https://blenderartists.org/t/trying-to-simulate-follow-path-constraint-using-just-python/1142440
def get_track_rotation(previous_vector: Vector, current_vector: Vector, next_vector: Vector, track_axis: str, up_axis: str, only_rotate_up, rotation_axis, rotation_offset: Quaternion):
    if up_axis == 'X':
        world_up = Vector((1.0, 0.0, 0.0))
    elif up_axis == 'Y':
        world_up = Vector((0.0, 1.0, 0.0))
    else:
        world_up = Vector((0.0, 0.0, 1.0))

    # Assumes first item.
    if previous_vector is None:
        tangent = (next_vector - current_vector).normalized()
    else:
        incoming_tangent = (current_vector - previous_vector).normalized()
        outgoing_tangent = (next_vector - current_vector).normalized()
        tangent = (outgoing_tangent + incoming_tangent).normalized()

    right = tangent.cross(world_up)
    right.normalize()
    up = right.cross(tangent).normalized()

    if track_axis.startswith('-'):
        right = -right
        tangent = -tangent

    if track_axis.endswith('X'):
        rotation_difference = Matrix([
            [tangent.x, right.x, up.x, 0.0],
            [tangent.y, right.y, up.y, 0.0],
            [tangent.z, right.z, up.z, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ]).to_quaternion()
    elif track_axis.endswith('Y'):
        rotation_difference = Matrix([
            [right.x, tangent.x, up.x, 0.0],
            [right.y, tangent.y, up.y, 0.0],
            [right.z, tangent.z, up.z, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ]).to_quaternion()
    else:
        rotation_difference = Matrix([
            [right.x, up.x, tangent.x, 0.0],
            [right.y, up.y, tangent.y, 0.0],
            [right.z, up.z, tangent.z, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ]).to_quaternion()

    rotation_difference = rotation_difference @ rotation_offset

    if only_rotate_up or not all((rotation_axis.x, rotation_axis.y, rotation_axis.z)):
        rotate_x = up_axis == 'X' if only_rotate_up else rotation_axis.x
        rotate_y = up_axis == 'Y' if only_rotate_up else rotation_axis.y
        rotate_z = up_axis == 'Z' if only_rotate_up else rotation_axis.z

        rotation_difference = rotation_difference.to_euler()
        if not rotate_x:
            rotation_difference.x = 0.0
        if not rotate_y:
            rotation_difference.y = 0.0
        if not rotate_z:
            rotation_difference.z = 0.0
        rotation_difference = rotation_difference.to_quaternion()
        
    
    return rotation_difference


def keyframe_pairing(position: list[Vector], target_frames: int, frame_step: int, include_rotation: bool, center_rotation: Vector, only_rotate_up: bool, rotation_axis, rotation_type: str, is_reverse: bool, track_axis: str, up_axis: str, rotation_offset: Quaternion) -> list[tuple]:
    """ Function to pair keyframe and position w/o rotation.
        Also to stretch/expand keyframe timing to fit total frames duration if it uses any.
    """
    if is_reverse:
        position = list(reversed(position))

    keyframe_data = []
    
    if target_frames == len(position):
        keyframe_data = []
        previous_rotation = Quaternion()
        previous_vector = None

        for index, current_vector in enumerate(position):
            if include_rotation and not index == len(position) - 1:
                next_vector = position[index+1]

                if rotation_type == 'ROTATION':
                    rotation_difference = get_rotation_difference(current_vector, next_vector, center_rotation, rotation_axis, previous_rotation)
                else:
                    rotation_difference = get_track_rotation(previous_vector, current_vector, next_vector, track_axis, up_axis, only_rotate_up, rotation_axis, rotation_offset)

                previous_rotation = rotation_difference
            else:
                rotation_difference = previous_rotation

            previous_vector = current_vector

            if not index == 0:
                index *= frame_step

            keyframe_data.append([index, current_vector.copy(), rotation_difference.copy(), False])

        return keyframe_data
    
    else:
        item_length = len(position)
        step = (item_length - 1) / (target_frames - 1)
        previous_index = None
        previous_rotation = Quaternion() # It's quaternion because it only affect get_rotation_difference
        rotation_difference = None
        previous_vector = None

        for index in range(target_frames):
            nearest_index = index * step
            nearest_index = round(nearest_index)
            nearest_index = min(nearest_index, item_length - 1)

            if previous_index == nearest_index:
                continue

            if include_rotation and not index == target_frames - 1:
                next_nearest = (index + 1) * step
                next_nearest = round(next_nearest)
                next_nearest = min(next_nearest, item_length - 1)
                next_vector = position[next_nearest]
                current_vector = position[nearest_index]

                if rotation_type == 'ROTATION':
                    rotation_difference = get_rotation_difference(current_vector, next_vector, center_rotation, rotation_axis, previous_rotation)
                else:
                    rotation_difference = get_track_rotation(previous_vector, current_vector, next_vector, track_axis, up_axis, only_rotate_up, rotation_axis, rotation_offset)

                previous_rotation = rotation_difference.copy()
            else:
                rotation_difference = previous_rotation

            previous_index = nearest_index

            if not index == 0:
                index *= frame_step

            keyframe_data.append([index, position[nearest_index].copy(), rotation_difference.copy(), False])

    return keyframe_data


# This can be improved by passing argument that determine whether it should calculate position only, rotation only, or both
# Right now, it will calculate both position and rotation regardless, though it's already fast as is, as such this can be put into lower priority
def process_keyframe(context: bpy.types.Context, keyframe_data: list, target_object: bpy.types.Object|bpy.types.PoseBone, relative_path: bool, initial_rotation: bool, orientation_location: str, orientation_rotation: str, movement_axis, rotation_type: str, smooth_flips: bool, flip_threshold: float):
    """ Function to properly set keyframe timing correspond to current frame, as well transform position
        and rotation correspond to global or local axis
    """
    current_frame = context.scene.frame_current
    keyframes = []

    # Note to self: always copy vector if you want to do operation on them, especially on animation...
    first_position = keyframe_data[0][1].copy()
    previous_rotation = None
    keyframe_count = len(keyframe_data)
    for index, (frame, location, rotation, is_rotation_negated) in enumerate(keyframe_data):
        new_matrix = Matrix()
        frame = current_frame + frame
        is_using_matrix_location = False
        is_using_matrix_rotation = False

        if relative_path:
            location -= first_position

        if not movement_axis.x:
            location.x = 0.0
        if not movement_axis.y:
            location.y = 0.0
        if not movement_axis.z:
            location.z = 0.0

        # https://blender.stackexchange.com/questions/44760/rotate-objects-around-their-origin-along-a-global-axis-scripted-without-bpy-op
        if isinstance(target_object, bpy.types.Object):
            matrix = target_object.matrix_world.copy()
        else:
            matrix = target_object.matrix.copy()
        matrix_inverted = matrix.copy().inverted()

        object_location, object_rotation, object_scale = matrix.decompose()
        if not initial_rotation:
            object_rotation = Quaternion()

        location_matrix = Matrix.Translation(object_location)
        rotation_matrix = object_rotation.to_matrix().to_4x4()
        scale_matrix = Matrix.Scale(object_scale[0],4,(1,0,0)) * Matrix.Scale(object_scale[1],4,(0,1,0)) @ Matrix.Scale(object_scale[2],4,(0,0,1))

        new_matrix = scale_matrix

        if orientation_rotation == 'GLOBAL':
            is_using_matrix_rotation = True
            rotation = rotation.to_matrix().to_4x4()

            new_matrix = rotation @ rotation_matrix @ new_matrix
        else:
            # Applicable for location. This allows for moving object in global axis even if the object initial rotation transform is not applied
            if orientation_location == 'GLOBAL':
                new_matrix = rotation_matrix @ new_matrix

            if target_object.rotation_mode == 'QUATERNION' and not initial_rotation:
                object_rotation = target_object.rotation_quaternion
            elif not initial_rotation:
                object_rotation = target_object.rotation_euler.to_quaternion()

            transformed_rotation = object_rotation @ rotation # simply swapping makes it rotate along local... huh...

        if orientation_location == 'GLOBAL':
            is_using_matrix_location = True
            location = Matrix.Translation(location)

            if relative_path:
                new_matrix = location @ location_matrix @ new_matrix
            else:
                new_matrix = location @ new_matrix
        else:
            local_transform = location @ matrix_inverted

            if relative_path:
                transformed_location = local_transform + object_location
            else:
                transformed_location = local_transform
            
        new_transformed_location, new_transformed_rotation, _ = new_matrix.decompose()
        if is_using_matrix_location:
            transformed_location = new_transformed_location
        if is_using_matrix_rotation:
            transformed_rotation = new_transformed_rotation

        # TODO: Not perfect, but it gets the job done
        # Another solution would be to use slerp? By taking the latest and older non-flipped rotation,
        # the inbetween can be later interpolated. Haven't test the result because I don't understand math
        # Worse result when converted into euler as negate() does nothing when converted into euler
        # Somehow has better result when map_to_zero is disabled compared to quaternion
        if smooth_flips and rotation_type == 'PATH' and previous_rotation is not None:
            if previous_rotation.rotation_difference(transformed_rotation).angle >= flip_threshold:
                transformed_rotation.negate()
                is_rotation_negated = True
        

        previous_rotation = transformed_rotation.copy()
        keyframes.append((frame, transformed_location, transformed_rotation, is_rotation_negated))

    return keyframes
        

def negate_euler(rotation: Euler, map_to_zero: bool):
    for vector_index, vector in enumerate(rotation):
        # I could do this, or make if statement for each operation that is negative..
        is_negative = False
        if vector < 0:
            is_negative = True
            vector = +vector
        
        negated_rotation = degrees(vector) - 360

        # Probably should not round this, was meant to prevent unaffected rotation
        if negated_rotation == -360:
            negated_rotation = 0

        if map_to_zero and negated_rotation <= -360:
            negated_rotation = negated_rotation % -360
        
        if is_negative and negated_rotation >= 0:
            negated_rotation = -negated_rotation
        
        rotation[vector_index] = radians(negated_rotation)

    return rotation


def apply_animation(keyframe_data: list, action: bpy.types.Action, data_path_mode: str, use_position: bool, use_rotation: bool, rotation_mode: str, interpolation: str, bone_name: str, map_to_zero: bool):
    data_path_location = 'location' if data_path_mode == 'OBJECT' else f'pose.bones["{bone_name}"].location'
    if rotation_mode == 'EULER':
        # Armature uses quaternion by default
        # There is no reason to use euler on armature, unless you're crazy freaks
        data_path_rotation = 'rotation_euler' if data_path_mode == 'OBJECT' else f'pose.bones["{bone_name}"].rotation_euler'
    else:
        data_path_rotation = 'rotation_quaternion' if data_path_mode == 'OBJECT' else f'pose.bones["{bone_name}"].rotation_quaternion'

    bone_fcurves_location = []
    bone_fcurves_rotation = []
    rotation_enum = 3 if rotation_mode == 'EULER' else 4
    
    if is_using_newer_version():
        fcurves = action.layers[0].strips[0].channelbag(action.slots[0]).fcurves
    else:
        fcurves = action.fcurves

    for fcurve in fcurves:
        if fcurve.data_path == data_path_location and use_position:
            bone_fcurves_location.append(fcurve)
        elif fcurve.data_path == data_path_rotation and use_rotation:
            bone_fcurves_rotation.append(fcurve)

    if not bone_fcurves_location and use_position:
        if is_using_newer_version():
            bone_fcurves_location = [fcurves.new(data_path=data_path_location, index=i) for i in range(3)]
        else:
            bone_fcurves_location = [fcurves.new(data_path=data_path_location, index=i, action_group=bone_name) for i in range(3)]

    if not bone_fcurves_rotation and use_rotation:
        if is_using_newer_version():
            bone_fcurves_rotation = [fcurves.new(data_path=data_path_rotation, index=i) for i in range(rotation_enum)]
        else:
            bone_fcurves_rotation = [fcurves.new(data_path=data_path_rotation, index=i, action_group=bone_name) for i in range(rotation_enum)]

    keyframe_count = len(keyframe_data)
    keyframe_frame, keyframe_location, keyframe_rotation, is_rotation_negated = zip(*keyframe_data)

    # For whatever reason, quaternion.negate() remain unaffected when converted into euler through Quaternion.to_euler()
    # Because of it, I just had to manually negate them myself
    # And no, Euler does not have function to negate, unlike Quaternion
    if rotation_mode == 'EULER':
        new_rotation = []
        for item_index, rotation in enumerate(keyframe_rotation):
            rotation = rotation.to_euler()
            if not is_rotation_negated[item_index]:
                new_rotation.append(rotation)
                continue

            rotation = negate_euler(rotation, map_to_zero)
            new_rotation.append(rotation)

        keyframe_rotation = new_rotation

    for index, fcurve in enumerate(bone_fcurves_location):
        fcurve_keyframe_count = len(fcurve.keyframe_points)
        fcurve_index_start = fcurve_keyframe_count
        fcurve_index_end = fcurve_keyframe_count + keyframe_count

        fcurve.keyframe_points.add(keyframe_count)

        coords = np.zeros(fcurve_index_end * 2, dtype=np.float64)
        fcurve.keyframe_points.foreach_get('co', coords)

        coords[fcurve_index_start * 2 : fcurve_index_end * 2 : 2] = keyframe_frame
        coords[fcurve_index_start * 2 + 1: fcurve_index_end * 2 + 1 : 2] = [location[index] for location in keyframe_location]
        fcurve.keyframe_points.foreach_set('co', coords)

        for keyframe in fcurve.keyframe_points[fcurve_index_start:fcurve_index_end]:
            keyframe.interpolation = interpolation

        fcurve.update()

    for index, fcurve in enumerate(bone_fcurves_rotation):
        fcurve_keyframe_count = len(fcurve.keyframe_points)
        fcurve_index_start = fcurve_keyframe_count
        fcurve_index_end = fcurve_keyframe_count + keyframe_count

        fcurve.keyframe_points.add(keyframe_count)

        coords = np.zeros(fcurve_index_end * 2, dtype=np.float64)
        fcurve.keyframe_points.foreach_get('co', coords)

        coords[fcurve_index_start * 2 : fcurve_index_end * 2 : 2] = keyframe_frame
        coords[fcurve_index_start * 2 + 1: fcurve_index_end * 2 + 1 : 2] = [rotation[index] for rotation in keyframe_rotation]
        fcurve.keyframe_points.foreach_set('co', coords)

        for keyframe in fcurve.keyframe_points[fcurve_index_start:fcurve_index_end]:
            keyframe.interpolation = interpolation

        fcurve.update()


def process_animate(context: bpy.types.Context, animate_position: bool, animate_rotation: bool):
    scene = context.scene
    stroke_props = scene.TrajectAnim_stroke_props
    stroke_mode = stroke_props.target

    main_prop = scene.TrajectAnim_main_props
    target_prop = scene.TrajectAnim_target
    orientation_position = main_prop.position_orientation
    orientation_rotation = main_prop.rotation_orientation
    target_frames = main_prop.duration if main_prop.timing == 'DURATION' else None
    frame_step = main_prop.frame_step
    movement_axis = scene.TrajectAnim_movement_axis
    rotation_axis = scene.TrajectAnim_rotation_axis
    track_axis = scene.TrajectAnim_track_axis.axis
    up_axis = scene.TrajectAnim_up_axis.axis
    only_rotate_up = main_prop.only_rotate_up

    rotation_offset_prop = scene.TrajectAnim_rotation_offset
    rotation_offset = Euler((rotation_offset_prop.x, rotation_offset_prop.y, rotation_offset_prop.z), 'XYZ')

    gpencil_props = scene.TrajectAnim_gpencil_props
    gpencil = gpencil_props.active_gpencil

    if not animate_rotation:
        rotate_along_path = main_prop.rotate_along_path
        animate_rotation = rotate_along_path
    reverse_path = main_prop.reverse_path
    relative_path = main_prop.relative_path
    initial_rotation = main_prop.initial_rotation
    interpolation = main_prop.interpolation
    delete_after = main_prop.delete_after_animate

    smooth_flips = main_prop.smooth_flips
    flip_threshold = main_prop.flip_threshold
    map_to_zero = main_prop.map_to_zero

    active_object = context.active_object

    if stroke_mode == 'AUTO':
        if active_object and active_object.type == 'GREASEPENCIL':
            stroke_mode = 'GPENCIL'
        elif active_object.type == 'CURVE':
            stroke_mode = 'CURVE'
        else:
            stroke_mode = 'ANNOTATION'
    
    if stroke_mode == 'ANNOTATION':
        try:
            active_layer, active_frame = annotation_func.get_active_annotation_frame(context=context)
            strokes = active_frame.strokes

            # I should've put these strokes point conversion into separate function, but due to
            # gpencil and curve already have their points converted, let's just maintain consistency.
            temp_strokes = []
            for stroke in strokes:
                temp_strokes.append([point.co for point in stroke.points])
            strokes = temp_strokes
        except AttributeError:
            return False
        
    elif stroke_mode == 'GPENCIL':
        if not gpencil:
            gpencil = context.grease_pencil

        if not gpencil:
            return False
        
        active_frame = gpencil_func.get_active_gpencil_frame(gpencil)
        strokes = gpencil_func.get_strokes(active_frame)

    else:
        if not active_object or not active_object.type == 'CURVE':
            return False
        
        strokes = [[vector.co for vector in active_object.data.splines.active.points]]

    convert_method = stroke_props.convert_method
    if convert_method == 'POINTS' or (convert_method == 'AUTO' and len(strokes) == 1):
        points = strokes[0]
    else:
        points = convert_intersection(strokes)

    if not target_frames:
        target_frames = len(points)          
    
    if main_prop.auto_axis:
        track_axis, up_axis = auto_determine_axis(points)
        main_prop.previous_axis = f'{track_axis} {up_axis}'
    
    if main_prop.auto_fix_rotation:
        if track_axis == 'X' and up_axis == 'Y':
            rotation_offset = Euler((radians(-90), 0.0, radians(0)), 'XYZ')
        elif track_axis == '-X' and up_axis == 'Y':
            rotation_offset = Euler((radians(-90), 0.0, radians(0)), 'XYZ')
        elif track_axis == 'Z' and up_axis == 'Y':
            rotation_offset = Euler((radians(-180), 0.0, 0.0), 'XYZ')
        elif track_axis == '-Z' and up_axis == 'Y':
            rotation_offset = Euler((radians(-180), 0.0, 0.0), 'XYZ')

        elif track_axis == 'Y' and up_axis == 'X':
            rotation_offset = Euler((0.0, radians(-90), 0.0), 'XYZ')
        elif track_axis == 'Z' and up_axis == 'X':
            rotation_offset = Euler((0.0, radians(-180), radians(-90)), 'XYZ')
        elif track_axis == '-Y' and up_axis == 'X':
            rotation_offset = Euler((0.0, radians(-90), 0.0), 'XYZ')
        elif track_axis == '-Z' and up_axis == 'X':
            rotation_offset = Euler((0.0, radians(-180), radians(90)), 'XYZ')

        elif track_axis == 'Y' and up_axis == 'Z':
            rotation_offset = Euler((0.0, 0.0, radians(90)), 'XYZ')
        elif track_axis == '-X' and up_axis == 'Z':
            rotation_offset = Euler((radians(-180), 0.0, 0.0), 'XYZ')
        elif track_axis == '-Y' and up_axis == 'Z':
            rotation_offset = Euler((0.0, 0.0, radians(-90)), 'XYZ')
        elif track_axis == 'X' and up_axis == 'Z':
            rotation_offset = Euler((radians(-180), 0.0, 0.0), 'XYZ')
    
    rotation_offset = rotation_offset.to_quaternion()

    if main_prop.target_behaviour == 'SELECTED':
        if context.mode == 'POSE':
            objects = [(active_object, bone) for bone in context.selected_pose_bones]
        else:
            objects = [(obj, None) for obj in context.selected_objects if not obj.type in ('ARMATURE', 'GREASEPENCIL', 'CURVE')]
    else:
        objects = [(object, None) for object in target_prop.objects]
     
    if main_prop.rotation_center == 'OBJECT':
        if main_prop.target_behaviour == 'SELECTED':
            first_object, first_bone = objects[0]
            if first_bone is not None:
                center_rotation = first_object.location + first_bone.location
            else:
                center_rotation = first_object.location
        else:
            first_item = objects[0][0]
            first_object = first_item.object
            first_bone_name = first_item.bone_name
            if first_bone_name:
                for bone in first_object.pose.bones:
                    bone_name = bone.name
                    if bone_name == first_bone_name:
                        first_bone = bone
                        break

                center_rotation = first_object.location + first_bone.loccation
            else:
                center_rotation = first_object.location
    else:
        center_rotation = scene.cursor.location

    rotation_type = 'PATH' if animate_position is True else 'ROTATION'
    keyframe_data = keyframe_pairing(points, target_frames, frame_step, animate_rotation, center_rotation, only_rotate_up, rotation_axis, rotation_type, reverse_path, track_axis, up_axis, rotation_offset)
    
    previous_target = None
    previous_keyframe_data = None
    for object, bone in objects:
        is_armature = bool(bone)
        if main_prop.target_behaviour == 'LIST':
            bone_name = object.bone_name
            is_armature = bool(bone_name)
            object = object.object
            object_name = object.name
        else:
            bone_name = bone.name if is_armature else ''
            object_name = object.name

        action = get_action(object, object_name)

        data_path_mode = 'ARMATURE' if is_armature else 'OBJECT'
        rotation_mode = 'QUATERNION' if object.rotation_mode == 'QUATERNION' else 'EULER'
        if object.rotation_mode == 'AXIS_ANGLE':
            raise RuntimeError('Unsupported rotation mode. Please use either Quaternion or Euler (XYZ)')
        
        target_object = bone if bone else object
        
        if previous_target == target_object:
            transformed_keyframe_data = previous_keyframe_data
        else:
            transformed_keyframe_data = process_keyframe(context, keyframe_data, target_object, relative_path, initial_rotation, orientation_position, orientation_rotation, movement_axis, rotation_type, smooth_flips, flip_threshold)

        apply_animation(transformed_keyframe_data, action, data_path_mode, animate_position, animate_rotation, rotation_mode, interpolation, bone_name, map_to_zero)

        previous_target = target_object
        previous_keyframe_data = transformed_keyframe_data

    if delete_after:
        if stroke_mode == 'ANNOTATION':
            active_layer.frames.remove(active_frame)
        elif stroke_mode == 'GPENCIL':
            active_layer = gpencil.layers.active
            active_layer.frames.remove(active_frame)
        else:
            bpy.data.remove(active_object)

    return True


from bpy.types import Operator


class AnimatePosition(Operator):
    """Animate all targerted object(s) or bones based on active trajectory stroke"""
    bl_idname = "trajectanim.animate_position"
    bl_label = "Animate Position"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        result = process_animate(context, animate_position=True, animate_rotation=False)

        if result:
            self.report({'INFO'}, 'Successfully animate trajectory')
        else:
            self.report({'INFO'}, 'Fail to animate. Stroke not found')
        
        return {'FINISHED'}

class AnimateRotation(Operator):
    """Animate all targerted object(s) or bones based on active trajectory stroke"""
    bl_idname = "trajectanim.animate_rotation"
    bl_label = "Animate Rotation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        result = process_animate(context, animate_position=False, animate_rotation=True)

        if result:
            self.report({'INFO'}, 'Successfully animate trajectory')
        else:
            self.report({'INFO'}, 'Fail to animate. Stroke not found')
        
        return {'FINISHED'}