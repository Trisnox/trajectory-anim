import bpy


class GREASE_PENCIL_PANEL(bpy.types.Panel):
    bl_category = 'TrajectAnim'
    bl_idname = 'OBJECT_PT_trajectanim_gpencil_panel'
    bl_label = 'Grease Pencil'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        gpencil_prop = scene.TrajectAnim_gpencil_props
        gpencil = gpencil_prop.active_gpencil
        active_gpencil = context.grease_pencil
        
        if not gpencil:
            col = layout.column()
            col.label(text='No active grease pencil.')
            col.label(text='Create new one using the')
            col.label(text='button below, or use an existing one.')

            col = layout.column()
            col.operator('trajectanim.gpencil_init', text='Create Grease Pencil', icon='GREASEPENCIL')
            col.prop(gpencil_prop, 'active_gpencil')

            return
        

        col = layout.column()
        col.prop(gpencil_prop, 'active_gpencil')

        col = layout.column()
        col.separator(factor=2, type='LINE')

        # Slight problem here, appearantly grease pencil layers does not have active index
        # layers.active simply return the active layer object
        # https://docs.blender.org/api/current/bpy.types.GreasePencilv3Layers.html#bpy.types.GreasePencilv3Layers
        # https://docs.blender.org/api/current/bpy.types.GreasePencilLayer.html#bpy.types.GreasePencilLayer
        if not gpencil == active_gpencil:
            col = layout.column()
            col.label(text='Select the active grease pencil')
            col.label(text='object to display layers here')
            return
        
        col = layout.column()
        col.template_grease_pencil_layer_tree()
        # col.template_list("GREASE_PENCIL_UL_attributes", "", gpencil, 'layers', gpencil.layers, 'there is no active index here???')
        row = col.row(align=True)
        row.operator('grease_pencil.layer_add', text='Add Layer', icon='ADD')
        row.operator('grease_pencil.layer_remove', text='Delete Layer', icon='REMOVE')
