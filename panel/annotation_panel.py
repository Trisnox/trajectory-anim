import bpy


class ANNOTATION_PANEL(bpy.types.Panel):
    bl_category = 'TrajectAnim'
    bl_idname = 'OBJECT_PT_trajectanim_annotation_panel'
    bl_label = 'Annotation'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        annotation_prop = scene.TrajectAnim_annotation_props
        
        if not bpy.data.grease_pencils:
            col = layout.column()
            col.label(text='No active annotation.')
            col.label(text='Start drawing using annotation tool!')
            return

        annotation_data = bpy.data.grease_pencils['Annotations']
        active_layer_index = annotation_data.layers.active_index
        active_layer = annotation_data.layers[active_layer_index]

        col = layout.column()
        col.template_list("GPENCIL_UL_annotation_layer", "", annotation_data, 'layers', annotation_data.layers, 'active_index')

        row = col.row(align=True)
        row.operator('gpencil.layer_annotation_add', text='Add Layer', icon='ADD')
        row.operator('gpencil.layer_annotation_remove', text='Delete Layer', icon='REMOVE')

        col = layout.column()
        col.prop(active_layer, 'thickness', text='Thickness')

        col = layout.column()
        col.operator('trajectanim.annotation_add_blank_keyframe', text='Insert Blank Keyframe', icon='KEYFRAME')
        col.prop(annotation_prop, 'all_layers', text='Only insert active Layer', invert_checkbox=True)
