from solid2 import *
import os
import math

"""
Combined (no split) SCAD generator for the capsule dispenser.
Changes vs Base_Distributeur_decoupe.py:
- Outputs a single SCAD file (no top/bottom split).
- Shortens overall height by 50mm.
- Reduces material thickness: back=1.0mm, rail=2.5mm, front=1.5mm (total 5.0mm).
"""

# Dimensions and structure
TOTAL_WIDTH = 260.0
TOTAL_HEIGHT = 260.0  # 310 - 50mm
BACK_THICKNESS = 1.0
RAIL_THICKNESS = 2.5
FRONT_THICKNESS = 1.5
TOTAL_THICKNESS = BACK_THICKNESS + RAIL_THICKNESS + FRONT_THICKNESS

# Capsule geometry
CAPSULE_BODY_DIAM = 30.0
CAPSULE_RIM_DIAM = 37.0

# Tolerances / track geometry
SLOT_WIDTH = 32.0
TRACK_WIDTH = 39.0
ENTRY_HOLE_DIAM = 40.0
TOP_MARGIN = 60.0
BOTTOM_MARGIN = 10.0

NUM_COLUMNS = 5
COLUMN_WIDTH = TOTAL_WIDTH / NUM_COLUMNS

# Tilt/stand
TILT_ANGLE = 15.0
STAND_DEPTH = 80.0
STAND_THICKNESS = 10.0

