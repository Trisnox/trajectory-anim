import bpy


def add_object(context: bpy.types.Context):
    scene = context.scene
    target_prop = scene.TrajectAnim_target
    main_prop = context.scene.TrajectAnim_main_props
    auto_cursor = main_prop.auto_cursor

    if auto_cursor and len(target_prop.objects) == 0:
        if context.mode == 'POSE':
            active_object = context.active_object
            active_bone = context.active_pose_bone
            bone_location, _, _ = active_bone.matrix.decompose()
            
            context.scene.cursor.location = active_object.location + bone_location
        else:
            context.scene.cursor.location = context.active_object.location

    if context.mode == 'POSE':
        active_object = context.active_object
        active_bone = context.active_pose_bone
        items = context.selected_pose_bones
        items.remove(active_bone)
        items.insert(0, active_bone)

        for bone in items:
            target = target_prop.objects.add()
            target.object = active_object
            target.name = bone.name
            target.icon = 'BONE_DATA'
            target.bone_name = bone.name
    else:
        active_object = context.active_object
        items = context.selected_objects
        items.remove(active_object)
        items.insert(0, active_object)

        for object in items:
            target = target_prop.objects.add()
            target.object = object
            target.icon = f'OUTLINER_OB_{object.type}'
            target.name = object.name
            
    return


def remove_object(context: bpy.types.Context):
    scene = context.scene
    target_prop = scene.TrajectAnim_target

    active_index = target_prop.active_index
    target_prop.objects.remove(active_index)

    return

def replace_object(context: bpy.types.Context):
    scene = context.scene
    target_prop = scene.TrajectAnim_target

    for index in reversed(range(len(target_prop.objects))):
        target_prop.objects.remove(index)
    
    add_object(context)

    return


from bpy.types import Operator


class TargetAddEntry(Operator):
    """Add entry to target list"""
    bl_idname = "trajectanim.target_add"
    bl_label = "Add entry to target list"

    def execute(self, context):
        result = add_object(context)

        return {'FINISHED'}
    

class TargetRemoveEntry(Operator):
    """Remove entry from target list"""
    bl_idname = "trajectanim.target_remove"
    bl_label = "Remove entry from target list"

    def execute(self, context):
        result = remove_object(context)

        return {'FINISHED'}


class TargetReplaceEntry(Operator):
    """Replace entry with newly selected object(s)"""
    bl_idname = "trajectanim.target_replace"
    bl_label = "Replace entry with newly selected object(s)"

    def execute(self, context):
        result = replace_object(context)

        return {'FINISHED'}
