---
title: Timing Chart
---

!!! info "Info"
    Only applies to annotation and grease pencil

This script support similar concept to [Timing Chart](https://www.youtube.com/watch?v=uZQ4GCdiCuM). You can draw intersection line to represent timing. Each intersection will make that point as the target position, starting and ending is inserted by default, so there is no need to intersect both start and end.

With this, you can fine tune the timing accordingly.

![type:video](../videos/position.mp4)

It's a good practice to always draw intersection on spots where sharp turn (eg: before/after turning, middle of the rotation, etc) is encountered. This is to ensure that object doesn't skip over certain path.

![proper intersection](../images/trajectory_path_intersection.jpg)

!!! warning "Warning"
    Especially when using annotation on 3D cursor, do not shift your view. Calculating intersection on 3D space is somewhat sensitive, even a slight offset will cause that intersection to fail. Intersection lines should be parralel with the main stroke