def create_replica(part="all"):
    back_plate_block = cube([TOTAL_WIDTH, BACK_THICKNESS, TOTAL_HEIGHT])
    rail_block = cube([TOTAL_WIDTH, RAIL_THICKNESS, TOTAL_HEIGHT])

    tracks = []
    back_cutouts, rail_cutouts, front_cutouts = [], [], []

    for i in range(NUM_COLUMNS):
        cx = (i * COLUMN_WIDTH) + (COLUMN_WIDTH / 2)
        track_radius = TRACK_WIDTH / 2.0
        is_last_col = i == NUM_COLUMNS - 1
        if is_last_col:
            cyl_diam = 38.5
            rect_start_z = BOTTOM_MARGIN
            rect_height = (TOTAL_HEIGHT - TOP_MARGIN) - rect_start_z
        else:
            rect_start_z = BOTTOM_MARGIN + track_radius
            rect_height = (TOTAL_HEIGHT - TOP_MARGIN) - rect_start_z

        track_rect = cube([TRACK_WIDTH, RAIL_THICKNESS + 1, rect_height])
        track_rect = translate([cx - TRACK_WIDTH / 2, -0.5, rect_start_z])(track_rect)
        tracks.append(track_rect)

        if not is_last_col:
            track_circle = cylinder(d=TRACK_WIDTH, h=RAIL_THICKNESS + 1, _fn=64)
            track_circle = rotate([-90, 0, 0])(track_circle)
            track_circle = translate([cx, -0.5, rect_start_z])(track_circle)
            tracks.append(track_circle)

        entry_clearance = cylinder(d=ENTRY_HOLE_DIAM, h=RAIL_THICKNESS + 1, _fn=64)
        entry_clearance = rotate([-90, 0, 0])(entry_clearance)
        entry_clearance = translate([cx, -0.5, TOTAL_HEIGHT - TOP_MARGIN])(entry_clearance)
        tracks.append(entry_clearance)

        # Servo recess cutouts (same logic, but height now fits in TOTAL_HEIGHT=260)
        sg90_w = 12.5
        sg90_h_body = 23.0
        sg90_h_ears = 33.0

        hole_top_z = (TOTAL_HEIGHT - TOP_MARGIN) + (ENTRY_HOLE_DIAM / 2.0)
        margin = 6.0
        servo_bottom_z = hole_top_z + margin

        c_body = cube([sg90_w, TOTAL_THICKNESS + 2, sg90_h_body])
        c_body = translate([cx - sg90_w / 2, -1, servo_bottom_z])(c_body)
        rail_cutouts.append(c_body)
        front_cutouts.append(c_body)

        center_z = servo_bottom_z + sg90_h_body / 2
        c_ears = cube([sg90_w, BACK_THICKNESS + 2, sg90_h_ears])
        c_ears = translate([cx - sg90_w / 2, -1, center_z - sg90_h_ears / 2])(c_ears)
        back_cutouts.append(c_ears)

        if is_last_col:
            slot_cut = cube([10.0, BACK_THICKNESS + 2.0, 35.0])
            slot_cut = translate([cx - 10.0 / 2.0, -1.0, BOTTOM_MARGIN + 1.0])(slot_cut)
            back_cutouts.append(slot_cut)

            cyl_diam = 38.5
            cyl = cylinder(d=cyl_diam, h=FRONT_THICKNESS + 2.0, _fn=64)
            cyl = rotate([-90, 0, 0])(cyl)
            cyl = translate([cx, -0.5, BOTTOM_MARGIN + 19.25])(cyl)
            front_cutouts.append(cyl)

            small_hole = cylinder(d=3.0, h=BACK_THICKNESS + 2.0, _fn=32)
            small_hole = rotate([0, 90, 90])(small_hole)
            small_hole_1 = translate([cx-13, -1.0, BOTTOM_MARGIN + 70.0])(small_hole)
            small_hole_2 = translate([cx+13, -1.0, BOTTOM_MARGIN + 70.0])(small_hole)
            back_cutouts.append(small_hole_1)
            back_cutouts.append(small_hole_2)

        screw_dist = 28.0
        s_top = cylinder(d=2.0, h=TOTAL_THICKNESS + 2, _fn=32)
        s_top = rotate([-90, 0, 0])(s_top)
        s_top = translate([cx, -1, center_z + screw_dist / 2])(s_top)

        s_bot = cylinder(d=2.0, h=TOTAL_THICKNESS + 2, _fn=32)
        s_bot = rotate([-90, 0, 0])(s_bot)
        s_bot = translate([cx, -1, center_z - screw_dist / 2])(s_bot)

        rail_cutouts.extend([s_top, s_bot])
        front_cutouts.extend([s_top, s_bot])

    if tracks:
        rail_block -= union()(*tracks)
    if back_cutouts:
        back_plate_block -= union()(*back_cutouts)
    if rail_cutouts:
        rail_block -= union()(*rail_cutouts)

    # Backside small cube at 53mm above bottom margin (protrudes outward)
    cube_w = 10.0
    cube_h = 10.0
    cube_t = 4.0
    cx_last = (NUM_COLUMNS - 1) * COLUMN_WIDTH + (COLUMN_WIDTH / 2.0)
    cube_x = cx_last - cube_w / 2.0
    cube_y = -cube_t
    cube_z = BOTTOM_MARGIN + 53.0 - 5
    outer_cube = cube([cube_w, cube_t, cube_h])
    delta = 0.1
    inner_w = 10.0 + delta
    inner_t = cube_t + delta
    inner_h = 4.0 + delta
    inner = translate([(cube_w - inner_w) / 2.0, - delta / 2.0, (cube_h - inner_h) / 2.0])(cube([inner_w, inner_t, inner_h]))

    extra_w = 10.0 + delta
    extra_t = 2.0 + delta
    extra_h = 6.0 + delta
    extra = translate([(cube_w - extra_w) / 2.0, (cube_t - extra_t) / 2.0 + 1.0, (cube_h - extra_h) / 2.0])(cube([extra_w, extra_t, extra_h]))

    back_plate_block += translate([cube_x, cube_y, cube_z])(outer_cube - union()(inner, extra))

    rail_layer = translate([0, BACK_THICKNESS, 0])(rail_block)

    front_block = cube([TOTAL_WIDTH, FRONT_THICKNESS, TOTAL_HEIGHT])
    slots, entries = [], []

    for i in range(NUM_COLUMNS):
        cx = (i * COLUMN_WIDTH) + (COLUMN_WIDTH / 2)
        slot_radius = SLOT_WIDTH / 2.0
        is_last_col = i == NUM_COLUMNS - 1
        if is_last_col:
            rect_start_z = BOTTOM_MARGIN
            rect_height = (TOTAL_HEIGHT - TOP_MARGIN) - rect_start_z
        else:
            rect_start_z = BOTTOM_MARGIN + slot_radius
            rect_height = (TOTAL_HEIGHT - TOP_MARGIN) - rect_start_z

        slot_rect = cube([SLOT_WIDTH, FRONT_THICKNESS + 1, rect_height])
        slot_rect = translate([cx - SLOT_WIDTH / 2, -0.5, rect_start_z])(slot_rect)
        slots.append(slot_rect)

        if not is_last_col:
            slot_circle = cylinder(d=SLOT_WIDTH, h=FRONT_THICKNESS + 1, _fn=64)
            slot_circle = rotate([-90, 0, 0])(slot_circle)
            slot_circle = translate([cx, -0.5, rect_start_z])(slot_circle)
            slots.append(slot_circle)

        entry = cylinder(d=ENTRY_HOLE_DIAM, h=FRONT_THICKNESS + 2, _fn=64)
        entry = rotate([-90, 0, 0])(entry)
        entry = translate([cx, -1, TOTAL_HEIGHT - TOP_MARGIN])(entry)
        entries.append(entry)

    if slots:
        front_block -= union()(*slots)
    if entries:
        front_block -= union()(*entries)
    if front_cutouts:
        front_block -= union()(*front_cutouts)

    front_layer = translate([0, BACK_THICKNESS + RAIL_THICKNESS, 0])(front_block)

    filler_block = cube([TOTAL_WIDTH, TOTAL_THICKNESS, 50])
    filler_block = translate([0, 0, -50])(filler_block)

    if part == "front":
        return translate([-TOTAL_WIDTH / 2, 0, 0])(front_block)
    if part == "rail":
        return translate([-TOTAL_WIDTH / 2, 0, 0])(rail_block)
    if part == "back":
        return translate([-TOTAL_WIDTH / 2, 0, 0])(back_plate_block)

    assembly = back_plate_block + rail_layer + front_layer + filler_block

    CORNER_RADIUS = 15.0
    EPS = 1.0

    tl_block = cube([CORNER_RADIUS + EPS, TOTAL_THICKNESS + 20, CORNER_RADIUS + EPS])
    tl_block = translate([-EPS, -10, TOTAL_HEIGHT - CORNER_RADIUS])(tl_block)
    tl_cyl = cylinder(r=CORNER_RADIUS, h=TOTAL_THICKNESS + 20, _fn=64)
    tl_cyl = rotate([-90, 0, 0])(tl_cyl)
    tl_cyl = translate([CORNER_RADIUS, -10, TOTAL_HEIGHT - CORNER_RADIUS])(tl_cyl)
    tl_cutter = tl_block - tl_cyl

    tr_block = cube([CORNER_RADIUS + EPS, TOTAL_THICKNESS + 20, CORNER_RADIUS + EPS])
    tr_block = translate([TOTAL_WIDTH - CORNER_RADIUS, -10, TOTAL_HEIGHT - CORNER_RADIUS])(tr_block)
    tr_cyl = cylinder(r=CORNER_RADIUS, h=TOTAL_THICKNESS + 20, _fn=64)
    tr_cyl = rotate([-90, 0, 0])(tr_cyl)
    tr_cyl = translate([TOTAL_WIDTH - CORNER_RADIUS, -10, TOTAL_HEIGHT - CORNER_RADIUS])(tr_cyl)
    tr_cutter = tr_block - tr_cyl

    assembly = assembly - tl_cutter - tr_cutter
    assembly = translate([-TOTAL_WIDTH / 2, 0, 0])(assembly)
    return assembly


