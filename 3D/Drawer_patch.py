# pyright: reportMissingImports=false

from solid2 import cube, cylinder, rotate, translate, union
import os

"""Drawer width extension patch (single-side).

Goal
----
This part is meant to be glued/attached on ONE side of an already printed drawer
whose width is ~20mm too small for the legs/grooves of Base_Distributeur_combined.

Geometry conventions (same as Drawer.py)
---------------------------------------
- X: drawer width
- Y: drawer sliding direction (drawer goes from back Y=-DRAWER_LENGTH to front Y=0)
- Z: height

Specific requirements implemented
--------------------------------
- Patch base plate: PATCH_WIDTH wide.
- Same hole diameter/spacing as Drawer.py on the patch base.
- Back plate at the rear (Y=-DRAWER_LENGTH):
  - Left side (inner/joint side) overhangs the base to compensate the gap where the
    main drawer back plate is shorter than the base.
  - Right side (outer side) remains shorter than the base (same idea as the main drawer).
"""

# --- Must match the drawer/base ecosystem ---
PATCH_WIDTH = 20.0  # width to add on ONE side
DRAWER_LENGTH = 90.0
DRAWER_THICKNESS = 3.6

# Groove (from Base_Distributeur_combined.py)
GROOVE_DEPTH = 2.5

# Back plate (same style as Drawer.py)
BACK_HEIGHT = 20.0
BACK_THICK = 5.0

# Extra front layer (requested): placed in front of the back plate along +Y
FRONT_LAYER_THICK = 3.0

# Extra top layer near the front-most holes (requested)
TOP_LAYER_THICK_Z = 3.0
TOP_LAYER_LEN_Y = 10.0

# Extra holes through the top layer where it overlaps the main drawer holes.
# 2 holes = the two rightmost columns of the drawer hole grid.
TOP_INTERSECT_HOLES = 2

# Hole pattern (same style as Drawer.py)
HOLE_DIAM = 4.0
HOLE_SPACING = 10.0
HOLE_MARGIN_X = 10.0
HOLE_MARGIN_Y_FRONT = 10.0

# User tweak: shift these two holes in X (mm)
TOP_INTERSECT_SHIFT_X = -4.5

# Overhang/inset of the back plate (X direction)
BACKPLATE_OVERHANG_LEFT = GROOVE_DEPTH
BACKPLATE_INSET_RIGHT = GROOVE_DEPTH


# --- Main drawer geometry (already printed) ---
# Used only to compute the X position of the cable-hole center mentioned by the user.
# These values mirror Drawer.py defaults.
MAIN_TOTAL_WIDTH = 260.0
MAIN_LEG_THICK = 15.0
MAIN_GROOVE_DEPTH = 2.5
MAIN_CLEARANCE_W = 0.5

MAIN_INNER_WIDTH = MAIN_TOTAL_WIDTH - (2 * MAIN_LEG_THICK)
MAIN_DRAWER_WIDTH = MAIN_INNER_WIDTH + (2 * MAIN_GROOVE_DEPTH) - MAIN_CLEARANCE_W
MAIN_RIGHT_EDGE_X = MAIN_DRAWER_WIDTH / 2.0

# Cable square holes on the main drawer back plate (Drawer.py)
MAIN_NUM_CABLE_HOLES = 6
MAIN_CABLE_HOLE_W = 20.0
# Z range: 8.6mm to 15.0mm (Drawer.py)
MAIN_CABLE_HOLE_H = 15.0 - 8.6  # 6.4mm
MAIN_CABLE_HOLE_Z = 8.6
MAIN_CABLE_HOLE_SPACING = 15.0

# "右侧第一个方孔" interpreted as the rightmost hole.
TARGET_HOLE_FROM_RIGHT = 0

# Extra small cube to key into the target square hole (requested)
TAB_WIDTH = 10.0

# Side holes on the ends of the back plate (mirrors Drawer.py "Side Locking Holes")
SIDE_HOLE_DIAM = 1.8
# Make this long enough so the right-side hole reaches into the tab area.
# (Large values are fine; it only subtracts air.)
SIDE_HOLE_LEN = 80.0
SIDE_HOLE_Z = 10.0


