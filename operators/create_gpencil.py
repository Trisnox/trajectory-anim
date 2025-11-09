import bpy


# 5.0 RNA types related to annotation are renamed, while grease pencil only have some renamed
# https://developer.blender.org/docs/release_notes/5.0/python_api/#annotations-grease-pencil
def is_using_5_0():
    return bpy.app.version >= (5, 0, 0)


def gpencil_init(context: bpy.types.Context):
    gpencil_name = 'trajectory_gpencil'
    if is_using_5_0():
        gpencil_data = bpy.data.grease_pencils.new(name=gpencil_name + '_data')
    else:
        gpencil_data = bpy.data.grease_pencils_v3.new(name=gpencil_name + '_data')
    gpencil_object = bpy.data.objects.new(gpencil_name, gpencil_data)
    context.collection.objects.link(gpencil_object)
    gpencil_object.show_in_front = True
    context.scene.TrajectAnim_gpencil_props.active_gpencil = gpencil_data

    active_layer = gpencil_data.layers.new(name='Layer', set_active=True)
    active_layer.frames.new(context.scene.frame_current)

    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except:
        pass

    bpy.ops.object.select_all(action='DESELECT')
    gpencil_object.select_set(True)
    context.view_layer.objects.active = gpencil_object

    bpy.ops.object.mode_set(mode='PAINT_GREASE_PENCIL')
    context.scene.tool_settings.gpencil_paint.color_mode = 'VERTEXCOLOR'

    return


from bpy.types import Operator


class GpencilInit(Operator):
    """Create Grease Pencil"""
    bl_idname = "trajectanim.gpencil_init"
    bl_label = "Crease Grease Pencil"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        result = gpencil_init(context)
        self.report({'INFO'}, 'Successfully created Grease Pencil')

        return {'FINISHED'}