def create_integrated_legs():
    """Integrated stand, unchanged except for reliance on new TOTAL_HEIGHT."""
    LEG_THICK = 5.0
    STAND_DEPTH = 90.0

    leg_l = cube([LEG_THICK, STAND_DEPTH, TOTAL_HEIGHT * 0.6])
    leg_l = translate([TOTAL_WIDTH / 2 - LEG_THICK, -STAND_DEPTH, 0])(leg_l)

    leg_r = cube([LEG_THICK, STAND_DEPTH, TOTAL_HEIGHT * 0.6])
    leg_r = translate([-TOTAL_WIDTH / 2, -STAND_DEPTH, 0])(leg_r)

    sidecar_holes = []
    SIDECAR_HOLE_DIAM = 3.2
    col_y = -8.0
    col_zs = [15.6, 65.6, 115.6]
    for z in col_zs:
        sh = cylinder(d=SIDECAR_HOLE_DIAM, h=LEG_THICK + 20, _fn=32)
        sh = rotate([0, 90, 0])(sh)
        sh = translate([-TOTAL_WIDTH / 2 - 10, col_y, z])(sh)
        sidecar_holes.append(sh)

    extra_holes = [(-28.0, 21.0), (-48.0, 26.3)]
    for (y, z) in extra_holes:
        sh = cylinder(d=SIDECAR_HOLE_DIAM, h=LEG_THICK + 20, _fn=32)
        sh = rotate([0, 90, 0])(sh)
        sh = translate([-TOTAL_WIDTH / 2 - 10, y, z])(sh)
        sidecar_holes.append(sh)

    EXT_DEPTH = 2.0
    EXT_HEIGHT = 50.0
    ext_block = cube([LEG_THICK, EXT_DEPTH, EXT_HEIGHT])
    ext_l = translate([TOTAL_WIDTH / 2 - LEG_THICK, -STAND_DEPTH - EXT_DEPTH, 0])(ext_block)
    ext_r = translate([-TOTAL_WIDTH / 2, -STAND_DEPTH - EXT_DEPTH, 0])(ext_block)
    leg_l += ext_l
    leg_r += ext_r

    CLEARANCE_H = 3.0
    y_d = -STAND_DEPTH + 2.5
    z_d_total = 10.0 + CLEARANCE_H
    theta_rad = math.radians(-TILT_ANGLE)
    y_s = y_d * math.cos(theta_rad) - z_d_total * math.sin(theta_rad)
    z_s = y_d * math.sin(theta_rad) + z_d_total * math.cos(theta_rad)
    y_s = round(y_s, 2)
    z_s = round(z_s, 2)

    LOCK_HOLE_DIAM = 2.2
    CB_DIAM = 4.5
    CB_DEPTH = 4.0

    lock_hole_l = cylinder(d=LOCK_HOLE_DIAM, h=LEG_THICK + 20, _fn=32)
    lock_hole_l = rotate([0, 90, 0])(lock_hole_l)
    lock_hole_l = translate([TOTAL_WIDTH / 2 - LEG_THICK - 10, y_s, z_s])(lock_hole_l)

    cb_l = cylinder(d=CB_DIAM, h=CB_DEPTH + 10, _fn=32)
    cb_l = rotate([0, 90, 0])(cb_l)
    cb_l = translate([TOTAL_WIDTH / 2 - CB_DEPTH, y_s, z_s])(cb_l)

    lock_hole_r = cylinder(d=LOCK_HOLE_DIAM, h=LEG_THICK + 20, _fn=32)
    lock_hole_r = rotate([0, 90, 0])(lock_hole_r)
    lock_hole_r = translate([-TOTAL_WIDTH / 2 - 10, y_s, z_s])(lock_hole_r)

    cb_r = cylinder(d=CB_DIAM, h=CB_DEPTH + 10, _fn=32)
    cb_r = rotate([0, 90, 0])(cb_r)
    cb_r = translate([-TOTAL_WIDTH / 2 - 10, y_s, z_s])(cb_r)

    SLOT_H = 15.0
    SLOT_W = 5.0
    SLOT_Y = -STAND_DEPTH / 2.0 + 10.0
    SLOT_ZS = [40.0, 60.0, 80.0]

    c_top = cylinder(d=SLOT_W, h=LEG_THICK + 20, _fn=32)
    c_top = rotate([0, 90, 0])(c_top)
    c_top = translate([0, 0, (SLOT_H - SLOT_W) / 2])(c_top)

    c_bot = cylinder(d=SLOT_W, h=LEG_THICK + 20, _fn=32)
    c_bot = rotate([0, 90, 0])(c_bot)
    c_bot = translate([0, 0, -(SLOT_H - SLOT_W) / 2])(c_bot)

    vert_slot = hull()(c_top, c_bot)
    horiz_slot = rotate([90, 0, 0])(vert_slot)
    cross_slot = vert_slot + horiz_slot

    slot_x = -TOTAL_WIDTH / 2 - 10
    cable_slots = []
    for z_pos in SLOT_ZS:
        s = translate([slot_x, SLOT_Y, z_pos])(cross_slot)
        cable_slots.append(s)

    leg_l_cuts = [lock_hole_l, cb_l]
    leg_l -= union()(*leg_l_cuts)

    leg_r_cuts = sidecar_holes + [lock_hole_r, cb_r] + cable_slots
    leg_r -= union()(*leg_r_cuts)

    raw_stand = leg_l + leg_r

    leg_height = TOTAL_HEIGHT * 0.6
    bar_height = 20.0
    cut_angle = math.degrees(math.atan((leg_height - bar_height) / STAND_DEPTH))
    cut_angle = round(cut_angle, 2)

    slope_cutter = cube([TOTAL_WIDTH + 50, 400, 400])
    slope_cutter = rotate([cut_angle, 0, 0])(slope_cutter)
    slope_cutter = translate([-(TOTAL_WIDTH + 50) / 2, -STAND_DEPTH, 20])(slope_cutter)

    STEP_DEPTH = 15.0 + 2.0
    MASK_Z_START = -20.0
    MASK_Z_TOP = CLEARANCE_H + 25.0
    STEP_HEIGHT = MASK_Z_TOP - MASK_Z_START

    step_mask = cube([TOTAL_WIDTH + 60, STEP_DEPTH, STEP_HEIGHT])
    step_mask = translate([-(TOTAL_WIDTH + 60) / 2, -STAND_DEPTH - 2.0, MASK_Z_START])(step_mask)
    step_mask = rotate([-TILT_ANGLE, 0, 0])(step_mask)

    final_slope_cutter = slope_cutter - step_mask
    final_stand = raw_stand - final_slope_cutter
    return final_stand


