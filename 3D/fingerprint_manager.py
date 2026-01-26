import time
import serial
import adafruit_fingerprint

# --- Configuration ---
# UART Connection: Usually /dev/serial0 on Raspberry Pi for GPIO 14/15
# If using a USB-to-Serial adapter, it might be /dev/ttyUSB0
uart = serial.Serial("/dev/serial0", baudrate=57600, timeout=1)

# Initialize Sensor
try:
    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
except Exception as e:
    print(f"Error connecting to sensor: {e}")
    print("Check wiring: Green->TX, White->RX, Red->3.3V, Black->GND")
    exit(1)

def get_fingerprint():
    """Get a fingerprint image, process it, and get a template."""
    print("Waiting for image...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Image taken")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    return True

def get_fingerprint_detail():
    """Get a fingerprint image, process it, and search database."""
    print("Waiting for image...", end="", flush=True)
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Image taken")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching...", end="", flush=True)
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True

def enroll_finger(location):
    """Enroll a finger at the specified location ID."""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print(f"Place finger on sensor (Step 1/2)...", end="", flush=True)
        else:
            print(f"Place SAME finger again (Step 2/2)...", end="", flush=True)

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="", flush=True)
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...", end="", flush=True)
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="", flush=True)
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print(f"Storing model at #{location}...", end="", flush=True)
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Stored")
        return True
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Bad storage location")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

def check_database():
    """List number of fingerprints."""
    if finger.read_templates() != adafruit_fingerprint.OK:
        print("Failed to read templates")
        return
    print(f"--------------------------------")
    print(f"Sensor contains {len(finger.templates)} templates.")
    print(f"Template IDs: {finger.templates}")
    print(f"--------------------------------")

def main_menu():
    while True:
        print("\n--- Fingerprint Manager ---")
        print("1. List stored fingerprints (Check DB)")
        print("2. Enroll new fingerprint")
        print("3. Test Search (Verify Finger)")
        print("4. Delete a fingerprint")
        print("5. Delete ALL fingerprints (Wipe DB)")
        print("q. Quit")
        choice = input("Select option: ")

        if choice == "1":
            check_database()
        
        elif choice == "2":
            check_database()
            try:
                loc = int(input("Enter ID # to save (1-127): "))
                if enroll_finger(loc):
                    print("✅ Enrollment SUCCESS!")
                else:
                    print("❌ Enrollment FAILED.")
            except ValueError:
                print("Invalid number.")

        elif choice == "3":
            print("Waiting for finger...")
            if get_fingerprint_detail():
                print(f"✅ DETECTED! ID #{finger.finger_id} with confidence {finger.confidence}")
            else:
                print("❌ Finger not found in database.")

        elif choice == "4":
            check_database()
            try:
                loc = int(input("Enter ID # to delete: "))
                if finger.delete_model(loc) == adafruit_fingerprint.OK:
                    print("Deleted!")
                else:
                    print("Failed to delete.")
            except ValueError:
                print("Invalid number.")

        elif choice == "5":
            confirm = input("Type 'YES' to wipe entire database: ")
            if confirm == "YES":
                if finger.empty_library() == adafruit_fingerprint.OK:
                    print("Database wiped!")
                else:
                    print("Failed to wipe.")
            else:
                print("Cancelled.")

        elif choice == "q":
            break

if __name__ == "__main__":
    print("Initializing sensor...")
    if finger.read_templates() != adafruit_fingerprint.OK:
        print("Failed to read templates")
    else:
        print(f"Sensor ready. Stored templates: {len(finger.templates)}")
    
    main_menu()
