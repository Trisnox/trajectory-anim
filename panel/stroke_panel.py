import bpy


class STROKE_PANEL(bpy.types.Panel):
    bl_category = 'TrajectAnim'
    bl_idname = 'OBJECT_PT_trajectanim_stroke_panel'
    bl_label = 'Stroke'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        stroke_prop = scene.TrajectAnim_stroke_props
        mode = stroke_prop.target
        gpencil_props = scene.TrajectAnim_gpencil_props
        active_gpencil = gpencil_props.active_gpencil
        active_annotation = context.active_annotation_layer
        active_object = context.active_object

        col = layout.column()
        col.prop(stroke_prop, 'target', text='Source')

        col = layout.column()
        col.separator(factor=5, type='LINE')

        if mode == 'AUTO':
            if not active_object or active_object.type == 'GREASEPENCIL':
                mode = 'GPENCIL'
                mode_text = 'Grease Pencil'
                icon = 'GREASEPENCIL'
            elif active_object.type == 'CURVE':
                mode = 'CURVE'
                mode_text = 'Curve'
                icon = 'OUTLINER_OB_CURVE'
            else:
                mode = 'ANNOTATION'
                mode_text = 'Annotation'
                icon = 'GREASEPENCIL_LAYER_GROUP' # why is there no annotation icon

            col = layout.column()
            col.label(text='Detected Source: ' + mode_text, icon=icon)

        if mode == 'ANNOTATION':
            if not active_annotation:
                col = layout.column()
                col.label(text='No active annotation.')
                return

            col = layout.column()
            col.operator('gpencil.annotation_active_frame_delete', text='Delete Active Frame', icon='X')
            
            col = layout.column()
            col.separator(factor=2, type='LINE')

            col = layout.column()
            col.operator('trajectanim.annotation_to_curve', text='Convert to Curve', icon='CURVE_DATA')
            col.prop(stroke_prop, 'convert_method', text='Convert Method')
            col.prop(stroke_prop, 'keep_original', text='Keep Original')

        elif mode == 'GPENCIL':
            if not active_gpencil:
                col = layout.column()
                col.label(text='No active grease pencil.')
                return
            
            col = layout.column()
            col.operator('trajectanim.clear_excess_strokes', text='Clear excess strokes', icon='OUTLINER_OB_CURVES')
            col.operator('trajectanim.clear_all_strokes', text='Clear All Strokes', icon='GP_SELECT_STROKES')
            col.operator('grease_pencil.active_frame_delete', text='Delete Active Frame', icon='X').all = False

            col = layout.column()
            col.separator(factor=2, type='LINE')

            col = layout.column()
            col.operator('trajectanim.intersect_stroke', text='Self Intersect', icon='STROKE')
            col.prop(stroke_prop, 'self_intersect_method', text='Intersection Method', icon='SNAP_MIDPOINT')

            col = layout.column()
            col.operator('trajectanim.gpencil_to_curve', text='Convert to Curve', icon='CURVE_DATA')
            col.prop(stroke_prop, 'convert_method', text='Convert Method')
            col.prop(stroke_prop, 'keep_original', text='Keep Original')

        else:
            if not active_object or not active_object.type == 'CURVE':
                col = layout.column()
                col.label(text='No active curve object')
                return

            col.operator('trajectanim.curve_to_gpencil', text='Convert to Grease Pencil', icon='GREASEPENCIL')
            col.prop(stroke_prop, 'keep_original', text='Keep Original')

