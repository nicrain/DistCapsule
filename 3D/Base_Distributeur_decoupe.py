from solid2 import *
import os
import math

# --- Amazon Product Replica Parameters (MOLEDINO) ---
# Dimensions: 32L x 26W x 1.2H cm -> Increased Height for Servo
TOTAL_WIDTH = 260.0
TOTAL_HEIGHT = 310.0
TOTAL_THICKNESS = 12.0

# Layer Thicknesses (Total 12mm)
# Structure: Back Plate + Rail Layer + Front Plate
BACK_THICKNESS = 4.0
RAIL_THICKNESS = 4.0   # Space for capsule rim (approx 1mm rim + clearance + tilt)
FRONT_THICKNESS = 4.0

# Nespresso Original Capsule Dimensions
CAPSULE_BODY_DIAM = 30.0
CAPSULE_RIM_DIAM = 37.0

# Design Tolerances
SLOT_WIDTH = 31.0       # Allows body (30mm) to pass, catches rim (37mm)
TRACK_WIDTH = 39.0      # Allows rim (37mm) to slide freely
ENTRY_HOLE_DIAM = 40.0  # Allows rim to be inserted from front
TOP_MARGIN = 60.0       # Distance from top edge to center of entry hole
BOTTOM_MARGIN = 10.0    # Distance from bottom edge to bottom of the slot

NUM_COLUMNS = 5
COLUMN_WIDTH = TOTAL_WIDTH / NUM_COLUMNS

# Tilt and Stand Parameters
TILT_ANGLE = 15.0       # Degrees to tilt back
STAND_DEPTH = 80.0      # How far back the stand extends (on the ground)
STAND_THICKNESS = 10.0  # Thickness of the stand legs

# Servo SG90 Parameters
SERVO_WIDTH = 23.0      # Width of the servo body (horizontal)
SERVO_HEIGHT = 12.5     # Thickness of the servo body (vertical in this orientation?)
                        # Standard SG90: 22.5 x 12.5 x 22.5 mm
                        # We will mount it such that the arm rotates in the XY plane (blocking the channel)
                        # So the servo axis is along Z (perpendicular to back plate)? 
                        # No, servo axis should be perpendicular to the plate (Y axis in our model coordinates before tilt)
                        # So the arm sweeps across the track.
SERVO_BODY_W = 23.0
SERVO_BODY_H = 23.0
SERVO_BODY_D = 12.5     # Depth (thickness)

# Servo Position
# User requested to move the servo UP so it doesn't overlap with the entry hole.
# Entry hole center is at TOTAL_HEIGHT - TOP_MARGIN (310). Radius 20 -> Top at 330.
# We place the servo shaft at 345 (15mm above the hole).
SERVO_Z_POS = 345.0
# Servo Offset: Keep it to the side (22mm)
SERVO_X_OFFSET = 22.0 

