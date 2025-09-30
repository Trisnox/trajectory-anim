import bpy


class TRAJECTANIM_PANEL:
    bl_category = 'TrajectAnim'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'


class TRAJECTANIM_MAIN_PANEL(TRAJECTANIM_PANEL, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_trajectanim_main_panel'
    bl_label = 'Main'
    bl_order = 0

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.operator('trajectanim.animate_position', text='Animate Position', icon='TRACKING')
        col.operator('trajectanim.animate_rotation', text='Animate Rotation', icon='DRIVER_ROTATIONAL_DIFFERENCE')


class TARGET_UL_entries(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        if item:
            row = layout.row(align=True)
            row.prop(item, "name", text="", icon=item.icon, emboss=False, expand=True)


class TRAJECTANIM_TARGET_PANEL(TRAJECTANIM_PANEL, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_trajectanim_target_panel'
    bl_parent_id = 'OBJECT_PT_trajectanim_main_panel'
    bl_label = 'Target'
    bl_order = 1

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        scene = context.scene
        main_prop = scene.TrajectAnim_main_props
        target_prop = scene.TrajectAnim_target

        col = layout.column()
        col.prop(main_prop, 'target_behaviour', text='Target')

        if main_prop.target_behaviour == 'SELECTED':
            box = layout.box()
            if context.mode == 'POSE':
                items = context.selected_pose_bones
            else:
                items = [obj for obj in context.selected_objects if not obj.type in ('ARMATURE', 'GREASEPENCIL', 'CURVE')]

            for object in items:
                if context.mode == 'POSE':
                    icon = 'BONE_DATA'
                else:
                    icon = f'OUTLINER_OB_{object.type}'
                box.label(text=object.name, icon=icon)
        else:
            col = layout.column()
            col.template_list("TARGET_UL_entries", "", target_prop, "objects", target_prop, "active_index")

            row = col.row(align=True)
            row.operator('trajectanim.target_add', text='Add', icon='ADD')
            row.operator('trajectanim.target_remove', text='Remove', icon='REMOVE')
            row.operator('trajectanim.target_replace', text='Substitute', icon='GESTURE_ROTATE')


class TRAJECTANIM_SETTINGS_PANEL(TRAJECTANIM_PANEL, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_trajectanim_settings_panel'
    bl_parent_id = 'OBJECT_PT_trajectanim_main_panel'
    bl_label = 'Settings'
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'RIGHT'
        scene = context.scene
        main_prop = scene.TrajectAnim_main_props
        stroke_prop = scene.TrajectAnim_stroke_props

        # If blender API could make the enum box width smaller, I wouldn't have done this
        # The goal is to make text aligned to the right, and make the box smaller so that the text will fit without truncation
        row = layout.split(factor=0.6)
        row.alignment = 'RIGHT'
        row.label(text='Position Orientation')
        row = row.row()
        row.prop(main_prop, 'position_orientation', text='')

        row = layout.split(factor=0.6)
        row.alignment = 'RIGHT'
        row.label(text='Rotation Orientation')
        row = row.row()
        row.prop(main_prop, 'rotation_orientation', text='')

        row = layout.split(factor=0.6)
        row.alignment = 'RIGHT'
        row.label(text='Rotation Center')
        row = row.row()
        row.prop(main_prop, 'rotation_center', text='')

        col = layout.column()
        col.separator(factor=1, type='LINE')

        row = layout.split(factor=0.6)
        row.alignment = 'RIGHT'
        row.label(text='Conversion Method')
        row = row.row()
        row.prop(stroke_prop, 'convert_method', text='')

        row = layout.split(factor=0.6)
        row.alignment = 'RIGHT'
        row.label(text='Timing')
        row = row.row()
        row.prop(main_prop, 'timing', text='')

        if main_prop.timing == 'DURATION':
            row = layout.split(factor=0.6)
            row.alignment = 'RIGHT'
            row.label(text='Total Duration')
            row = row.row()
            row.prop(main_prop, 'duration', text='')

        row = layout.split(factor=0.6)
        row.alignment = 'RIGHT'
        row.label(text='Frame Step')
        row = row.row()
        row.prop(main_prop, 'frame_step', text='')

        col = layout.column()
        col.separator(factor=1, type='LINE')

        row = layout.split(factor=0.6)
        row.alignment = 'RIGHT'
        row.label(text='Interpolation')
        row = row.row()
        row.prop(main_prop, 'interpolation', text='')

        col = layout.column()
        col.separator(factor=1, type='LINE')

        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(main_prop, 'relative_path', text='Relative to Stroke')
        col.prop(main_prop, 'initial_rotation', text='Initial Rotation')
        col.prop(main_prop, 'rotate_along_path', text='Rotate Along Path')
        col = col.column()
        col.prop(main_prop, 'reverse_path', text='Reverse Path')
        col.prop(main_prop, 'delete_after_animate', text='Delete After')


class TRAJECTANIM_TRACK_SETTINGS_PANEL(TRAJECTANIM_PANEL, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_trajectanim_track_settings_panel'
    bl_parent_id = 'OBJECT_PT_trajectanim_settings_panel'
    bl_label = 'Track Settings'
    bl_order = 0
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        main_prop = scene.TrajectAnim_main_props
        movement_axis_prop = scene.TrajectAnim_movement_axis
        rotation_axis_prop = scene.TrajectAnim_rotation_axis
        track_axis_prop = scene.TrajectAnim_track_axis
        up_axis_prop = scene.TrajectAnim_up_axis

        layout.enabled = main_prop.rotate_along_path

        col = layout.column()
        col.label(text='Movement Axis:')

        grid = layout.grid_flow(columns=3, align=True)
        grid.prop(movement_axis_prop, 'x', text='X', toggle=1)
        grid.prop(movement_axis_prop, 'y', text='Y', toggle=1)
        grid.prop(movement_axis_prop, 'z', text='Z', toggle=1)

        col = layout.column()
        col.separator(factor=1, type='LINE')

        col = layout.column()
        col.label(text='Rotation Axis:')

        grid = layout.grid_flow(columns=3, align=True)
        grid.prop(rotation_axis_prop, 'x', text='X', toggle=1)
        grid.prop(rotation_axis_prop, 'y', text='Y', toggle=1)
        grid.prop(rotation_axis_prop, 'z', text='Z', toggle=1)

        col = layout.column()
        col.separator(factor=1, type='LINE')

        col = layout.column()
        col.prop(main_prop, 'only_rotate_up', text='Only Rotate Up')
        col.prop(main_prop, 'auto_axis', text='Determine Axis Automatically')

        col = layout.column()
        col.enabled = not main_prop.auto_axis
        col.label(text='Track/Forward Axis:')
        col.row().prop(track_axis_prop, 'axis', expand=True)

        col = layout.column()
        col.enabled = not main_prop.auto_axis
        col.label(text='Up Axis:')
        col.row().prop(up_axis_prop, 'axis', expand=True)

        col = layout.column()
        col.label(text=f'Previous Automatic Axis: {main_prop.previous_axis}')

class TRAJECTANIM_ROTATION_OFFSET_PANEL(TRAJECTANIM_PANEL, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_trajectanim_rotation_offset_panel'
    bl_parent_id = 'OBJECT_PT_trajectanim_settings_panel'
    bl_label = 'Rotation Offset'
    bl_order = 1
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        main_prop = scene.TrajectAnim_main_props
        rotation_offset = scene.TrajectAnim_rotation_offset

        layout.enabled = main_prop.rotate_along_path
        
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(main_prop, 'auto_fix_rotation', text='Auto Fix Rotation')

        col = layout.column()
        col.enabled = not main_prop.auto_fix_rotation

        row = col.split(factor=0.5)
        row.alignment = 'RIGHT'
        row.label(text='Offset Rotation X')
        row = row.row()
        row.prop(rotation_offset, 'x', text='')
        
        row = col.split(factor=0.5)
        row.alignment = 'RIGHT'
        row.label(text='Y')
        row = row.row()
        row.prop(rotation_offset, 'y', text='')

        row = col.split(factor=0.5)
        row.alignment = 'RIGHT'
        row.label(text='Z')
        row = row.row()
        row.prop(rotation_offset, 'z', text='')


class TRAJECTANIM_ROTATION_FLIP_PANEL(TRAJECTANIM_PANEL, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_trajectanim_rotation_flip_panel'
    bl_parent_id = 'OBJECT_PT_trajectanim_settings_panel'
    bl_label = 'Flip Detection'
    bl_order = 2
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        main_prop = scene.TrajectAnim_main_props
        
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(main_prop, 'smooth_flips', text='Smooth flips')

        col = col.column()
        col.enabled = main_prop.smooth_flips
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(main_prop, 'map_to_zero', text='Map to Zero')

        col = col.column()
        row = col.split(factor=0.5)
        row.alignment = 'RIGHT'
        row.label(text='Flip Threshold')
        row = row.row()
        row.prop(main_prop, 'flip_threshold', text='')
