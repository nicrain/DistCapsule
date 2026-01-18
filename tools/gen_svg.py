import os

IMAGES = [
    ("docs/slides/pic/system_architecture.svg", "SYSTEM ARCHITECTURE", "(App -> API -> Core)"),
    ("docs/slides/pic/app_login.svg", "APP LOGIN SCREEN", "(Wi-Fi Button)"),
    ("docs/slides/pic/app_dashboard.svg", "APP DASHBOARD", "(Green/Yellow Status)"),
    ("docs/slides/pic/app_admin.svg", "ADMIN PANEL", "(Select User & Actions)"),
    ("docs/slides/pic/hardware_wiring.svg", "HARDWARE WIRING", "(Pi 5 + Servos + Screen)"),
    ("docs/slides/pic/ips_ui_matrix.svg", "IPS SCREEN UI MATRIX", "(Idle / Countdown / Error)"),
    ("docs/slides/pic/3d_render.svg", "3D RENDER / PHOTO", "(OpenSCAD Design)")
]

def create_svg(path, title, subtitle):
    # Create directory
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    svg_content = f"""<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="100%" height="100%" fill="white" stroke="black" stroke-width="10"/>
  
  <!-- Cross pattern -->
  <line x1="0" y1="0" x2="800" y2="600" stroke="#ddd" stroke-width="2"/>
  <line x1="800" y1="0" x2="0" y2="600" stroke="#ddd" stroke-width="2"/>
  
  <!-- Text -->
  <text x="50%" y="40%" font-family="Arial" font-size="40" font-weight="bold" text-anchor="middle" fill="black">{title}</text>
  <text x="50%" y="50%" font-family="Arial" font-size="30" text-anchor="middle" fill="#666">{subtitle}</text>
  <text x="50%" y="90%" font-family="Monospace" font-size="20" text-anchor="middle" fill="#aaa">{os.path.basename(path)}</text>
</svg>"""

    with open(path, "w") as f:
        f.write(svg_content)
    print(f"Generated SVG: {path}")

if __name__ == "__main__":
    for path, title, sub in IMAGES:
        create_svg(path, title, sub)
