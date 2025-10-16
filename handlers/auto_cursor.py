import bpy


def auto_cursor_object_msgbus():
    context = bpy.context
    main_prop = context.scene.TrajectAnim_main_props
    auto_cursor = main_prop.auto_cursor
    target_behaviour = main_prop.target_behaviour

    # 'LIST' is already integrated in their own function (trajectanim_target.py)
    if not auto_cursor or not target_behaviour == 'SELECTED':
        return

    active_object = context.active_object
    if not active_object or active_object.type in ('ARMATURE', 'GREASEPENCIL', 'CURVE'):
        return
    
    context.scene.cursor.location = active_object.location


# Tracking selected pose bone through msgbus doesn't seemed to work


def register():
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.LayerObjects, 'active'),
        owner=bpy.types.LayerObjects,
        notify=auto_cursor_object_msgbus,
        args=(),
    )
    

def unregister():
    bpy.msgbus.clear_by_owner(bpy.types.LayerObjects)