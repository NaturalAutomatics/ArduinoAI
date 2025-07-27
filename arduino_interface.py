import serial
import serial.tools.list_ports
import subprocess
import os
import time
from typing import Optional, List, Dict

class ArduinoInterface:
    def __init__(self, port: Optional[str] = None, baudrate: int = 9600):
        self.port = port or self._find_arduino_port()
        self.baudrate = baudrate
        self.connection = None
        print(f"Using Arduino port: {self.port}")
        
    def _find_arduino_port(self) -> Optional[str]:
        """Auto-detect Arduino USB port"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'Arduino' in port.description or 'CH340' in port.description or 'USB' in port.description:
                return port.device
        return None
    
    def connect(self) -> bool:
        """Connect to Arduino"""
        try:
            if self.port:
                self.connection = serial.Serial(self.port, self.baudrate, timeout=2)
                time.sleep(2)  # Arduino reset delay
                return True
        except Exception as e:
            print(f"Connection failed: {e}")
        return False
    
    def read_data(self) -> Dict:
        """Read sensor data from Arduino"""
        if not self.connection:
            return {}
        
        try:
            self.connection.write(b'READ\n')
            response = self.connection.readline().decode().strip()
            # Parse JSON-like response from Arduino
            return eval(response) if response else {}
        except:
            return {}
    
    def upload_firmware(self, sketch_path: str) -> bool:
        """Upload new firmware to Arduino"""
        try:
            # Close connection before upload
            if self.connection:
                self.connection.close()
                time.sleep(1)
            
            # Try Arduino CLI first
            if self._try_arduino_cli(sketch_path):
                return True
            
            # Fallback: Manual upload instruction
            print("WARNING: Arduino CLI not found. Manual upload required:")
            sketch_file = self._find_sketch_file(sketch_path)
            print(f"Open this file in Arduino IDE: {sketch_file}")
            print(f"Upload to {self.port} manually")
            
            input("Press Enter after uploading firmware manually...")
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"Upload exception: {e}")
            return False
    
    def _try_arduino_cli(self, sketch_path: str) -> bool:
        """Try using Arduino CLI"""
        try:
            sketch_name = os.path.basename(sketch_path)
            
            print(f"Trying Arduino CLI for: {sketch_name}")
            compile_cmd = f'arduino-cli compile --fqbn arduino:avr:uno "{sketch_path}"'
            compile_result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
            
            if compile_result.returncode != 0:
                return False
            
            upload_cmd = f'arduino-cli upload -p {self.port} --fqbn arduino:avr:uno "{sketch_path}"'
            upload_result = subprocess.run(upload_cmd, shell=True, capture_output=True, text=True)
            
            return upload_result.returncode == 0
            
        except:
            return False
    
    def _find_sketch_file(self, sketch_path: str) -> str:
        """Find the .ino file in sketch directory"""
        if os.path.isdir(sketch_path):
            for file in os.listdir(sketch_path):
                if file.endswith('.ino'):
                    return os.path.join(sketch_path, file)
        return sketch_path
    
    def disconnect(self):
        """Close connection"""
        if self.connection:
            self.connection.close()