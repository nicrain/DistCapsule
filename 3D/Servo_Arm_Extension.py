from solid2 import *
import os

# --- SG90 Single Arm Dimensions (Reference) ---
# These are the dimensions of the "cavity" we need to create
# User measured total length = 21.5mm.
# Total Length = (Hub_Diam/2) + Center_to_Tip_End
# 21.5 = 3.75 + Center_to_Tip_End => Center_to_Tip_End = 17.75
ORIGINAL_ARM_LENGTH = 19.25 # From center to tip end (increased by 1.5mm)
ORIGINAL_HUB_DIAM = 7.5     # Diameter of the round part (with clearance)
ORIGINAL_ARM_WIDTH = 5.5    # Width of the arm part (with clearance, increased by 0.5mm)
ORIGINAL_ARM_THICK = 2.0    # Thickness of the flat arm part
ORIGINAL_HUB_HEIGHT = 4.5   # Total height of the hub

# --- Extension Arm Parameters ---
# Shape: Circular Disk (Cam)
# Diameter: 38mm
# Rotation Center: At 30mm of the diameter (Offset)
EXT_DIAMETER = 38.0
EXT_THICKNESS = 4.0         # Total thickness
SCREW_HOLE_DIAM = 2.4       # For the M2/M2.5 screw to pass through

def create_extension_arm():
    # 1. Main Body (Circular Disk with Offset)
    # Diameter 38mm. Radius 19mm.
    # Rotation Center (Servo Shaft) is at [0,0].
    # User wants rotation center at "30mm of the diameter".
    # This implies the distance from the shaft to the furthest edge is 30mm.
    # Offset = Reach - Radius = 30 - 19 = 11mm.
    # We translate the circle center by 11mm along Y (direction of the arm).
    
    OFFSET = 11.0
    
    main_body = cylinder(d=EXT_DIAMETER, h=EXT_THICKNESS)
    main_body = translate([0, OFFSET, 0])(main_body)
    
    # 2. The Recess (Pocket for the original arm)
    
    # 2. The Recess (Pocket for the original arm)
    # Located on the BOTTOM (Z=0)
    # Shape: "Chain on wheels" (Hull of Hub Circle and Tip Circle)
    # User requested smooth transition from Hub (7.5mm) to Tip (5mm).
    
    RECESS_DEPTH = 3.0
    
    # Calculate Tip Circle Center
    # Total length is 19.5. Tip circle diam is 5.0.
    # Center is at 19.5 - 2.5 = 17.0
    tip_center_y = ORIGINAL_ARM_LENGTH - (ORIGINAL_ARM_WIDTH / 2.0)
    
    # Create the smooth shape using hull()
    # 1. Hub Circle at [0,0]
    # 2. Tip Circle at [0, tip_center_y]
    recess_obj = hull()(
        cylinder(d=ORIGINAL_HUB_DIAM, h=RECESS_DEPTH + 0.1),
        translate([0, tip_center_y, 0])(
            cylinder(d=ORIGINAL_ARM_WIDTH, h=RECESS_DEPTH + 0.1)
        )
    )
    
    recess = translate([0, 0, -0.1])(recess_obj)
    
    # 3. Screw area thickness increase (4mm diameter circle, 1mm height at recess bottom)
    screw_area_fill = cylinder(d=4.0, h=1.1)
    screw_area_fill = translate([0, 0, 2.0])(screw_area_fill)
    
    # 4. Bottom side recess (4mm diameter, 1mm depth on the opposite face)
    bottom_recess = cylinder(d=4.0, h=1.0)
    bottom_recess = translate([0, 0, EXT_THICKNESS - 0.5])(bottom_recess)
    
    # 5. Screw Hole (Through all)
    screw_hole = cylinder(d=SCREW_HOLE_DIAM, h=EXT_THICKNESS + 2)
    screw_hole = translate([0, 0, -1])(screw_hole)
    
    # 6. Final Boolean (before flip)
    final_part = main_body - recess + screw_area_fill - bottom_recess - screw_hole
    
    # User requested to flip it upside down for printing optimization
    # (Avoid supports by putting the flat face on the bed and the recess on top)
    final_part = rotate([180, 0, 0])(final_part)
    final_part = translate([0, 0, EXT_THICKNESS])(final_part)
    
    return final_part

if __name__ == "__main__":
    part = create_extension_arm()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "Servo_Arm_Extension.scad")
    
    part.save_as_scad(file_path)
    print(f"Generated SCAD: {file_path}")
