from solid2 import *
import os

# --- Dimensions from Base_Distributeur.py ---
TOTAL_WIDTH = 260.0
LEG_THICK = 15.0
STAND_DEPTH = 90.0
TILT_ANGLE = 15.0

# --- Drawer Parameters ---
GROOVE_DEPTH = 2.5
DRAWER_THICKNESS = 3.6
CLEARANCE_W = 0.5 # Total width clearance (0.25 per side)

# Inner width between legs
INNER_WIDTH = TOTAL_WIDTH - (2 * LEG_THICK)

# Drawer Width = Inner Width + (2 * Groove Depth) - Clearance
DRAWER_WIDTH = INNER_WIDTH + (2 * GROOVE_DEPTH) - CLEARANCE_W

# Drawer Length
# It needs to slide in from the back.
# Length should match STAND_DEPTH roughly.
DRAWER_LENGTH = STAND_DEPTH

# Hole Grid Parameters
HOLE_DIAM = 4.0
HOLE_SPACING = 10.0

def create_drawer():
    # 1. Base Plate
    # Centered on X
    base = cube([DRAWER_WIDTH, DRAWER_LENGTH, DRAWER_THICKNESS])
    base = translate([-DRAWER_WIDTH/2, -DRAWER_LENGTH, 0])(base)
    
    # 2. Back Plate (Handle / Seal)
    # Located at the back end (Y = -DRAWER_LENGTH)
    # It should fill the gap between legs (INNER_WIDTH)
    # Height: Let's make it 20mm high to match the old crossbar look
    # Thickness: 5mm
    BACK_HEIGHT = 20.0
    BACK_THICK = 5.0
    
    back_plate = cube([INNER_WIDTH - 0.5, BACK_THICK, BACK_HEIGHT]) # 0.5 clearance for back plate width
    # Position: Centered X, At back Y, On top of base (or flush bottom?)
    # Let's make it flush bottom, so it sticks up.
    back_plate = translate([-(INNER_WIDTH - 0.5)/2, -DRAWER_LENGTH, 0])(back_plate)
    
    drawer = base + back_plate
    
    # --- Cable Management Holes in Back Plate ---
    # 6 holes, 20mm wide.
    # Z range: 8.6mm to 15.0mm.
    
    NUM_CABLE_HOLES = 6
    CABLE_HOLE_W = 20.0
    CABLE_HOLE_H = 15.0 - 8.6 # 6.4mm
    CABLE_HOLE_Z = 8.6
    CABLE_HOLE_SPACING = 15.0
    
    # Calculate total width of the hole array
    total_holes_width = (NUM_CABLE_HOLES * CABLE_HOLE_W) + ((NUM_CABLE_HOLES - 1) * CABLE_HOLE_SPACING)
    
    # Start X (Centered)
    start_x_cable = -total_holes_width / 2.0 + (CABLE_HOLE_W / 2.0)
    
    cable_cutouts = []
    for k in range(NUM_CABLE_HOLES):
        cx = start_x_cable + (k * (CABLE_HOLE_W + CABLE_HOLE_SPACING))
        
        # Cutout block
        cutout = cube([CABLE_HOLE_W, BACK_THICK + 2, CABLE_HOLE_H])
        cutout = translate([cx - CABLE_HOLE_W/2, -DRAWER_LENGTH - 1, CABLE_HOLE_Z])(cutout)
        cable_cutouts.append(cutout)
        
    for c in cable_cutouts:
        drawer -= c
    
    # --- Side Locking Holes ---
    # 2.8mm Through Holes on the side of the back plate.
    # Position: Z=10.0 (Middle of 20mm height)
    # Y = -DRAWER_LENGTH + (BACK_THICK / 2) = -90 + 2.5 = -87.5
    # Depth: Drill through to the first/last cable cutout.
    
    LOCK_HOLE_DIAM = 2.8
    LOCK_HOLE_Z = 10.0
    LOCK_HOLE_Y = -DRAWER_LENGTH + (BACK_THICK / 2.0)
    
    # Left Hole (X negative)
    # Needs to reach the first cutout.
    # First cutout center X is start_x_cable.
    # Cutout width is 20. So left edge is start_x_cable - 10.
    # Drawer left edge is -DRAWER_WIDTH/2.
    # Hole length needs to be slightly more than distance to cutout.
    
    # Right Hole (X positive)
    # Needs to reach the last cutout.
    
    # Let's just make them long enough to definitely hit the cutout space (e.g. 50mm)
    
    lh = cylinder(d=1.8, h=40) # M2 Pilot Hole (1.8mm)
    lh = rotate([0, 90, 0])(lh)
    
    # Left Side Hole
    lh_l = translate([-DRAWER_WIDTH/2 - 10, LOCK_HOLE_Y, LOCK_HOLE_Z])(lh)
    
    # Right Side Hole (Rotate 180 or just translate from right)
    lh_r = translate([DRAWER_WIDTH/2 + 10, LOCK_HOLE_Y, LOCK_HOLE_Z])(rotate([0, 180, 0])(lh))
    
    drawer -= lh_l
    drawer -= lh_r

    # 3. Grid Holes
    # Create a grid of holes on the base plate
    # Avoid the edges (Groove area)
    # Groove engagement is 2.5mm - 0.25 = 2.25mm.
    # Let's leave 5mm margin from side edges.
    
    start_x = -DRAWER_WIDTH/2 + 10
    end_x = DRAWER_WIDTH/2 - 10
    start_y = -DRAWER_LENGTH + 10 + BACK_THICK # Avoid back plate
    end_y = -10
    
    holes = []
    
    # Calculate number of holes
    x_range = end_x - start_x
    y_range = end_y - start_y
    
    nx = int(x_range / HOLE_SPACING)
    ny = int(y_range / HOLE_SPACING)
    
    for i in range(nx + 1):
        for j in range(ny + 1):
            hx = start_x + i * HOLE_SPACING
            hy = start_y + j * HOLE_SPACING
            
            h = cylinder(d=HOLE_DIAM, h=DRAWER_THICKNESS + 2)
            h = translate([hx, hy, -1])(h)
            holes.append(h)
            
    for h in holes:
        drawer -= h
        
    return drawer

if __name__ == "__main__":
    part = create_drawer()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "Drawer.scad")
    
    part.save_as_scad(file_path)
    print(f"Generated: {file_path}")