def create_replica(part="all"):
    # 1. Back Plate (Solid)
    # Position: Y = 0 to 4
    back_plate_block = cube([TOTAL_WIDTH, BACK_THICKNESS, TOTAL_HEIGHT])
    
    # 2. Middle Rail Layer (Tracks)
    # Position: Y = 4 to 8
    rail_block = cube([TOTAL_WIDTH, RAIL_THICKNESS, TOTAL_HEIGHT])
    
    tracks = []
    
    # Separate cutout lists for each layer to create the "recessed" mounting
    back_cutouts = []
    rail_cutouts = []
    front_cutouts = []
    
    for i in range(NUM_COLUMNS):
        cx = (i * COLUMN_WIDTH) + (COLUMN_WIDTH / 2)
        
        # --- Track Geometry ---
        track_radius = TRACK_WIDTH / 2.0
        
        # A. Rectangular part
        rect_start_z = BOTTOM_MARGIN + track_radius
        rect_height = (TOTAL_HEIGHT - TOP_MARGIN) - rect_start_z
        
        track_rect = cube([TRACK_WIDTH, RAIL_THICKNESS + 1, rect_height])
        track_rect = translate([cx - TRACK_WIDTH/2, -0.5, rect_start_z])(track_rect)
        tracks.append(track_rect)
        
        # B. Circular Bottom
        track_circle = cylinder(d=TRACK_WIDTH, h=RAIL_THICKNESS + 1, _fn=64)
        track_circle = rotate([-90, 0, 0])(track_circle)
        track_circle = translate([cx, -0.5, rect_start_z])(track_circle)
        tracks.append(track_circle)
        
        # C. Entry Clearance (Top)
        entry_clearance = cylinder(d=ENTRY_HOLE_DIAM, h=RAIL_THICKNESS + 1, _fn=64)
        entry_clearance = rotate([-90, 0, 0])(entry_clearance)
        entry_clearance = translate([cx, -0.5, TOTAL_HEIGHT - TOP_MARGIN])(entry_clearance)
        tracks.append(entry_clearance)
        
        # --- Servo Mounting (Recessed) ---
        # Goal: Sink the servo into the Back Plate so the ears rest on the Rail Layer.
        # This allows the shaft to protrude further to the front.
        
        # Dimensions
        sg90_w = 12.5
        sg90_h_body = 23.0
        sg90_h_ears = 33.0  # Total length including flanges
        
        # Position (Above hole)
        hole_top_z = (TOTAL_HEIGHT - TOP_MARGIN) + (ENTRY_HOLE_DIAM / 2.0)
        margin = 6.0
        servo_bottom_z = hole_top_z + margin
        
        # 1. Body Cutout (Small) - Goes through Rail and Front
        # Positioned at servo_bottom_z
        c_body = cube([sg90_w, TOTAL_THICKNESS + 2, sg90_h_body])
        c_body = translate([cx - sg90_w/2, -1, servo_bottom_z])(c_body)
        
        rail_cutouts.append(c_body)
        front_cutouts.append(c_body)
        
        # 2. Ears Cutout (Large) - Goes through Back Plate ONLY
        # Centered on the body cutout, but taller
        # Center Z of body = servo_bottom_z + sg90_h_body/2
        center_z = servo_bottom_z + sg90_h_body/2
        
        c_ears = cube([sg90_w, BACK_THICKNESS + 2, sg90_h_ears])
        # Align center Z
        c_ears = translate([cx - sg90_w/2, -1, center_z - sg90_h_ears/2])(c_ears)
        
        back_cutouts.append(c_ears)
        
        # 3. Screw Holes - Go through Rail and Front (for mounting)
        # Located at the "ears" position (top and bottom of the body)
        # Screw distance approx 28mm apart (center to center)
        screw_dist = 28.0
        
        s_top = cylinder(d=2.0, h=TOTAL_THICKNESS + 2, _fn=32)
        s_top = rotate([-90, 0, 0])(s_top)
        s_top = translate([cx, -1, center_z + screw_dist/2])(s_top)
        
        s_bot = cylinder(d=2.0, h=TOTAL_THICKNESS + 2, _fn=32)
        s_bot = rotate([-90, 0, 0])(s_bot)
        s_bot = translate([cx, -1, center_z - screw_dist/2])(s_bot)
        
        rail_cutouts.append(s_top)
        rail_cutouts.append(s_bot)
        front_cutouts.append(s_top)
        front_cutouts.append(s_bot)

    # Apply tracks to rail layer
    if tracks:
        rail_block -= union()(*tracks)

    # Apply Layer-Specific Cutouts
    if back_cutouts:
        back_plate_block -= union()(*back_cutouts)
        
    if rail_cutouts:
        rail_block -= union()(*rail_cutouts)
        
    rail_layer = translate([0, BACK_THICKNESS, 0])(rail_block)


    # 3. Front Plate (Slots + Entry Holes)
    # Position: Y = 8 to 12
    front_block = cube([TOTAL_WIDTH, FRONT_THICKNESS, TOTAL_HEIGHT])
    
    slots = []
    entries = []
    
    for i in range(NUM_COLUMNS):
        cx = (i * COLUMN_WIDTH) + (COLUMN_WIDTH / 2)
        
        # Slot Geometry
        slot_radius = SLOT_WIDTH / 2.0
        
        # A. Rectangular part
        rect_start_z = BOTTOM_MARGIN + slot_radius
        rect_height = (TOTAL_HEIGHT - TOP_MARGIN) - rect_start_z
        
        slot_rect = cube([SLOT_WIDTH, FRONT_THICKNESS + 1, rect_height])
        slot_rect = translate([cx - SLOT_WIDTH/2, -0.5, rect_start_z])(slot_rect)
        slots.append(slot_rect)
        
        # B. Circular Bottom
        slot_circle = cylinder(d=SLOT_WIDTH, h=FRONT_THICKNESS + 1, _fn=64)
        slot_circle = rotate([-90, 0, 0])(slot_circle)
        slot_circle = translate([cx, -0.5, rect_start_z])(slot_circle)
        slots.append(slot_circle)
        
        # C. Entry Hole (Top)
        entry = cylinder(d=ENTRY_HOLE_DIAM, h=FRONT_THICKNESS + 2, _fn=64)
        entry = rotate([-90, 0, 0])(entry)
        entry = translate([cx, -1, TOTAL_HEIGHT - TOP_MARGIN])(entry)
        entries.append(entry)
        
    if slots:
        front_block -= union()(*slots)
    if entries:
        front_block -= union()(*entries)
        
    # Apply servo cutouts to front plate (Through Hole)
    if front_cutouts:
        front_block -= union()(*front_cutouts)

    front_layer = translate([0, BACK_THICKNESS + RAIL_THICKNESS, 0])(front_block)

    # --- Base Filler ---
    # Fill the wedge gap under the body (Y=0 to 12) caused by the 15 deg tilt.
    # We simply extend the body downwards. The excess will be cut globally in the main block.
    filler_block = cube([TOTAL_WIDTH, TOTAL_THICKNESS, 50])
    filler_block = translate([0, 0, -50])(filler_block)
    
    # Return specific part if requested
    if part == "front":
        return translate([-TOTAL_WIDTH/2, 0, 0])(front_block)
    elif part == "rail":
        return translate([-TOTAL_WIDTH/2, 0, 0])(rail_block)
    elif part == "back":
        return translate([-TOTAL_WIDTH/2, 0, 0])(back_plate_block)

    # 4. Combine into one object
    assembly = back_plate_block + rail_layer + front_layer + filler_block
    
    # --- Rounded Corners (Top Left & Top Right) ---
    CORNER_RADIUS = 15.0
    EPS = 1.0 # Extra margin to ensure clean cuts
    
    # Cutter for Top-Left (X=0)
    # Block covers [-EPS, R] in X, [H-R, H+EPS] in Z
    tl_block = cube([CORNER_RADIUS + EPS, TOTAL_THICKNESS + 20, CORNER_RADIUS + EPS])
    tl_block = translate([-EPS, -10, TOTAL_HEIGHT - CORNER_RADIUS])(tl_block)
    
    tl_cyl = cylinder(r=CORNER_RADIUS, h=TOTAL_THICKNESS + 20, _fn=64)
    tl_cyl = rotate([-90, 0, 0])(tl_cyl) # Axis along Y
    tl_cyl = translate([CORNER_RADIUS, -10, TOTAL_HEIGHT - CORNER_RADIUS])(tl_cyl)
    
    tl_cutter = tl_block - tl_cyl
    
    # Cutter for Top-Right (X=TOTAL_WIDTH)
    # Block covers [W-R, W+EPS] in X, [H-R, H+EPS] in Z
    tr_block = cube([CORNER_RADIUS + EPS, TOTAL_THICKNESS + 20, CORNER_RADIUS + EPS])
    tr_block = translate([TOTAL_WIDTH - CORNER_RADIUS, -10, TOTAL_HEIGHT - CORNER_RADIUS])(tr_block)
    
    tr_cyl = cylinder(r=CORNER_RADIUS, h=TOTAL_THICKNESS + 20, _fn=64)
    tr_cyl = rotate([-90, 0, 0])(tr_cyl)
    tr_cyl = translate([TOTAL_WIDTH - CORNER_RADIUS, -10, TOTAL_HEIGHT - CORNER_RADIUS])(tr_cyl)
    
    tr_cutter = tr_block - tr_cyl
    
    assembly = assembly - tl_cutter - tr_cutter
    
    # --- Sidecar Mounting Holes (Right Side) ---
    # Holes on the rightmost edge to attach the Control Box
    # Located on the Bottom Half (< 190mm)
    # Adjusted to fit in the 6.5mm solid margin on the right edge.
    
    # Center on X axis for better preview
    assembly = translate([-TOTAL_WIDTH/2, 0, 0])(assembly)
    
    return assembly

