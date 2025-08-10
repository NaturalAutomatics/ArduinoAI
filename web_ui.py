from flask import Flask, render_template, jsonify
import json
import threading
import webbrowser
from datetime import datetime

class ArduinoWebUI:
    def __init__(self, port=5000):
        self.app = Flask(__name__)
        self.port = port
        self.current_instruction = None
        self.connection_history = []
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('arduino_ui.html')
        
        @self.app.route('/api/current_instruction')
        def get_current_instruction():
            return jsonify(self.current_instruction or {})
        
        @self.app.route('/api/history')
        def get_history():
            return jsonify(self.connection_history[-10:])  # Last 10 instructions
        
        @self.app.route('/api/trigger_evolution', methods=['POST'])
        def trigger_evolution():
            if hasattr(self, 'evolution_callback'):
                self.evolution_callback()
                return jsonify({'status': 'evolution_triggered'})
            return jsonify({'status': 'no_callback'})
        
        @self.app.route('/api/firmware_code')
        def get_firmware_code():
            return jsonify(getattr(self, 'current_firmware_code', ''))
    
    def update_instruction(self, instruction_data):
        """Update current instruction for user"""
        self.current_instruction = {
            'timestamp': datetime.now().isoformat(),
            'instruction': instruction_data.get('hardware_changes', ''),
            'cycle': instruction_data.get('cycle', 0),
            'sensors': instruction_data.get('current_sensors', []),
            'ai_generated': '[AI]' in str(instruction_data)
        }
        
        # Add to history
        self.connection_history.append(self.current_instruction.copy())
        
    def start_server(self):
        """Start web server in background thread"""
        def run_server():
            self.app.run(host='localhost', port=self.port, debug=False, use_reloader=False)
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        
        # Open browser
        webbrowser.open(f'http://localhost:{self.port}')
        
    def clear_instruction(self):
        """Clear current instruction when completed"""
        if self.current_instruction:
            self.current_instruction['completed'] = True
    
    def set_evolution_callback(self, callback):
        """Set callback for evolution button"""
        self.evolution_callback = callback
    
    def update_firmware_code(self, firmware_code: str):
        """Update current firmware code for display"""
        self.current_firmware_code = firmware_code