---
title: Grease Pencil Panel
---

# Overview
![gpencil_panel](../images/gpencil_panel.png)

## Active Grease Pencil
This property is used to link grease pencil data so that script know which grease pencil to use and to display layers in this panel for convenience. Another use is for [converting curve into grease pencil](../stroke_panel/index.md#overview-curve), if this data exist, then curve will be directly converted into grease pencil keyframe.

This is optional, can be left blank, though the script prioritized active grease pencil data over selected ones.

!!! info "Layers"
    Unfortunately, grease pencil layers API lacks active index, so the layers cannot always be shown. Layers will only be shown if you select the grease pencil object correspond to the active ones.