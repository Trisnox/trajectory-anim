from mathutils import Vector
from mathutils.geometry import intersect_line_line as LineIntersect
from mathutils.geometry import intersect_point_line as PtLineIntersect

# Code taken from TinyCad, which is licensed under: GPL-2.0-or-later/GPL-3.0-or-later
# https://projects.blender.org/extensions/mesh_tiny_cad/src/branch/main/source/XALL.py
threshold = 1.0e-5

def __point_on_edge(p, edge):
    pt, _percent = PtLineIntersect(p, *edge)
    on_line = (pt - p).length < threshold
    return on_line and (0.0 <= _percent <= 1.0)


def __num_edges_point_lies_on(pt, edges):
    res = [__point_on_edge(pt, edge) for edge in [edges[:2], edges[2:]]]
    return len([i for i in res if i])


def __can_skip(closest_points, vert_vectors):
    if not closest_points:
        return True
    if not isinstance(closest_points[0].x, float):
        return True
    if __num_edges_point_lies_on(closest_points[0], vert_vectors) < 2:
        return True

    cpa, cpb = closest_points
    return (cpa - cpb).length > threshold


# Note: this is slow due to having to calculate between the source and all the target stroke.
# It would've been faster if we were to select only the edges we want to intersect, so that the script does not need to
# calculate unecessary intersections. Unfortunately, that's not the case with annotation, as there is no edit mode for annotation
def find_stroke_intersection(source_stroke: list, stroke_targets: list) -> list[Vector]:
    """
    Function to search intersection between the source stroke and all target strokes.

    Arguments
    ---------
    source_stroke: `list`
        List containing vector points [Vector, Vector, Vector, ...]
    stroke_targets: `list`
        List containing lists of vector points [[Vector, Vector, ...], [Vector, Vector, ...], ...]

    Return
    ------
    intersect_points_only: `list`
        List containing vector of starting, intersections, and ending
    
    intersect_points_all: `list`
        List containing vector of source target, including its intersection

    """
    intersect_points_only = []
    intersect_points_all = []
    start_point = source_stroke[0]
    end_point = source_stroke[-1]

    intersect_points_only.append(start_point)
    for source_index in range(len(source_stroke) - 1):
        v1, v2 = source_stroke[source_index], source_stroke[source_index+1]

        intersect_points_all.append(v1)
        for target_stroke in stroke_targets:
            target_stroke = target_stroke
            for target_index in range(len(target_stroke) - 1):
                v3, v4 = target_stroke[target_index], target_stroke[target_index+1]
                
                iv = LineIntersect(v1, v2, v3, v4)
                if __can_skip(iv, (v1, v2, v3, v4)):
                    continue

                intersection = (iv[0] + iv[1]) / 2
                intersect_points_only.append(intersection)
                intersect_points_all.append(intersection)
            intersect_points_all.append(v2)
    
    intersect_points_only.append(end_point)
    return intersect_points_only, intersect_points_all
