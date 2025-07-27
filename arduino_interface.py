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
            cmd = f'arduino-cli compile --fqbn arduino:avr:uno {sketch_path}'
            subprocess.run(cmd, shell=True, check=True)
            
            cmd = f'arduino-cli upload -p {self.port} --fqbn arduino:avr:uno {sketch_path}'
            result = subprocess.run(cmd, shell=True, check=True)
            
            time.sleep(3)  # Upload delay
            return result.returncode == 0
        except:
            return False
    
    def disconnect(self):
        """Close connection"""
        if self.connection:
            self.connection.close()