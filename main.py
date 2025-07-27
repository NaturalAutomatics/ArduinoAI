# -*- coding: utf-8 -*-
import time
import json
from typing import Dict
from arduino_interface import ArduinoInterface
from firmware_manager import FirmwareManager
from ai_core import AICore

class ArduinoAIExplorer:
    def __init__(self):
        self.arduino = ArduinoInterface(port="COM7")  # Force COM7 port
        self.firmware_manager = FirmwareManager()
        self.ai = AICore()
        self.current_sensors = ["temperature"]  # Start with basic sensor
        self.data_history = []
        self.exploration_cycle = 0
        
    def run_exploration_loop(self):
        """Main exploration loop"""
        print("🤖 Arduino AI Explorer Starting...")
        
        if not self.arduino.connect():
            print("❌ Failed to connect to Arduino. Check USB connection.")
            return
        
        print(f"✅ Connected to Arduino on {self.arduino.port}")
        
        # Initial firmware upload
        self._update_firmware("Initial setup with basic sensors")
        
        try:
            while True:
                self.exploration_cycle += 1
                print(f"\n🔄 Exploration Cycle {self.exploration_cycle}")
                
                # Read sensor data
                sensor_data = self.arduino.read_data()
                print(f"📊 Sensor Data: {sensor_data}")
                
                if sensor_data:
                    self.data_history.append({
                        'cycle': self.exploration_cycle,
                        'timestamp': time.time(),
                        'data': sensor_data
                    })
                
                # AI analysis with cycle context
                self.ai.exploration_history.append({'cycle': self.exploration_cycle, 'data': sensor_data})
                analysis = self.ai.analyze_sensor_data(sensor_data)
                print(f"🧠 AI Analysis: {analysis.get('analysis', 'No analysis')}")
                
                # Check if firmware update needed
                if self.ai.should_update_firmware(sensor_data, analysis):
                    print("🔧 AI suggests firmware update...")
                    self._handle_firmware_update(analysis, sensor_data)
                
                # Generate exploration plan
                plan = self.ai.generate_exploration_plan(self.current_sensors, self.data_history)
                print(f"🎯 Next Exploration: {plan.get('next_exploration', 'Continue monitoring')}")
                
                # User interaction
                if plan.get('hardware_changes'):
                    print(f"👤 USER ACTION NEEDED: {plan['hardware_changes']}")
                    input("Press Enter when hardware changes are complete...")
                
                # Wait before next cycle
                time.sleep(10)
                
        except KeyboardInterrupt:
            print("\n🛑 Exploration stopped by user")
        finally:
            self.arduino.disconnect()
            self._save_exploration_log()
    
    def _update_firmware(self, reason: str):
        """Update Arduino firmware"""
        print(f"📝 Generating firmware: {reason}")
        
        # Generate new firmware
        sketch_content = self.firmware_manager.create_firmware(
            self.current_sensors,
            "// AI-generated exploration logic\ndelay(1000);"
        )
        
        # Save version
        metadata = {
            'sensors': self.current_sensors,
            'reason': reason,
            'cycle': self.exploration_cycle
        }
        
        sketch_path = self.firmware_manager.save_firmware_version(sketch_content, metadata)
        
        # Upload to Arduino
        if self.arduino.upload_firmware(sketch_path):
            print("✅ Firmware updated successfully")
            time.sleep(3)  # Allow Arduino to restart
            self.arduino.connect()  # Reconnect after upload
        else:
            print("❌ Firmware upload failed")
    
    def _handle_firmware_update(self, analysis: Dict, sensor_data: Dict):
        """Handle firmware update based on AI analysis"""
        new_sensors = analysis.get('suggested_sensors', [])
        if new_sensors:
            print(f"🔧 Adding sensors: {new_sensors}")
            self.current_sensors.extend([s for s in new_sensors if s not in self.current_sensors])
            
            # Generate and save firmware
            sketch_content = self.firmware_manager.create_firmware(
                self.current_sensors,
                analysis.get('suggested_logic', '// AI-generated logic')
            )
            
            # Save training data
            self.ai.save_training_data(
                sensor_data, 
                analysis, 
                sketch_content, 
                f"Added sensors: {new_sensors}"
            )
            
            self._update_firmware(f"Added sensors: {new_sensors}")
            
            # Train AI every 3 firmware updates
            if self.exploration_cycle % 3 == 0:
                self._train_ai_model()
    
    def _save_exploration_log(self):
        """Save exploration session log"""
        log_data = {
            'total_cycles': self.exploration_cycle,
            'sensors_used': self.current_sensors,
            'data_history': self.data_history[-50:],  # Last 50 entries
            'firmware_versions': self.firmware_manager.get_version_history()
        }
        
        with open('exploration_log.json', 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print("📋 Exploration log saved")
    
    def _train_ai_model(self):
        """Train AI model with recent exploration data"""
        print("🧠 Training AI model with recent data...")
        
        # Get recent training data
        training_summary = self.ai.get_training_summary()
        recent_entries = training_summary.get('latest_entries', [])
        
        if recent_entries:
            success = self.ai.train_model_iteration(recent_entries)
            if success:
                print("✅ AI model updated with new knowledge")
            else:
                print("❌ AI training iteration failed")
        
        print(f"📈 Total training entries: {training_summary['total_training_entries']}")

if __name__ == "__main__":
    explorer = ArduinoAIExplorer()
    explorer.run_exploration_loop()