# pyright: reportMissingImports=false

"""Assemble Drawer + Drawer_patch into a single SCAD.

Why
----
OpenSCAD `include` is awkward when your .scad files emit geometry at top-level
(as SolidPython exports commonly do). Assembling in Python keeps transforms
predictable.

Usage
-----
python 3D/Drawer_assemble.py

Output
------
3D/Drawer_with_patch.scad

Notes
-----
- Drawer.py uses a centered X coordinate system (drawer spans [-W/2, +W/2]).
- Drawer_patch.py uses X in [0, PATCH_WIDTH] and assumes X=0 is glued to the
  main drawer right edge.
"""

from __future__ import annotations

import os

from solid2 import translate, union

import Drawer
import Drawer_patch


# Which side to attach the patch to.
# - "right": patch X=0 aligns to drawer right edge (+W/2)
# - "left":  patch X=PATCH_WIDTH aligns to drawer left edge (-W/2)
PATCH_SIDE = "right"  # "right" | "left"

# Optional extra offsets for fine alignment (mm)
EXTRA_OFFSET_X = 0.0
EXTRA_OFFSET_Y = 0.0
EXTRA_OFFSET_Z = 0.0


def assemble():
    drawer = Drawer.create_drawer()
    patch = Drawer_patch.create_patch()

    drawer_right_edge_x = Drawer.DRAWER_WIDTH / 2.0
    drawer_left_edge_x = -Drawer.DRAWER_WIDTH / 2.0

    if PATCH_SIDE == "right":
        patch_tx = drawer_right_edge_x
    elif PATCH_SIDE == "left":
        # Move patch so its right edge touches the drawer left edge
        patch_tx = drawer_left_edge_x - Drawer_patch.PATCH_WIDTH
    else:
        raise ValueError('PATCH_SIDE must be "right" or "left"')

    patch = translate([
        patch_tx + EXTRA_OFFSET_X,
        EXTRA_OFFSET_Y,
        EXTRA_OFFSET_Z,
    ])(patch)

    return union()(drawer, patch)


if __name__ == "__main__":
    part = assemble()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "Drawer_with_patch.scad")

    part.save_as_scad(file_path)
    print(f"Generated: {file_path}")