def main():
    body = create_replica()
    stand = create_integrated_legs()
    full_model = body + stand

    final_model = rotate([TILT_ANGLE, 0, 0])(full_model)

    LEG_THICK = 5.0
    GROOVE_H = 4.0
    GROOVE_D = 2.5
    CLEARANCE_H = 3.0
    EXTRA_CUT = 0.1
    GROOVE_STOP_Y = -2.0
    GROOVE_START_Y = -200.0
    GROOVE_LEN = GROOVE_STOP_Y - GROOVE_START_Y

    g_left = cube([GROOVE_D + EXTRA_CUT, GROOVE_LEN, GROOVE_H])
    g_left = translate([TOTAL_WIDTH / 2 - LEG_THICK - EXTRA_CUT, GROOVE_START_Y, CLEARANCE_H])(g_left)

    g_right = cube([GROOVE_D + EXTRA_CUT, GROOVE_LEN, GROOVE_H])
    g_right = translate([-TOTAL_WIDTH / 2 + LEG_THICK - GROOVE_D, GROOVE_START_Y, CLEARANCE_H])(g_right)

    final_model = final_model - g_left - g_right

    ground_cut_box = cube([TOTAL_WIDTH + 100, STAND_DEPTH + 200, 100])
    ground_cut_box = translate([-(TOTAL_WIDTH + 100) / 2, -STAND_DEPTH - 100, -100])(ground_cut_box)
    final_model -= ground_cut_box

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "Base_Distributeur_Combined.scad")
    final_model.save_as_scad(output_path)
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
