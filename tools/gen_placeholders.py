import os
from PIL import Image, ImageDraw, ImageFont

# Define the images to generate (Filename, Description)
IMAGES = [
    ("docs/slides/pic/system_architecture.png", "SYSTEM ARCHITECTURE\n(App -> API -> Core)"),
    ("docs/slides/pic/app_login.png", "APP LOGIN SCREEN\n(Wi-Fi Button)"),
    ("docs/slides/pic/app_dashboard.png", "APP DASHBOARD\n(Green/Yellow Status)"),
    ("docs/slides/pic/app_admin.png", "ADMIN PANEL\n(Select User & Actions)"),
    ("docs/slides/pic/hardware_wiring.png", "HARDWARE WIRING\n(Pi 5 + Servos + Screen)"),
    ("docs/slides/pic/ips_ui_matrix.png", "IPS SCREEN UI MATRIX\n(Idle / Countdown / Error)"),
    ("docs/slides/pic/3d_render.png", "3D RENDER / PHOTO\n(OpenSCAD Design)")
]

def create_placeholder(path, text):
    # Image settings
    width, height = 800, 600
    bg_color = (255, 255, 255) # White
    text_color = (0, 0, 0)     # Black
    
    # Create directory if not exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    img = Image.new('RGB', (width, height), color=bg_color)
    d = ImageDraw.Draw(img)
    
    # Add filename to text
    full_text = f"FILE: {os.path.basename(path)}\n\n{text}"
    
    # Draw text (centered simply)
    # Note: Default font is used to avoid dependency issues
    d.text((50, 250), full_text, fill=text_color)
    
    # Add a border
    d.rectangle([0, 0, width-1, height-1], outline=text_color, width=5)
    
    img.save(path)
    print(f"Generated: {path}")

if __name__ == "__main__":
    print("Generating placeholder images...")
    try:
        for path, desc in IMAGES:
            create_placeholder(path, desc)
        print("Done.")
    except ImportError:
        print("Error: PIL (Pillow) library is not installed.")
        print("Please run: pip install Pillow")
    except Exception as e:
        print(f"An error occurred: {e}")
