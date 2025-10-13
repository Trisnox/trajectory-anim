---
title: Add-on Tutorial
---

!!! info "Info"
    The first drawn stroke/first curve spline will be used as the trajectory line, anything besides that will be ignored or used to calculate intersection. With that being said, you must draw trajectory as single continuous line. There is also stroke operator such as `Delete Active Frame` or `Delete All Strokes` to easily remove all strokes.

## Quick Tutorial
The fastest way to use this addon is to:

- Select an object(s) or bone(s)
- Select Annotation Tool
- If you want to draw on surface, make sure annotation placement is set to stroke, otherwise set to 3D cursor and make sure 3D cursor is snapped to the active object
- Draw trajectory line that represent path or rotation
- Press `Animate Position` / `Animate Position`

## Timing Chart
!!! info "Info"
    Only applies to annotation and grease pencil

Similar to the concept of [Timing Chart](https://www.youtube.com/watch?v=uZQ4GCdiCuM), you can draw intersection line to represent timing. Each intersection will make that point as the target position, starting and ending is inserted by default, so there is no need to intersect both start and end. This is optional, but this allow for better timing control.

It's a good practice to always draw intersection on spots where sharp turn (eg: before/after turning, middle of the rotation, etc) is encountered. This is to ensure that object doesn't skip over certain path.

![proper_intersection](../images/trajectory_path_intersection.jpg)

The order of interection does not matter. You can draw intersection line in any order, as long they intersect with the main stroke, the intersection will be recognized.

!!! warning "Warning"
    Especially when using annotation on 3D cursor, do not shift your view. Calculating intersection on 3D space is somewhat sensitive, even a slight offset will cause that intersection to fail. Intersection lines should be parralel with the main stroke

## Stroke and Target Object
Inside the main panel, there is list of target. By default is uses `Selected` behaviour, which will use all selected object as the target. You can change this to `List` which allow better control for object selection.

And at lowermost panel, there is stroke panel. `Animate Position`/`Animate Rotation` will use the source target defined by that property. By default, it uses `Automatic`, which will always default to annotation if the active object is not a grease pencil or curve.

---

For quick usage, use annotation. Annotation can be accessed everywhere, and is very quick and easy. Unfortunately, annotation strokes are read-only (on bpy API), and the operation are limited to drawing and erasing.

For ease of use, use grease pencil. They have full control over everything, editing stroke, keyframe editing, etc. Unfortunately using grease pencil might be quite the hassle since you need to switch modes every so often. Also, when using grease pencil, it is recommended to use `List` as the target object.

Curve is somewhat redundant since `Follow Path` object constraints is made to work with that, they also have much better result comparing with this add-on. Either way, the process is similar to grease pencil, you can edit or add points to tweak the path/rotation. Also, curve doesn't support intersection nor bezier points.

## Animate Position
After target object/bone is initialized, simply draw your stroke by using annotation or grease pencil (use the grease pencil panel to link grease pencil data).

After that, press `Animate Position` to animate the object/bone.

![type:video](../videos/animate_position.mp4)

In order to make object rotate along path, simply enable `Rotate Along Path` checkbox.

![type:video](../videos/animate_position_along_path.mp4)

You can also set position offset to offset the rotation.

## Animate Rotation
For rotation, the `Rotation Center` property will be used to calculate the rotation. By default it uses `3D Cursor`, however `Object` will use the first target from the list, it uses object's origin position or bone matrix position.

After target object/bone is initialized, simply draw your stroke by using annotation or grease pencil (use the grease pencil panel to link grease pencil data). The stroke will define the rotation, eg: semi circle will represent 180° rotation, a full circle will represent 360°, etc.

![type:video](../videos/animate_rotation.mp4)

Rotation is done by using global axis by default. You can set the orientation in the settings panel.