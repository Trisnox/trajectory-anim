---
title: Stroke Panel
---

# Overview
Stroke panel will have different operators depending on which type of stroke you choose.

## Source Stroke
Stroke that will be used for most operations. By default `Automatic` will always default to annotation if there are no grease pencil or curve amongst the selected objects, otherwise use grease pencil or curve.

---

`Automatic` will always try to use that respective source if any.

Annotation are easily accessible.

Setting [`Active Grease Pencil`](../grease_pencil_panel/index.md#active-grease-pencil) will surpress any other grease pencil.

Curve object has to be selected.

## Overview - Annotation
![Stroke Annotation](../images/stroke_panel_annotation.png)

- `Delete Active Frame`: Delete active frame
- `Convert to Curve`: Convert stroke into curve object. Can choose whether to keep annotation or remove them after, and/or to convert only the intersection or all points.

!!! info "Info"
    Annotation API are limited to read-only (no API to add/remove stroke), so there is not much we can do about them.

## Overview - Grease Pencil
![Stroke Gpencil](../images/stroke_panel_gpencil.png)

- `Clear Excess Strokes`: Remove all but the first stroke
- `Clear All Strokes`: Remove all strokes, but keep the keyframe
- `Delete Active Frame`: Delete active frame

- `Self Intersect`: Depending on setting, can be used to add points to intersection, or to only include starting, intersection, and ending of the stroke. Excess strokes will be removed afterward
- `Convert to Curve`: Convert stroke into curve object. Can choose whether to keep annotation or remove them after, and/or to convert only the intersection or all points.

## Overview - Curve
![Stroke Curve](../images/stroke_panel_curve.png)

- `Convert to Grease Pencil`: Convert points into grease pencil stroke. Add a new keyframe on current frame if [`Active Grease Pencil`](../grease_pencil_panel/index.md#active-grease-pencil) is set, otherwise call `bpy.ops.object.convert()` (equivalent to `Object > Convert > Grease Pencil`) operator and set [`Active Grease Pencil`](../grease_pencil_panel/index.md#active-grease-pencil) to this newly created grease pencil.