def create_integrated_legs():
    """
    Generates a 'Picture Frame' style stand.
    Two legs at the extreme edges, connected by a bar at the bottom.
    """
    LEG_THICK = 15.0
    STAND_DEPTH = 90.0 # Depth on the ground
    
    # 1. Create the raw block for the stand (Legs + Crossbar)
    # Height reduced to 0.6 * TOTAL_HEIGHT
    
    # Left Leg Block (Positive X - User Left)
    leg_l = cube([LEG_THICK, STAND_DEPTH, TOTAL_HEIGHT * 0.6])
    leg_l = translate([TOTAL_WIDTH/2 - LEG_THICK, -STAND_DEPTH, 0])(leg_l)
    
    # Right Leg Block (Negative X - User Right)
    leg_r = cube([LEG_THICK, STAND_DEPTH, TOTAL_HEIGHT * 0.6])
    leg_r = translate([-TOTAL_WIDTH/2, -STAND_DEPTH, 0])(leg_r)
    
    # --- Sidecar Mounting Holes (Right Leg / Negative X) ---
    # Holes on the Right Leg (Negative X) to attach the Control Box
    
    sidecar_holes = []
    SIDECAR_HOLE_DIAM = 3.2 # M3
    
    # 1. Vertical Column at Y = -8.0
    # Bottom hole at 15.6 (Stand Frame) to match locking hole height (13.0) in Final Frame
    col_y = -8.0
    col_zs = [15.6, 65.6, 115.6]
    
    for z in col_zs:
        sh = cylinder(d=SIDECAR_HOLE_DIAM, h=LEG_THICK + 20, _fn=32)
        sh = rotate([0, 90, 0])(sh)
        sh = translate([-TOTAL_WIDTH/2 - 10, col_y, z])(sh)
        sidecar_holes.append(sh)
        
    # 2. Horizontal Row (aligned with bottom hole)
    # Spacing 20mm backwards. Z adjusted to maintain horizontal level in tilted view.
    # Hole 2: Y=-28.0, Z=21.0
    # Hole 3: Y=-48.0, Z=26.3
    extra_holes = [(-28.0, 21.0), (-48.0, 26.3)]
    
    for (y, z) in extra_holes:
        sh = cylinder(d=SIDECAR_HOLE_DIAM, h=LEG_THICK + 20, _fn=32)
        sh = rotate([0, 90, 0])(sh)
        sh = translate([-TOTAL_WIDTH/2 - 10, y, z])(sh)
        sidecar_holes.append(sh)
        
    # --- Leg Extension for Counterbore ---
    # We need to extend the legs backwards at the bottom to accommodate the counterbore.
    # Extension: 2mm deep, enough height to cover the step.
    EXT_DEPTH = 2.0
    EXT_HEIGHT = 50.0 # Arbitrary high enough, will be trimmed by slope_cutter
    
    ext_block = cube([LEG_THICK, EXT_DEPTH, EXT_HEIGHT])
    
    # Left Extension (Positive X)
    ext_l = translate([TOTAL_WIDTH/2 - LEG_THICK, -STAND_DEPTH - EXT_DEPTH, 0])(ext_block)
    leg_l += ext_l
    
    # Right Extension (Negative X)
    ext_r = translate([-TOTAL_WIDTH/2, -STAND_DEPTH - EXT_DEPTH, 0])(ext_block)
    leg_r += ext_r
    
    # --- Drawer Locking Holes (Screw Holes) ---
    # User requested holes on the side of the legs to fix the drawer.
    # Drawer is tilted by -15 deg.
    # Drawer Back Plate Center in Drawer Frame:
    # Y_d = -STAND_DEPTH + (5.0 / 2.0) = -90 + 2.5 = -87.5
    # Z_d = 10.0 (Middle of 20mm height)
    # Z_offset = CLEARANCE_H = 3.0
    
    CLEARANCE_H = 3.0
    
    # Transform to Stand Frame (Rotate -15 deg around X)
    # y_s = y_d * cos(theta) - (z_d + z_offset) * sin(theta)
    # z_s = y_d * sin(theta) + (z_d + z_offset) * cos(theta)
    
    y_d = -STAND_DEPTH + 2.5
    z_d_total = 10.0 + CLEARANCE_H
    theta_rad = math.radians(-TILT_ANGLE)
    
    y_s = y_d * math.cos(theta_rad) - z_d_total * math.sin(theta_rad)
    z_s = y_d * math.sin(theta_rad) + z_d_total * math.cos(theta_rad)
    
    y_s = round(y_s, 2)
    z_s = round(z_s, 2)
    
    LOCK_HOLE_DIAM = 2.2 # M2 Clearance
    CB_DIAM = 4.5 # M2 Head approx 3.8mm
    CB_DEPTH = 4.0 # Depth of the counterbore
    
    # Left Leg Hole (Positive X)
    # 1. Through Hole
    lock_hole_l = cylinder(d=LOCK_HOLE_DIAM, h=LEG_THICK + 20, _fn=32)
    lock_hole_l = rotate([0, 90, 0])(lock_hole_l)
    lock_hole_l = translate([TOTAL_WIDTH/2 - LEG_THICK - 10, y_s, z_s])(lock_hole_l)
    
    # 2. Counterbore (From Right/Outside of the Left Leg)
    # Leg Right Face is at X = TOTAL_WIDTH/2
    # Cut from X = TOTAL_WIDTH/2 - CB_DEPTH to TOTAL_WIDTH/2 + 10
    cb_l = cylinder(d=CB_DIAM, h=CB_DEPTH + 10, _fn=32)
    cb_l = rotate([0, 90, 0])(cb_l)
    cb_l = translate([TOTAL_WIDTH/2 - CB_DEPTH, y_s, z_s])(cb_l)
    
    # Right Leg Hole (Negative X)
    # 1. Through Hole
    lock_hole_r = cylinder(d=LOCK_HOLE_DIAM, h=LEG_THICK + 20, _fn=32)
    lock_hole_r = rotate([0, 90, 0])(lock_hole_r)
    lock_hole_r = translate([-TOTAL_WIDTH/2 - 10, y_s, z_s])(lock_hole_r)
    
    # 2. Counterbore (From Left/Outside of the Right Leg)
    # Leg Left Face is at X = -TOTAL_WIDTH/2
    # Cut from X = -TOTAL_WIDTH/2 - 10 to -TOTAL_WIDTH/2 + CB_DEPTH
    cb_r = cylinder(d=CB_DIAM, h=CB_DEPTH + 10, _fn=32)
    cb_r = rotate([0, 90, 0])(cb_r)
    cb_r = translate([-TOTAL_WIDTH/2 - 10, y_s, z_s])(cb_r)
    
    # --- Cable Management Slots (Right Leg / Negative X) ---
    # 3 Cross Slots: 15mm x 15mm overall
    # Y = -35.0 (Center -45 + 10)
    # Z = 40, 60, 80
    
    SLOT_H = 15.0
    SLOT_W = 5.0
    SLOT_Y = -STAND_DEPTH / 2.0 + 10.0 # Shifted 10mm forward from center
    SLOT_ZS = [40.0, 60.0, 80.0]
    
    # Create Vertical Slot
    c_top = cylinder(d=SLOT_W, h=LEG_THICK + 20, _fn=32)
    c_top = rotate([0, 90, 0])(c_top)
    c_top = translate([0, 0, (SLOT_H - SLOT_W)/2])(c_top)
    
    c_bot = cylinder(d=SLOT_W, h=LEG_THICK + 20, _fn=32)
    c_bot = rotate([0, 90, 0])(c_bot)
    c_bot = translate([0, 0, -(SLOT_H - SLOT_W)/2])(c_bot)
    
    vert_slot = hull()(c_top, c_bot)
    
    # Create Horizontal Slot (Rotate vertical by 90 deg around X)
    horiz_slot = rotate([90, 0, 0])(vert_slot)
    
    cross_slot = vert_slot + horiz_slot
    
    # Apply to Right Leg (leg_r) - Negative X
    slot_x = -TOTAL_WIDTH/2 - 10
    
    cable_slots = []
    for z_pos in SLOT_ZS:
        s = translate([slot_x, SLOT_Y, z_pos])(cross_slot)
        cable_slots.append(s)

    # --- Apply All Cuts ---
    
    # Left Leg Cuts
    leg_l_cuts = [lock_hole_l, cb_l]
    leg_l -= union()(*leg_l_cuts)
    
    # Right Leg Cuts
    leg_r_cuts = sidecar_holes + [lock_hole_r, cb_r] + cable_slots
    leg_r -= union()(*leg_r_cuts)

    raw_stand = leg_l + leg_r
    
    # 2. Cut the shape to be triangular
    
    # B. Cut the Back/Inside to make it a frame
    # We want a triangular profile from the side.
    # Top point: Y=0, Z = TOTAL_HEIGHT * 0.6
    # Bottom back point: Y=-STAND_DEPTH, Z = 20mm (Crossbar height)
    
    leg_height = TOTAL_HEIGHT * 0.6
    bar_height = 20.0
    
    # Calculate angle dynamically
    # tan(angle) = opposite / adjacent = (leg_height - bar_height) / STAND_DEPTH
    cut_angle = math.degrees(math.atan((leg_height - bar_height) / STAND_DEPTH))
    cut_angle = round(cut_angle, 2)
    
    slope_cutter = cube([TOTAL_WIDTH + 50, 400, 400])
    # Rotate so the bottom face becomes the slope
    # We want to keep what is BELOW the slope.
    # If we rotate by +cut_angle, the bottom face tilts up-forward.
    slope_cutter = rotate([cut_angle, 0, 0])(slope_cutter)
    
    # Position the cutter so its bottom-back edge touches the crossbar top
    # Target point: Y = -STAND_DEPTH, Z = 20
    slope_cutter = translate([-(TOTAL_WIDTH+50)/2, -STAND_DEPTH, 20])(slope_cutter)
    
    # --- Step Protector ---
    # User requested a "step" at the back to ensure the locking hole has enough material.
    # This step should match the drawer back plate shape (tilted -15 deg).
    # We subtract this "step shape" from the slope_cutter, so the cutter DOES NOT cut this area.
    # We also need to extend it downwards to fill the gap between the slope line and the ground.
    
    STEP_DEPTH = 15.0 + 2.0 # Cover the back plate (5mm) + margin + hole area + EXTENSION
    
    # Calculate height to cover from bottom (-20) to top (CLEARANCE_H + 25)
    MASK_Z_START = -20.0
    MASK_Z_TOP = CLEARANCE_H + 25.0
    STEP_HEIGHT = MASK_Z_TOP - MASK_Z_START
    
    step_mask = cube([TOTAL_WIDTH + 60, STEP_DEPTH, STEP_HEIGHT])
    # Position at the back, aligned with the groove/drawer
    # Start at Y = -STAND_DEPTH - 2.0 (Extension start)
    step_mask = translate([-(TOTAL_WIDTH+60)/2, -STAND_DEPTH - 2.0, MASK_Z_START])(step_mask)
    # Rotate to match drawer tilt
    step_mask = rotate([-TILT_ANGLE, 0, 0])(step_mask)
    
    # Modify the cutter
    final_slope_cutter = slope_cutter - step_mask
    
    final_stand = raw_stand - final_slope_cutter
    
    return final_stand

