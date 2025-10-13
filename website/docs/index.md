# Trajectory Anim

![type:video](videos/showcase.mp4)

Blender add-on to quickly animate by drawing trajectory line.

Similar to `Follow Path` constraints, you can animate an object by drawing a trajectory line, but much more convenient and faster than using the constraints. Aside from following and/or rotating along the path, you can also draw trajectory line to represent rotation. Not only that, but you can also draw intersection line in your trajectory line to represent [timing chart](https://www.youtube.com/watch?v=uZQ4GCdiCuM), which give better control over timing/easing.

Main repository [github.com/Trisnox/trajectory-anim/](https://github.com/Trisnox/trajectory-anim/)

<div class="grid cards" markdown>

-   :fontawesome-solid-download:{ .lg .middle } __Installation__

    ---

    Guide on how to install the add-on

    [:octicons-arrow-right-24: Installation](./install.md)

-   :material-book-open-variant:{ .lg .middle } __Tutorial/Guide__

    ---

    Quick Guide on how to use the add-on

    [:octicons-arrow-right-24: Add-on Tutorial](./tutorial.md)
    
</div>

___
Or if you're looking for an in-depth explanation about certain operator/button

<div class="grid cards" markdown>

-   :material-animation:{ .lg .middle } __Main Panel__

    ---

    **Main Panel**<br>
    Main panel to animate the position or rotation, alongside its settings

    [:octicons-arrow-right-24: Main Panel](./main_panel/index.md)

-   :material-draw:{ .lg .middle } __Stroke Panel__

    ---

    **Stroke Panel**<br>
    Panel to operate with stroke type selection, alongside its operator correspond to the stroke types

    [:octicons-arrow-right-24: Stroke Panel](./stroke_panel/index.md)

-   :material-note-edit-outline:{ .lg .middle } __Annotation Panel__

    ---

    **Annotation Panel**<br>
    Panel to show annotation layers for convenience

    [:octicons-arrow-right-24: Annotation Panel](./annotation_panel/index.md)

-   :material-grease-pencil:{ .lg .middle } __Grease Pencil Panel__

    ---

    **Grease Pencil Panel**<br>
    Panel to set Active Grease Pencil, and to show grease pencil layers for convenience

    [:octicons-arrow-right-24: Grease Pencil Panel](./grease_pencil_panel/index.md)
    
</div>

___
Or other topics

<div class="grid cards" markdown>

-   :material-timer-settings:{ .lg .middle } __Timing Chart__

    ---

    **Timing Chart**<br>
    Page explaining about timing chart integration with trajectory stroke

    [:octicons-arrow-right-24: Timing Chart](./other/timing_chart.md)

    
</div>

## Features
- Timing Chart: Similar to [Timing Chart](https://www.youtube.com/watch?v=uZQ4GCdiCuM), you can draw intersection line that will act as a timing. Starting and ending points is not required to be intersected
- Multi Target: You can apply position/rotation to as many objects/bones as you want
- Global/Local Orientation: You can choose whether you want to move or rotate the object through global axis, or local axis
- Relativity: You can choose whether you want snap along the path, or relative to its current position
- Rotate Along Path: Similar to using `Follow Curve`, this will cause object to rotate along the path
- Automatic Tracking: Track axis and up axis are determined automatically based off the given path, you can also manually input your own track axis and up axis
- Timings: You can set the duration to your liking, or even add step frame to skip every x frames
- Stroke Operators: Many operator to quickly tweak your strokes
- Layers: No need to draw everything using single layer, you can use layers and script will only animate from strokes belonging to the active layer
- Supports Many Types: From annotation, grease pencil, or even curve object

## Issues
If you encounter any issues or bug, please report them to the [issues page](https://github.com/Trisnox/trajectory-anim/issues)
