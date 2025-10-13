---
title: Animate Rotation
---

!!! info "Info"
    Stroke mentioned in this page depends on the stroke detection on [`Source Stroke`](../stroke_panel/index.md#source-stroke)

!!! warning "Rotation Types"
    It is recommended to use Quaternion or Euler rotation type. Any other rotation type than Quaternion or Euler will throw error.

## Animate Rotation
Animate object/bone rotation based off given stroke path. You can also [draw interection line to fine tune your timing](../other/timing_chart.md).

![type:video](../videos/animate_rotation.mp4)

## Settings
### Rotation Orientation
When set to global, target rotation will rotate across global axis, while local will just copy local rotation into the object.

### Rotation Center
Since rotation needs to be calculated from world origin, this setting can help to offset the stroke depending on which setting it uses.

`3D Cursor` will calculate the rotation by using 3d cursor as the center.

`Object` will calculate the rotation by using origin from active object or first item in the [target list](target_enum.md) if using list.


!!! info "Info"
    [`Rotation Offset`](animate_position.md#rotation-offset) is not used for this one as they are only used for tracking.