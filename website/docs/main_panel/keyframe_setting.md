---
title: Keyframe Settings
---

## Keyframe Settings
### Conversion Method
By default it uses `Automatic`, which will use points if there is only single stroke, otherwise use intersection.

`Points` will use each individual point from stroke source. Only the first stroke will be recognized, everything else will be ignored.

`Intersection` will use the first stroke as the refernce, and then try to calculate intersection with other strokes. Only starting, intersection, and ending will be used. Please read [`Timing Chart`](../other/timing_chart.md) for more info.

### Timing
!!! info "Info"
    Points mentioned in this section is depends on [`Conversion Method`](#conversion-method) setting that you choose.

`Points` will use all points into keyframe.

`Duration` will try to fit all points into desired duration. Keyframes cannot have more than whatever the `Total Duration` is being set. If there are less keyframes than the total duration, then keyframe will be stretched, otherwise they will be shrinked.

### Frame Step
Keyframe will be skipped every this many frame.

By default it caps at 1, which will fill every frame. If set to 2, then keyframe will skip every 1 frame, 3 will skip every 2 frame, etc.

### Interpolation
Interpolation type used for each keyframe.

!!! abstract "Interpolation Types"
    Currently there is only three main interpolation, linear, bezier, and constant. Honestly I think this is enough for most purpose, but let me know if I should add more or all interpolation into the list.