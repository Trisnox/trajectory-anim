import bpy


def add_object(context: bpy.types.Context):
    scene = context.scene
    target_prop = scene.TrajectAnim_target

    if context.mode == 'POSE':
        active_object = context.active_object
        for bone in context.selected_pose_bones:
            target = target_prop.objects.add()
            target.object = active_object
            target.name = bone.name
            target.icon = 'BONE_DATA'
            target.bone_name = bone.name
    else:
        for object in context.selected_objects:
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
