import os
import json
import shutil
from datetime import datetime
from typing import Dict, List

class FirmwareManager:
    def __init__(self, base_path: str = "firmware_versions"):
        self.base_path = base_path
        self.current_version = 0
        os.makedirs(base_path, exist_ok=True)
        self._load_version_info()
    
    def _load_version_info(self):
        """Load version tracking info"""
        info_file = os.path.join(self.base_path, "version_info.json")
        if os.path.exists(info_file):
            with open(info_file, 'r') as f:
                data = json.load(f)
                self.current_version = data.get('current_version', 0)
    
    def _save_version_info(self):
        """Save version tracking info"""
        info_file = os.path.join(self.base_path, "version_info.json")
        with open(info_file, 'w') as f:
            json.dump({'current_version': self.current_version}, f)
    
    def create_firmware(self, sensors: List[str], logic: str) -> str:
        """Generate Arduino sketch based on sensors and logic"""
        # Clean logic to prevent syntax errors
        clean_logic = logic.strip() if logic else "// No additional logic"
        
        sketch = f'''void setup() {{
  Serial.begin(9600);
{self._generate_setup_code(sensors)}
}}

void loop() {{
  if (Serial.available() && Serial.readString().indexOf("READ") >= 0) {{
    Serial.print("{{");
{self._generate_read_code(sensors)}
    Serial.println("}}");
  }}
  
  {clean_logic}
  
  delay(100);
}}

{self._generate_helper_functions(sensors)}'''
        return sketch
    
    def _generate_setup_code(self, sensors: List[str]) -> str:
        """Generate setup code for sensors"""
        setup_lines = []
        for sensor in sensors:
            if sensor == "temperature":
                setup_lines.append("  // Temperature sensor on A0")
            elif sensor == "light":
                setup_lines.append("  // Light sensor on A1")
            elif sensor == "motion":
                setup_lines.append("  pinMode(2, INPUT); // Motion sensor")
            elif sensor == "humidity":
                setup_lines.append("  // Humidity sensor on A2")
            elif sensor == "sound":
                setup_lines.append("  // Sound sensor on A3")
        return "\n".join(setup_lines) if setup_lines else "  // No sensors configured"
    
    def _generate_read_code(self, sensors: List[str]) -> str:
        """Generate sensor reading code"""
        if not sensors:
            return '    Serial.print("\\"status\\":\\"no_sensors\\"");'
        
        read_lines = []
        for i, sensor in enumerate(sensors):
            comma = "," if i < len(sensors) - 1 else ""
            if sensor == "temperature":
                read_lines.append(f'    Serial.print("\\"temp\\":" + String(analogRead(A0)) + "{comma}");')
            elif sensor == "light":
                read_lines.append(f'    Serial.print("\\"light\\":" + String(analogRead(A1)) + "{comma}");')
            elif sensor == "motion":
                read_lines.append(f'    Serial.print("\\"motion\\":" + String(digitalRead(2)) + "{comma}");')
            elif sensor == "humidity":
                read_lines.append(f'    Serial.print("\\"humidity\\":" + String(analogRead(A2)) + "{comma}");')
            elif sensor == "sound":
                read_lines.append(f'    Serial.print("\\"sound\\":" + String(analogRead(A3)) + "{comma}");')
        return "\n".join(read_lines)
    
    def _generate_helper_functions(self, sensors: List[str]) -> str:
        """Generate helper functions"""
        return "// Helper functions can be added here"
    
    def save_firmware_version(self, sketch_content: str, metadata: Dict) -> str:
        """Save firmware version with metadata"""
        self.current_version += 1
        version_dir = os.path.join(self.base_path, f"v{self.current_version}")
        os.makedirs(version_dir, exist_ok=True)
        
        # Create sketch directory (Arduino CLI needs directory structure)
        sketch_name = f"sketch_v{self.current_version}"
        sketch_dir = os.path.join(version_dir, sketch_name)
        os.makedirs(sketch_dir, exist_ok=True)
        
        # Save sketch with proper name
        sketch_path = os.path.join(sketch_dir, f"{sketch_name}.ino")
        with open(sketch_path, 'w') as f:
            f.write(sketch_content)
        
        # Save metadata
        metadata['version'] = self.current_version
        metadata['timestamp'] = datetime.now().isoformat()
        
        meta_path = os.path.join(version_dir, "metadata.json")
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self._save_version_info()
        return sketch_dir  # Return directory path for Arduino CLI
    
    def get_version_history(self) -> List[Dict]:
        """Get list of all firmware versions"""
        versions = []
        for i in range(1, self.current_version + 1):
            meta_path = os.path.join(self.base_path, f"v{i}", "metadata.json")
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    versions.append(json.load(f))
        return versions