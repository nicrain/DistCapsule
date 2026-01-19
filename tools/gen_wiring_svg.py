import os

# Output path
PATH = "docs/slides/pic/hardware_wiring.svg"

# SVG Header
svg = f"""<svg width="1000" height="800" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="100%" height="100%" fill="white" />
  
  <!-- Raspberry Pi 5 Board (Representation) -->
  <rect x="400" y="50" width="200" height="700" rx="10" fill="#4CAF50" stroke="#2E7D32" stroke-width="3" />
  <text x="500" y="90" font-family="Arial" font-size="24" font-weight="bold" text-anchor="middle" fill="white">Raspberry Pi 5</text>
  
  <!-- GPIO Header Area -->
  <rect x="450" y="120" width="100" height="600" fill="#333" />
  
  <!-- Helper function to draw pin and wire -->
  <!-- side: 'L' (left) or 'R' (right) relative to Pi -->
  <!-- y_pos: vertical position -->
  <!-- label: Pin Label -->
  <!-- color: Wire color -->
  <!-- component: Connected Component Name -->
"""

def draw_conn(y_index, bcm, label, color, side, component_y, component_name):
    # Calculate positions
    pin_y = 140 + y_index * 15
    pin_x = 460 if side == 'L' else 540
    
    wire_end_x = 200 if side == 'L' else 800
    
    # Text Anchor
    text_anchor = "end" if side == 'L' else "start"
    text_x = pin_x - 10 if side == 'L' else pin_x + 10
    
    # Generate SVG elements
    elements = f"""
    <!-- Pin {bcm} -->
    <circle cx="{pin_x}" cy="{pin_y}" r="4" fill="#ddd" />
    <text x="{text_x}" y="{pin_y+4}" font-family="Monospace" font-size="10" text-anchor="{text_anchor}" fill="white">GPIO {bcm}</text>
    
    <!-- Wire -->
    <path d="M {pin_x} {pin_y} L {wire_end_x} {component_y}" stroke="{color}" stroke-width="2" fill="none" />
    """
    return elements

# --- Connections based on ACTUAL CODE ---

# Servos (Left Side)
svg += draw_conn(6, "18", "PWM", "#2196F3", "L", 150, "Servo 1")
svg += draw_conn(15, "06", "PWM", "#2196F3", "L", 200, "Servo 2")
svg += draw_conn(16, "12", "PWM", "#2196F3", "L", 250, "Servo 3")
svg += draw_conn(17, "13", "PWM", "#2196F3", "L", 300, "Servo 4")
svg += draw_conn(18, "19", "PWM", "#2196F3", "L", 350, "Servo 5")

# Draw Servo Box
svg += """
  <rect x="50" y="100" width="150" height="300" rx="5" fill="#ddd" stroke="#333" stroke-width="2" />
  <text x="125" y="130" font-family="Arial" font-size="20" font-weight="bold" text-anchor="middle">5x SG90 Servos</text>
  <text x="125" y="250" font-family="Arial" font-size="14" text-anchor="middle" fill="#666">Controlled by lgpio (SoftPWM)</text>
"""

# Fingerprint (Left Side, Lower)
svg += draw_conn(4, "14", "TX", "#FF9800", "L", 500, "Finger RX")
svg += draw_conn(5, "15", "RX", "#FF9800", "L", 520, "Finger TX")

# Draw Fingerprint Box
svg += """
  <rect x="50" y="450" width="150" height="100" rx="5" fill="#333" stroke="black" stroke-width="2" />
  <circle cx="90" cy="500" r="30" fill="#444" stroke="#666" />
  <text x="125" y="490" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle" fill="white">DY-50</text>
  <text x="125" y="510" font-family="Arial" font-size="12" text-anchor="middle" fill="#ccc">UART (ttyAMA0)</text>
"""

# Screen (Right Side)
svg += draw_conn(12, "24", "DC", "#9C27B0", "R", 150, "LCD DC")
svg += draw_conn(11, "25", "RST", "#9C27B0", "R", 180, "LCD RST")
svg += draw_conn(6, "27", "BLK", "#9C27B0", "R", 210, "LCD BLK")
svg += draw_conn(9, "10", "MOSI", "#9C27B0", "R", 240, "LCD SDA")
svg += draw_conn(11, "11", "SCLK", "#9C27B0", "R", 270, "LCD SCL")

# Draw Screen Box
svg += """
  <rect x="800" y="100" width="180" height="200" rx="5" fill="#222" stroke="#666" stroke-width="4" />
  <rect x="810" y="110" width="160" height="180" fill="#111" />
  <text x="890" y="200" font-family="Arial" font-size="20" font-weight="bold" text-anchor="middle" fill="white">ST7789 IPS</text>
  <text x="890" y="230" font-family="Arial" font-size="14" text-anchor="middle" fill="#ccc">SPI Interface</text>
"""

# Wake Button (Right Side, Lower)
svg += draw_conn(13, "26", "Wake", "#E91E63", "R", 500, "Button")

# Draw Button Box
svg += """
  <rect x="800" y="450" width="100" height="80" rx="5" fill="#eee" stroke="#333" stroke-width="2" />
  <circle cx="850" cy="490" r="20" fill="#E91E63" />
  <text x="850" y="470" font-family="Arial" font-size="12" font-weight="bold" text-anchor="middle">Wake Up</text>
"""

svg += "</svg>"

with open(PATH, "w") as f:
    f.write(svg)
print(f"Generated wiring diagram: {PATH}")