def create_patch():
    # Base plate (X from 0..PATCH_WIDTH)
    base = cube([PATCH_WIDTH, DRAWER_LENGTH, DRAWER_THICKNESS])
    base = translate([0, -DRAWER_LENGTH, 0])(base)

    # Back plate:
    # - located at the very back (same as Drawer.py)
    # - shifted to overhang on the LEFT side and be inset on the RIGHT side
    back_w = PATCH_WIDTH - BACKPLATE_INSET_RIGHT + BACKPLATE_OVERHANG_LEFT
    back_x0 = -BACKPLATE_OVERHANG_LEFT
    back_plate = cube([back_w, BACK_THICK, BACK_HEIGHT - DRAWER_THICKNESS])
    back_plate = translate([back_x0, -DRAWER_LENGTH, DRAWER_THICKNESS])(back_plate)

    patch = base + back_plate

    # Side holes on the back plate ends (贯穿孔): drill along X at both ends.
    # IMPORTANT: do NOT subtract them yet; we subtract later so they also cut the `tab`.
    side_hole_y = -DRAWER_LENGTH + (BACK_THICK / 2.0)
    side_hole = cylinder(d=SIDE_HOLE_DIAM, h=SIDE_HOLE_LEN)
    side_hole = rotate([0, 90, 0])(side_hole)

    back_left_x = back_x0
    back_right_x = back_x0 + back_w

    # Drill from left end towards +X
    sh_left = translate([back_left_x - 10.0, side_hole_y, SIDE_HOLE_Z])(side_hole)
    # Drill from right end towards -X
    sh_right = translate([back_right_x + 10.0, side_hole_y, SIDE_HOLE_Z])(
        rotate([0, 180, 0])(side_hole)
    )

    # Extra layer in front of the back plate:
    # - same height as the back plate
    # - thickness = FRONT_LAYER_THICK
    # - right edge matches the original back plate right edge
    # - left edge extends into the main drawer until the center of the target cable hole
    total_holes_width = (MAIN_NUM_CABLE_HOLES * MAIN_CABLE_HOLE_W) + ((MAIN_NUM_CABLE_HOLES - 1) * MAIN_CABLE_HOLE_SPACING)
    start_x_cable = -total_holes_width / 2.0 + (MAIN_CABLE_HOLE_W / 2.0)
    target_k = (MAIN_NUM_CABLE_HOLES - 1) - TARGET_HOLE_FROM_RIGHT
    target_hole_center_x = start_x_cable + (target_k * (MAIN_CABLE_HOLE_W + MAIN_CABLE_HOLE_SPACING))

    # Patch X=0 is assumed to be glued on the main drawer right edge.
    # Convert main-drawer coordinate to patch coordinate.
    hole_center_patch_x = target_hole_center_x - MAIN_RIGHT_EDGE_X
    front_x0 = hole_center_patch_x
    front_x1 = PATCH_WIDTH - BACKPLATE_INSET_RIGHT
    front_w = front_x1 - front_x0

    front_layer = cube([front_w, FRONT_LAYER_THICK, BACK_HEIGHT - DRAWER_THICKNESS])
    front_layer = translate([front_x0, -DRAWER_LENGTH + BACK_THICK, DRAWER_THICKNESS])(front_layer)
    patch += front_layer

    # Extra layer on top of the base near the front-most hole row (farthest from back plate):
    # - Z thickness = TOP_LAYER_THICK_Z
    # - Y length = TOP_LAYER_LEN_Y
    # - X: right edge matches the base (PATCH_WIDTH), left edge matches front_layer (front_x0)
    top_x0 = front_x0
    top_x1 = PATCH_WIDTH
    top_w = top_x1 - top_x0
    if top_w > 0:
      top_y1 = -HOLE_MARGIN_Y_FRONT
      top_y0 = top_y1 - TOP_LAYER_LEN_Y
      top_layer = cube([top_w, TOP_LAYER_LEN_Y, TOP_LAYER_THICK_Z])
      top_layer = translate([top_x0, top_y0, DRAWER_THICKNESS])(top_layer)
      patch += top_layer

    # Keying tab: sits where the front layer overlaps the target square hole.
    # Dimensions: width=TAB_WIDTH, thickness=hole thickness (~back plate thickness), height=hole height.
    # Placement: centered on the target hole center in X, spans the back-plate thickness in Y,
    # starts at the same Z as the square hole in Drawer.py.
    tab = cube([TAB_WIDTH, BACK_THICK, MAIN_CABLE_HOLE_H])
    tab = translate([
      hole_center_patch_x - (TAB_WIDTH / 2.0) + 4.9,
      -DRAWER_LENGTH,
      MAIN_CABLE_HOLE_Z,
    ])(tab)
    patch += tab

    # Now subtract the side holes so they also go through the tab (if they overlap).
    patch -= sh_left
    patch -= sh_right

    # Hole grid on base (same parameters as Drawer.py, adapted to the patch extents)
    start_x = HOLE_MARGIN_X
    end_x = PATCH_WIDTH - HOLE_MARGIN_X
    start_y = -DRAWER_LENGTH + HOLE_MARGIN_Y_FRONT + BACK_THICK  # avoid back plate
    end_y = -HOLE_MARGIN_Y_FRONT

    x_range = end_x - start_x
    y_range = end_y - start_y

    holes = []
    if x_range >= 0 and y_range >= 0:
      nx = int(x_range / HOLE_SPACING)
      ny = int(y_range / HOLE_SPACING)

      # Front-most hole row in Drawer.py logic (closest to the front, i.e. max Y)
      frontmost_hy = start_y + ny * HOLE_SPACING

      # If the top layer extends into negative X (over the main drawer),
      # open the two overlapped drawer holes (x=-10, -20 relative to drawer right edge).
      # This prevents the new top layer from blocking the drawer body's two holes.
      if top_x0 < 0:
        for i in range(TOP_INTERSECT_HOLES):
          hx = -(HOLE_MARGIN_X + i * HOLE_SPACING) + TOP_INTERSECT_SHIFT_X
          hy = frontmost_hy
          h = cylinder(d=HOLE_DIAM, h=DRAWER_THICKNESS + TOP_LAYER_THICK_Z + 2)
          h = translate([hx, hy, -1])(h)
          holes.append(h)

      for i in range(nx + 1):
          for j in range(ny + 1):
              hx = start_x + i * HOLE_SPACING
              hy = start_y + j * HOLE_SPACING

              # Cut through base + the extra top layer so holes stay open.
              h = cylinder(d=HOLE_DIAM, h=DRAWER_THICKNESS + TOP_LAYER_THICK_Z + 2)
              h = translate([hx, hy, -1])(h)
              holes.append(h)

    if holes:
        patch -= union()(*holes)

    return patch


if __name__ == "__main__":
    part = create_patch()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "Drawer_patch.scad")

    part.save_as_scad(file_path)
    print(f"Generated: {file_path}")
