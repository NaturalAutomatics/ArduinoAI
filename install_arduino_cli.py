import os
import requests
import zipfile
import subprocess

def install_arduino_cli():
    """Download and install Arduino CLI for Windows"""
    print("Downloading Arduino CLI...")
    
    # Correct Arduino CLI download URL for Windows
    url = "https://github.com/arduino/arduino-cli/releases/download/v0.35.3/arduino-cli_0.35.3_Windows_64bit.zip"
    
    try:
        # Download with proper headers
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        print(f"Downloaded {len(response.content)} bytes")
        
        with open("arduino-cli.zip", "wb") as f:
            f.write(response.content)
        
        # Verify it's a zip file
        if not zipfile.is_zipfile("arduino-cli.zip"):
            print("ERROR: Downloaded file is not a valid zip")
            return
        
        # Extract
        print("Extracting...")
        with zipfile.ZipFile("arduino-cli.zip", 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Clean up
        os.remove("arduino-cli.zip")
        
        # Test if executable works
        if os.path.exists("arduino-cli.exe"):
            print("Testing Arduino CLI...")
            result = subprocess.run("arduino-cli.exe version", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("SUCCESS: Arduino CLI working!")
                
                # Install Arduino AVR core
                print("Installing Arduino AVR core...")
                subprocess.run("arduino-cli.exe core install arduino:avr", shell=True)
                print("SUCCESS: Arduino CLI installed!")
            else:
                print("ERROR: Arduino CLI test failed")
        else:
            print("ERROR: arduino-cli.exe not found after extraction")
        
    except Exception as e:
        print(f"Installation failed: {e}")
        print("Manual install: Download from https://arduino.github.io/arduino-cli/")

def manual_install_instructions():
    """Show manual installation instructions"""
    print("\nManual Arduino CLI Installation:")
    print("1. Go to: https://arduino.github.io/arduino-cli/")
    print("2. Download Windows 64-bit version")
    print("3. Extract arduino-cli.exe to this folder")
    print("4. Run: arduino-cli.exe core install arduino:avr")
    print("\nOR just use the manual upload method in main.py!")

if __name__ == "__main__":
    try:
        install_arduino_cli()
    except:
        print("Auto-install failed")
    manual_install_instructions()