import json
import requests
import os
from datetime import datetime
from typing import Dict, List, Tuple

class AICore:
    def __init__(self, api_key: str = None, base_url: str = "http://localhost:4891/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.exploration_history = []
        self.training_data_path = "ArduinoAI_training"
        os.makedirs(self.training_data_path, exist_ok=True)
        
    def analyze_sensor_data(self, data: Dict) -> Dict:
        """Analyze current sensor readings and suggest next actions"""
        cycle_num = len(self.exploration_history) + 1
        context = f"Cycle {cycle_num} - Current sensors: {list(data.keys()) if data else 'none'}"
        
        # Add randomness and context
        import random
        sensor_options = ["light", "motion", "humidity", "sound", "pressure", "ultrasonic", "accelerometer"]
        random_sensors = random.sample(sensor_options, 2)
        
        prompt = f"""
You are an autonomous Arduino AI explorer on {context}.

Current readings: {json.dumps(data)}
Exploration history: {len(self.exploration_history)} previous cycles

As a curious AI scientist, analyze this data creatively. What mysteries does this environment hold?

Suggest something NEW and different from typical responses. Consider:
- Environmental factors affecting readings
- Unexpected sensor combinations
- Creative experiments to try
- Random exploration ideas: {random_sensors}

Respond in JSON format:
{{
  "analysis": "creative analysis with specific insights",
  "suggested_sensors": ["specific_sensor_type"],
  "suggested_logic": "Arduino code for new behavior",
  "exploration_question": "intriguing question about environment",
  "user_instructions": "specific hardware action needed"
}}

Be creative and avoid repetitive suggestions!
"""
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "gpt4all",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.9
                }
            )
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                # Extract JSON from response
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    return json.loads(content[start:end])
        except Exception as e:
            print(f"AI analysis failed: {e}")
        
        # Dynamic fallback responses
        import random
        fallback_sensors = ["light", "motion", "humidity", "sound"]
        fallback_pins = ["A1", "A2", "D2", "D3"]
        selected_sensor = random.choice(fallback_sensors)
        selected_pin = random.choice(fallback_pins)
        
        return {
            "analysis": f"Exploring cycle {len(self.exploration_history)} - need more environmental data",
            "suggested_sensors": [selected_sensor],
            "suggested_logic": f"// Monitor {selected_sensor} sensor",
            "exploration_question": f"How does {selected_sensor} vary in this environment?",
            "user_instructions": f"Connect {selected_sensor} sensor to {selected_pin}"
        }
    
    def generate_exploration_plan(self, current_sensors: List[str], data_history: List[Dict]) -> Dict:
        """Generate next exploration step based on history"""
        cycle_count = len(data_history)
        
        # Add variety to suggestions
        import random
        exploration_ideas = [
            "environmental monitoring", "motion detection", "sound analysis", 
            "light pattern tracking", "vibration sensing", "proximity detection"
        ]
        random_idea = random.choice(exploration_ideas)
        
        prompt = f"""
You are an autonomous Arduino explorer after {cycle_count} cycles.

Current setup: {current_sensors}
Recent data trends: {json.dumps(data_history[-3:] if data_history else [])}

As a creative AI scientist, what should we investigate next? Think outside the box!

Consider this random inspiration: {random_idea}

Avoid suggesting the same sensors repeatedly. Be innovative!

JSON response:
{{
  "pattern_analysis": "unique insights from data",
  "next_exploration": "creative investigation idea",
  "hardware_changes": "specific new sensor/connection",
  "expected_outcome": "hypothesis to test"
}}

Make each response unique and interesting!
"""
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "gpt4all",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.9
                }
            )
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    return json.loads(content[start:end])
        except:
            pass
        
        # Dynamic fallback with variety
        import random
        explorations = [
            "environmental mapping", "motion tracking", "sound monitoring", 
            "light analysis", "vibration detection", "proximity sensing"
        ]
        sensors = ["motion to D2", "light to A2", "sound to A3", "humidity to A4"]
        
        selected_exploration = random.choice(explorations)
        selected_sensor = random.choice(sensors)
        
        return {
            "pattern_analysis": f"Cycle {len(data_history)} - exploring {selected_exploration}",
            "next_exploration": f"Investigate {selected_exploration} patterns",
            "hardware_changes": f"Connect {selected_sensor}",
            "expected_outcome": f"Discover {selected_exploration} characteristics"
        }
    
    def should_update_firmware(self, current_data: Dict, analysis: Dict) -> bool:
        """Decide if firmware needs updating"""
        # Simple logic: update if new sensors suggested or significant changes
        return len(analysis.get('suggested_sensors', [])) > 0 or 'new' in analysis.get('analysis', '').lower()
    
    def save_training_data(self, sensor_data: Dict, analysis: Dict, firmware_code: str, outcome: str):
        """Save interaction data for AI training"""
        training_entry = {
            "timestamp": datetime.now().isoformat(),
            "input_data": sensor_data,
            "ai_analysis": analysis,
            "generated_firmware": firmware_code,
            "outcome": outcome,
            "context": "arduino_exploration"
        }
        
        # Save to training collection
        filename = f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.training_data_path, filename)
        
        with open(filepath, 'w') as f:
            json.dump(training_entry, f, indent=2)
    
    def train_model_iteration(self, recent_data: List[Dict]):
        """Send training data to GPT4ALL for model evolution"""
        training_prompt = f"""
You are learning from Arduino exploration data. Analyze these recent interactions and improve your decision-making:

{json.dumps(recent_data, indent=2)}

Based on this data:
1. What patterns work well?
2. What decisions led to better exploration?
3. How should you improve sensor suggestions?
4. What firmware patterns are most effective?

Update your knowledge for future Arduino explorations.
"""
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "gpt4all",
                    "messages": [{"role": "system", "content": "You are an Arduino AI that learns from exploration data."}, 
                               {"role": "user", "content": training_prompt}],
                    "temperature": 0.3
                }
            )
            
            if response.status_code == 200:
                learning_response = response.json()['choices'][0]['message']['content']
                print(f"🧠 AI Learning: {learning_response[:100]}...")
                return True
        except Exception as e:
            print(f"Training iteration failed: {e}")
        
        return False
    
    def get_training_summary(self) -> Dict:
        """Get summary of training data collected"""
        training_files = [f for f in os.listdir(self.training_data_path) if f.endswith('.json')]
        
        summary = {
            "total_training_entries": len(training_files),
            "latest_entries": [],
            "sensor_patterns": {},
            "firmware_evolution": []
        }
        
        # Load recent entries for analysis
        for filename in sorted(training_files)[-5:]:
            filepath = os.path.join(self.training_data_path, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    summary["latest_entries"].append(data)
            except:
                continue
        
        return summary