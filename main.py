# -*- coding: utf-8 -*-
import time
import json
from typing import Dict
from arduino_interface import ArduinoInterface
from firmware_manager import FirmwareManager
from ai_core import AICore
from web_ui import ArduinoWebUI

class ArduinoAIExplorer:
    def __init__(self):
        self.arduino = ArduinoInterface(port="COM7")  # Force COM7 port
        self.firmware_manager = FirmwareManager()
        self.ai = AICore()
        self.current_sensors = ["temperature"]  # Start with basic sensor
        self.data_history = []
        self.exploration_cycle = 0
        
        # Start web UI
        self.web_ui = ArduinoWebUI()
        self.web_ui.set_evolution_callback(self.trigger_evolution_cycle)
        self.web_ui.start_server()
        print("🌐 Web UI started at http://localhost:5000")
        
        # Initialize with basic firmware
        initial_firmware = self.firmware_manager.create_firmware(self.current_sensors, "// Initial firmware")
        self.web_ui.update_firmware_code(initial_firmware)
        
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
                
                # User interaction - show if AI generated or fallback
                if plan.get('hardware_changes'):
                    ai_generated = "[AI]" if "fallback" not in str(plan) else "[FALLBACK]"
                    
                    # Convert complex AI response to readable instruction
                    instruction_text = self._format_instruction(plan['hardware_changes'])
                    print(f"👤 USER ACTION NEEDED {ai_generated}: {instruction_text}")
                    
                    # Update web UI
                    ui_data = {
                        'hardware_changes': instruction_text,
                        'cycle': self.exploration_cycle,
                        'current_sensors': self.current_sensors,
                        'ai_generated': "[AI]" in ai_generated
                    }
                    self.web_ui.update_instruction(ui_data)
                    
                    # Wait for user to complete hardware changes
                    print("🔄 Use the web UI evolution button or press Enter to continue...")
                    input()
                    self.web_ui.clear_instruction()
                    
                    # Stop automatic cycling - wait for manual evolution trigger
                    print("⏸️ Automatic cycling paused. Use web UI to trigger evolution.")
                    while True:
                        time.sleep(5)  # Keep connection alive but don't auto-cycle
                else:
                    # No hardware changes needed, continue monitoring
                    time.sleep(10)
                
        except KeyboardInterrupt:
            print("\n🛑 Exploration stopped by user")
        finally:
            self.arduino.disconnect()
            self._save_exploration_log()
    
    def _update_firmware(self, reason: str):
        """Update Arduino firmware"""
        print(f"📝 Generating firmware: {reason}")
        
        # Generate new firmware with safe logic
        safe_logic = "// AI-generated exploration logic\ndelay(1000);"
        sketch_content = self.firmware_manager.create_firmware(
            self.current_sensors,
            safe_logic
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
            
            # Generate and save firmware with validated logic
            ai_logic = analysis.get('suggested_logic', '// AI-generated logic')
            # Clean AI logic to prevent syntax errors
            safe_logic = self._validate_arduino_logic(ai_logic)
            sketch_content = self.firmware_manager.create_firmware(
                self.current_sensors,
                safe_logic
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
    
    def _validate_arduino_logic(self, logic: str) -> str:
        """Validate and clean AI-generated Arduino logic"""
        if not logic or not isinstance(logic, str):
            return "// No additional logic"
        
        # Remove potentially dangerous or invalid code
        dangerous_keywords = ['#include', 'system(', 'exec(', 'eval(']
        clean_logic = logic
        
        for keyword in dangerous_keywords:
            if keyword in clean_logic:
                clean_logic = "// Unsafe code removed"
                break
        
        # Ensure it's valid C++ comment or code
        if not (clean_logic.strip().startswith('//') or 
                clean_logic.strip().startswith('/*') or
                any(c in clean_logic for c in [';', '{', '}'])):
            clean_logic = f"// {clean_logic}"
        
        return clean_logic
    
    def _format_instruction(self, hardware_changes) -> str:
        """Convert AI response to readable instruction"""
        if isinstance(hardware_changes, str):
            return hardware_changes
        
        if isinstance(hardware_changes, list):
            # Handle list of components
            components = []
            for item in hardware_changes:
                if isinstance(item, dict) and 'type' in item:
                    components.append(item['type'])
                else:
                    components.append(str(item))
            
            if 'ultrasonic' in str(hardware_changes).lower():
                return "Connect HC-SR04 ultrasonic sensor: Trig to D3, Echo to D4, VCC to 5V, GND to GND"
            elif 'motion' in str(hardware_changes).lower() or 'pir' in str(hardware_changes).lower():
                return "Connect PIR motion sensor to pin D2 (VCC to 5V, GND to GND)"
            elif 'light' in str(hardware_changes).lower():
                return "Connect photoresistor to pin A1 with 10kΩ pull-down resistor"
            elif 'humidity' in str(hardware_changes).lower() or 'dht' in str(hardware_changes).lower():
                return "Connect DHT22 humidity sensor to pin A2 (VCC to 5V, GND to GND)"
            elif 'sound' in str(hardware_changes).lower() or 'microphone' in str(hardware_changes).lower():
                return "Connect microphone sensor to pin A3 (VCC to 5V, GND to GND)"
            else:
                return f"Connect components: {', '.join(components)}"
        
        if isinstance(hardware_changes, dict):
            # Handle dict response
            if 'sensor' in hardware_changes:
                sensor_type = str(hardware_changes['sensor']).lower()
                pin = hardware_changes.get('pin', 'A1')
                
                if 'hc-sr04' in sensor_type or 'ultrasonic' in sensor_type:
                    return "Connect HC-SR04 ultrasonic sensor: Trig to D3, Echo to D4, VCC to 5V, GND to GND"
                elif 'pir' in sensor_type or 'motion' in sensor_type:
                    return "Connect PIR motion sensor to pin D2, VCC to 5V, GND to GND"
                elif 'photoresistor' in sensor_type or 'light' in sensor_type:
                    return "Connect photoresistor to pin A1 with 10kΩ resistor to GND"
                elif 'dht' in sensor_type or 'humidity' in sensor_type:
                    return "Connect DHT22 humidity sensor: Data to A2, VCC to 5V, GND to GND"
                elif 'microphone' in sensor_type or 'sound' in sensor_type:
                    return "Connect microphone sensor to pin A3, VCC to 5V, GND to GND"
                else:
                    return f"Connect {hardware_changes['sensor']} sensor to pin {pin}"
            
            if 'type' in hardware_changes:
                sensor_type = hardware_changes['type'].lower()
                if 'ultrasonic' in sensor_type:
                    return "Connect HC-SR04 ultrasonic sensor: Trig to D3, Echo to D4"
                elif 'motion' in sensor_type:
                    return "Connect PIR motion sensor to pin D2"
                elif 'light' in sensor_type:
                    return "Connect photoresistor to pin A1"
                elif 'humidity' in sensor_type:
                    return "Connect DHT22 humidity sensor to pin A2"
                elif 'sound' in sensor_type:
                    return "Connect microphone sensor to pin A3"
        
        # Fallback
        return f"Connect sensor as instructed: {str(hardware_changes)[:100]}"
    
    def trigger_evolution_cycle(self):
        """Trigger complete evolution cycle from web UI"""
        print("🚀 Evolution cycle triggered from web UI!")
        
        # 1. Read current sensor data
        sensor_data = self.arduino.read_data()
        print(f"📊 Real-world data: {sensor_data}")
        
        if sensor_data:
            # 2. Add to history
            self.data_history.append({
                'cycle': self.exploration_cycle,
                'timestamp': time.time(),
                'data': sensor_data
            })
            
            # 3. AI analysis with real data
            self.ai.exploration_history.append({'cycle': self.exploration_cycle, 'data': sensor_data})
            analysis = self.ai.analyze_sensor_data(sensor_data)
            print(f"🧠 AI learned from real data: {analysis.get('analysis', 'No analysis')[:100]}...")
            
            # 4. Train AI with real-world feedback
            self.ai.save_training_data(
                sensor_data, 
                analysis, 
                "Real-world feedback", 
                "Evolution cycle triggered"
            )
            
            # 5. Force AI training with new data
            training_summary = self.ai.get_training_summary()
            recent_entries = training_summary.get('latest_entries', [])
            if recent_entries:
                success = self.ai.train_model_iteration(recent_entries)
                if success:
                    print("✅ AI evolved with real-world data!")
            
            # 6. Generate evolved firmware with AI code evolution
            new_sensors = analysis.get('suggested_sensors', [])
            if new_sensors:
                self.current_sensors.extend([s for s in new_sensors if s not in self.current_sensors])
            
            # Get current firmware for evolution
            current_firmware = self.firmware_manager.create_firmware(
                self.current_sensors,
                "// Current firmware for evolution"
            )
            
            # Ask AI to evolve the firmware code
            print("🧠 Asking AI to evolve firmware code...")
            evolved_firmware = self.ai.evolve_firmware_code(
                current_firmware, 
                self.current_sensors, 
                sensor_data
            )
            
            # Validate evolved firmware
            sketch_content = self._validate_evolved_firmware(evolved_firmware)
            
            # 7. Upload AI-evolved firmware
            metadata = {
                'sensors': self.current_sensors,
                'reason': 'AI-evolved firmware based on real data',
                'cycle': self.exploration_cycle,
                'real_data': sensor_data,
                'ai_evolved': True
            }
            
            sketch_path = self.firmware_manager.save_firmware_version(sketch_content, metadata)
            print(f"💾 Saved AI-evolved firmware v{self.firmware_manager.current_version}")
            
            # Update web UI with new firmware code
            self.web_ui.update_firmware_code(sketch_content)
            
            if self.arduino.upload_firmware(sketch_path):
                print("✅ AI-evolved firmware uploaded successfully!")
                print(f"🚀 Arduino now running AI-optimized code for: {', '.join(self.current_sensors)}")
                time.sleep(3)
                self.arduino.connect()
            else:
                print("❌ AI-evolved firmware upload failed")
            
            # 8. Increment cycle and generate next exploration plan
            self.exploration_cycle += 1
            plan = self.ai.generate_exploration_plan(self.current_sensors, self.data_history)
            if plan.get('hardware_changes'):
                instruction_text = self._format_instruction(plan['hardware_changes'])
                print(f"🎯 Next evolution step: {instruction_text}")
                
                # Update web UI with new instruction
                ui_data = {
                    'hardware_changes': instruction_text,
                    'cycle': self.exploration_cycle,
                    'current_sensors': self.current_sensors,
                    'ai_generated': True
                }
                self.web_ui.update_instruction(ui_data)
        
        else:
            print("❌ No sensor data available for evolution")
    
    def _validate_evolved_firmware(self, evolved_code: str) -> str:
        """Validate and clean AI-evolved firmware"""
        # Basic validation
        if not evolved_code or len(evolved_code) < 50:
            return self.firmware_manager.create_firmware(self.current_sensors, "// Evolution failed")
        
        # Check for required Arduino structure
        if 'void setup()' not in evolved_code or 'void loop()' not in evolved_code:
            return self.firmware_manager.create_firmware(self.current_sensors, "// Invalid structure")
        
        # Remove dangerous code
        dangerous_patterns = ['#include <', 'system(', 'exec(', 'eval(']
        for pattern in dangerous_patterns:
            if pattern in evolved_code:
                print(f"⚠️ Removed dangerous pattern: {pattern}")
                evolved_code = evolved_code.replace(pattern, f"// REMOVED: {pattern}")
        
        # Ensure Serial.begin is present
        if 'Serial.begin(' not in evolved_code:
            evolved_code = evolved_code.replace('void setup() {', 'void setup() {\n  Serial.begin(9600);')
        
        return evolved_code

if __name__ == "__main__":
    explorer = ArduinoAIExplorer()
    explorer.run_exploration_loop()