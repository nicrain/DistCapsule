from solid2 import *
import os
import math

# --- Control Box Parameters ---
BOX_WIDTH = 100.0
BOX_HEIGHT = 200.0  # Slightly taller than the bottom split (190mm)
BOX_DEPTH = 50.0
WALL_THICKNESS = 3.0
TILT_ANGLE = 15.0

# Hardware Dimensions
# Screen: 40mm x 28mm PCB (Assumed for 1.3" module)
SCREEN_PCB_W = 40.0
SCREEN_PCB_H = 28.0
SCREEN_VIEW_W = 24.0 # Viewport width
SCREEN_VIEW_H = 24.0 # Viewport height

# Fingerprint Sensor (Trapezoid Prism)
# User: "45x22x19, slanted window... short side 29... trapezoid (top 29, bottom 45)"
# This describes the side profile (Length vs Depth?).
# Let's assume the FACE on the box is the 22mm x 29mm (or 45mm?) area.
# Usually the "Face" is the part you touch.
# If it's a trapezoid prism, the face might be the slanted part?
# Let's make a cutout that is 22mm wide and 45mm tall (max dimension) to be safe,
# or 29mm if the face is the small part.
# Let's assume the cutout needs to be 22mm (Width) x 45mm (Height) to fit the whole unit?
# Or maybe the face is 22x29 and the body expands to 45?
# Let's make a 23mm x 46mm rectangular cutout for now.
FP_CUTOUT_W = 23.0
FP_CUTOUT_H = 46.0

# Camera (Pi Module 3)
CAM_W = 25.0
CAM_H = 24.0
CAM_LENS_D = 8.0

# Mounting Holes (Must match Base_Distributeur)
MOUNT_HOLE_Z = [50, 100, 150]
MOUNT_HOLE_DIAM = 3.2

def create_control_box():
    # 1. Main Shell (Hollow Box)
    # Open at the BACK (Y=BOX_DEPTH)
    shell = cube([BOX_WIDTH, BOX_DEPTH, BOX_HEIGHT])
    cavity = cube([BOX_WIDTH - 2*WALL_THICKNESS, BOX_DEPTH, BOX_HEIGHT - 2*WALL_THICKNESS])
    cavity = translate([WALL_THICKNESS, WALL_THICKNESS, WALL_THICKNESS])(cavity) # Leave front wall (Y=0..3)
    
    box = shell - cavity
    
    # 2. Cutouts on Front Face (Y=0 to WALL_THICKNESS)
    
    # A. Fingerprint Sensor (Bottom)
    # Position: Centered X, Z=30
    fp_z = 30.0
    fp_cutout = cube([FP_CUTOUT_W, WALL_THICKNESS + 10, FP_CUTOUT_H])
    fp_cutout = translate([BOX_WIDTH/2 - FP_CUTOUT_W/2, -5, fp_z - FP_CUTOUT_H/2])(fp_cutout)
    box -= fp_cutout
    
    # B. Screen (Middle)
    # Position: Centered X, Z=100
    screen_z = 100.0
    # PCB Cutout (Inside) - Optional, for now just Viewport
    screen_cutout = cube([SCREEN_VIEW_W, WALL_THICKNESS + 10, SCREEN_VIEW_H])
    screen_cutout = translate([BOX_WIDTH/2 - SCREEN_VIEW_W/2, -5, screen_z - SCREEN_VIEW_H/2])(screen_cutout)
    box -= screen_cutout
    
    # C. Camera (Top)
    # Position: Centered X, Z=180
    cam_z = 180.0
    cam_hole = cylinder(d=CAM_LENS_D, h=WALL_THICKNESS + 10)
    cam_hole = rotate([-90, 0, 0])(cam_hole)
    cam_hole = translate([BOX_WIDTH/2, -5, cam_z])(cam_hole)
    box -= cam_hole
    
    # 3. Mounting Holes (Left Side)
    # Holes on Left Wall (X=0) to match Distributor Right Wall.
    # Distributor Holes are at Y=6mm.
    
    mount_holes = []
    for z in MOUNT_HOLE_Z:
        mh = cylinder(d=MOUNT_HOLE_DIAM, h=WALL_THICKNESS + 10)
        mh = rotate([0, 90, 0])(mh)
        mh = translate([-5, 6, z])(mh)
        mount_holes.append(mh)
        
    for h in mount_holes:
        box -= h
        
    # 4. Cable Pass-through (Left Side)
    cable_hole = cube([WALL_THICKNESS + 10, 20, 40])
    cable_hole = translate([-5, 15, 120])(cable_hole)
    box -= cable_hole    # 4. Cable Pass-through (Right Side)
    cable_hole = cube([WALL_THICKNESS + 10, 20, 40])
    cable_hole = translate([BOX_WIDTH - 5, 15, 120])(cable_hole)
    box -= cable_hole
    
    # 5. Tilt Cut (Bottom)
    # The box is attached to a tilted distributor (15 deg back).
    # So the box is also tilted 15 deg back.
    # We need to cut the bottom so it sits flat on the table.
    # In the Box's coordinate system (Vertical), the "Floor" is a plane tilted UP by 15 degrees (from front to back).
    # Floor Plane passes through (0,0,0) and has normal vector tilted 15 deg.
    # Z_floor = Y * tan(15).
    # We remove everything where Z < Y * tan(15).
    
    # Create a large wedge to subtract
    # Wedge height at back (Y=50) = 50 * tan(15) ~= 13.4mm
    
    wedge_h = BOX_DEPTH * math.tan(math.radians(TILT_ANGLE)) + 5.0 # Extra margin
    
    # Create a wedge shape using a polyhedron or just a rotated cube
    # Rotated cube is easier.
    # We want the top face of the cutter to be the floor plane.
    # Cutter should be BELOW the floor plane.
    
    cutter = cube([BOX_WIDTH + 20, BOX_DEPTH + 50, 50])
    # Position it so its top face is at Z=0 initially
    cutter = translate([-10, -10, -50])(cutter)
    # Rotate it up by 15 degrees around X axis
    cutter = rotate([TILT_ANGLE, 0, 0])(cutter)
    
    box -= cutter
    
    return box

if __name__ == "__main__":
    control_box = create_control_box()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    f_box = os.path.join(script_dir, "Control_Box.scad")
    control_box.save_as_scad(f_box)
    print(f"Generated: {f_box}")