if __name__ == "__main__":
    # 1. Create the Main Body (Vertical)
    body = create_replica()
    
    # 2. Create the Integrated Stand (Vertical, pre-cut)
    stand = create_integrated_legs()
    
    # 3. Combine them
    full_model = body + stand
    
    # 4. Rotate the entire assembly by 15 degrees
    # This makes the body tilt back, and the stand's bottom (which was cut at 15 deg) become flat.
    final_model = rotate([TILT_ANGLE, 0, 0])(full_model)
    
    # 4.5. Global Groove Cut (Horizontal)
    # Cut the drawer grooves horizontally after rotation.
    LEG_THICK = 15.0
    GROOVE_H = 4.0
    GROOVE_D = 2.5
    CLEARANCE_H = 3.0
    EXTRA_CUT = 0.1 # Extra width to ensure clean cut on the open side
    GROOVE_STOP_Y = -2.0 # Stop before hitting the main body (Y=0)
    
    # Calculate Groove Length
    # Start far back (-200) and stop at GROOVE_STOP_Y
    GROOVE_START_Y = -200.0
    GROOVE_LEN = GROOVE_STOP_Y - GROOVE_START_Y
    
    # Left Groove (Positive X)
    # Inner face of left leg is at X = TOTAL_WIDTH/2 - LEG_THICK
    # We want to cut from (Face - EXTRA) to (Face + GROOVE_D)
    g_left = cube([GROOVE_D + EXTRA_CUT, GROOVE_LEN, GROOVE_H])
    g_left = translate([TOTAL_WIDTH/2 - LEG_THICK - EXTRA_CUT, GROOVE_START_Y, CLEARANCE_H])(g_left)
    
    # Right Groove (Negative X)
    # Inner face of right leg is at X = -TOTAL_WIDTH/2 + LEG_THICK
    # We want to cut from (Face - GROOVE_D) to (Face + EXTRA)
    g_right = cube([GROOVE_D + EXTRA_CUT, GROOVE_LEN, GROOVE_H])
    g_right = translate([-TOTAL_WIDTH/2 + LEG_THICK - GROOVE_D, GROOVE_START_Y, CLEARANCE_H])(g_right)
    
    final_model = final_model - g_left - g_right
    
    # 5. Global Ground Cut
    # Cut everything below Z=0 to ensure a perfectly flat base.
    # This handles the body filler and any other protrusions.
    ground_cut_box = cube([TOTAL_WIDTH + 100, STAND_DEPTH + 200, 100])
    ground_cut_box = translate([-(TOTAL_WIDTH+100)/2, -STAND_DEPTH - 100, -100])(ground_cut_box)
    
    final_model -= ground_cut_box
    
    # --- Splitting Logic (Flat Cut + Printed Pins) ---
    # Updated Z=220 to be just below the top entry holes (Z_local ~230 -> Z_global ~222)
    CUT_Z = 220.0
    
    # Pin Parameters
    PIN_DIAM = 4.0
    PIN_RADIUS = PIN_DIAM / 2.0
    PIN_HEIGHT = 8.0 # Height of the pin sticking out
    TOLERANCE = 0.3 # Gap for printed pins (0.3mm is safer for FDM)
    
    # Pin Locations
    # Calculated based on TILT_ANGLE=15 and Z=220
    # Main Body Center Y_local = 6.0
    # z_global = y_local * sin(15) + z_local * cos(15) = 220
    # 6 * 0.2588 + z_local * 0.9659 = 220 => z_local = 226
    # y_global = y_local * cos(15) - z_local * sin(15)
    # 6 * 0.9659 - 226 * 0.2588 = 5.8 - 58.5 = -52.7
    
    PIN_Y_CENTER = -52.7
    
    # Use the solid pillars between columns for pins
    # Columns are 52mm wide. Tracks are 39mm wide.
    # Gap between tracks is 13mm.
    # Pillars are at X = +/- 26.0 and +/- 78.0
    
    pin_locs = [
        (-78.0, PIN_Y_CENTER),       # Pillar between Col 1 & 2
        (-26.0, PIN_Y_CENTER),       # Pillar between Col 2 & 3
        (26.0, PIN_Y_CENTER),        # Pillar between Col 3 & 4
        (78.0, PIN_Y_CENTER)         # Pillar between Col 4 & 5
    ]
    
    pins = []
    holes = []
    
    CHAMFER_H = 1.5 # Height of the chamfer/taper
    
    for (px, py) in pin_locs:
        # Pin (for Bottom Part) - Sticking UP
        # 1. Main cylindrical body
        p_body = cylinder(r=PIN_RADIUS, h=PIN_HEIGHT - CHAMFER_H, _fn=32)
        # 2. Tapered top (Chamfer) for easier insertion
        p_top = cylinder(r1=PIN_RADIUS, r2=PIN_RADIUS - 1.0, h=CHAMFER_H, _fn=32)
        p_top = translate([0, 0, PIN_HEIGHT - CHAMFER_H])(p_top)
        
        p = p_body + p_top
        p = translate([px, py, CUT_Z])(p)
        pins.append(p)
        
        # Hole (for Top Part) - Going UP
        # Radius = PIN_RADIUS + TOLERANCE
        # Depth = PIN_HEIGHT + 1.0 (Clearance at tip)
        
        # Fix: Start cut slightly below surface (-0.1) to ensure clean opening
        HOLE_EXTRA_Z = 0.1
        
        # 1. Main Hole Body (shifted down by EXTRA_Z)
        h = cylinder(r=PIN_RADIUS + TOLERANCE, h=PIN_HEIGHT + 1.0 + HOLE_EXTRA_Z, _fn=32)
        h = translate([0, 0, -HOLE_EXTRA_Z])(h)
        
        h = translate([px, py, CUT_Z])(h)
        holes.append(h)
        
    pins_union = union()(*pins)
    holes_union = union()(*holes)
    
    # Create Bottom Part (Z < 140)
    # Intersection with Cube + Pins
    cutter_bot = cube([500, 500, CUT_Z])
    cutter_bot = translate([-250, -250, 0])(cutter_bot)
    
    part_bottom = intersection()(final_model, cutter_bot)
    part_bottom += pins_union
    
    # Create Top Part (Z > 140)
    # Intersection with Cube - Holes
    cutter_top = cube([500, 500, 500])
    cutter_top = translate([-250, -250, CUT_Z])(cutter_top)
    
    part_top = intersection()(final_model, cutter_top)
    part_top -= holes_union
    
    # Move Top Part to Z=0 for printing (Optional, but good for preview)
    # part_top = translate([0, 0, -CUT_Z])(part_top)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Save Parts
    file_path_bot = os.path.join(script_dir, "Base_Distributeur_Bottom.scad")
    part_bottom.save_as_scad(file_path_bot)
    print(f"Generated: {file_path_bot}")
    
    file_path_top = os.path.join(script_dir, "Base_Distributeur_Top.scad")
    part_top.save_as_scad(file_path_top)
    print(f"Generated: {file_path_top}")

