---
title: Target List
---

## Target List
The box contain list of affected target object or bone.

By default it uses `Selected`, which will insert all selected object or bone into the list. Ignored if object type is either `CURVE`, `GREASEPENCIL` or `ARMATURE`. This is recommended if you're using annotation.

Using `List` allows you to manually select target object or bone. Unlike `Selected` which doesn't append both object and bone at the same time depending on the context mode, `List` is capable of having both object and bone regardless if you were no longer in pose mode or whether the object is no longer selected. This is recommended if you're using grease pencil or curve.

`List` have three operation:

- `Add`: add all selected object into the list
- `Remove`: remove selected entry from the list
- `Substitute`: remove all entry, and then do the same operation as `Add`