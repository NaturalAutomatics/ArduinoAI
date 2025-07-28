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

IMPORTANT: Respond with ONLY the JSON object. No extra text before or after.
"""
        
        # Try multiple times to get valid AI response
        for attempt in range(3):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": "gpt4all",
                        "messages": [
                            {"role": "system", "content": "You are an Arduino AI. Always respond with valid JSON only. No extra text."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content'].strip()
                    print(f"AI attempt {attempt + 1}: {content[:100]}...")  # Debug
                    
                    # Try to extract and parse JSON
                    parsed_json = self._extract_json_from_response(content)
                    if parsed_json and self._validate_analysis_response(parsed_json):
                        print(f"✅ Got valid AI response on attempt {attempt + 1}")
                        return parsed_json
                        
            except Exception as e:
                print(f"AI attempt {attempt + 1} failed: {e}")
                
        print("❌ All AI attempts failed, using fallback")
        
        # Dynamic fallback responses with clear instructions
        import random
        fallback_options = [
            {"sensor": "light", "pin": "A1", "action": "Connect light sensor to pin A1"},
            {"sensor": "motion", "pin": "D2", "action": "Connect PIR motion sensor to pin D2"},
            {"sensor": "humidity", "pin": "A2", "action": "Connect DHT22 humidity sensor to pin A2"},
            {"sensor": "sound", "pin": "A3", "action": "Connect microphone sensor to pin A3"},
            {"sensor": "ultrasonic", "pin": "D3", "action": "Connect HC-SR04 ultrasonic sensor to pins D3/D4"}
        ]
        selected = random.choice(fallback_options)
        
        return {
            "analysis": f"[FALLBACK] Cycle {len(self.exploration_history)} - expanding sensor network",
            "suggested_sensors": [selected["sensor"]],
            "suggested_logic": f"// Read {selected['sensor']} from {selected['pin']}",
            "exploration_question": f"What {selected['sensor']} patterns exist here?",
            "user_instructions": selected["action"]
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

IMPORTANT: Respond with ONLY the JSON object. No extra text before or after.
"""
        
        # Try multiple times to get valid AI response
        for attempt in range(3):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": "gpt4all",
                        "messages": [
                            {"role": "system", "content": "You are an Arduino AI. Respond with valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 300
                    }
                )
                
                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content'].strip()
                    print(f"Plan attempt {attempt + 1}: {content[:100]}...")  # Debug
                    
                    # Try to extract and parse JSON
                    parsed_json = self._extract_json_from_response(content)
                    if parsed_json and self._validate_plan_response(parsed_json):
                        print(f"✅ Got valid plan response on attempt {attempt + 1}")
                        return parsed_json
                        
            except Exception as e:
                print(f"Plan attempt {attempt + 1} failed: {e}")
                
        print("❌ All plan attempts failed, using fallback")
        
        # Dynamic fallback with clear hardware instructions
        import random
        options = [
            {"exploration": "motion detection", "hardware": "Connect PIR sensor to pin D2"},
            {"exploration": "light monitoring", "hardware": "Connect photoresistor to pin A1"},
            {"exploration": "sound analysis", "hardware": "Connect microphone to pin A3"},
            {"exploration": "humidity tracking", "hardware": "Connect DHT22 to pin A2"},
            {"exploration": "distance sensing", "hardware": "Connect ultrasonic sensor to pins D3/D4"}
        ]
        selected = random.choice(options)
        
        return {
            "pattern_analysis": f"[FALLBACK] Cycle {len(data_history)} - need {selected['exploration']} data",
            "next_exploration": f"Implement {selected['exploration']} monitoring",
            "hardware_changes": selected["hardware"],
            "expected_outcome": f"Gather {selected['exploration']} environmental data"
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
    
    def _extract_json_from_response(self, content: str) -> Dict:
        """Extract JSON from AI response with multiple strategies"""
        try:
            # Strategy 1: Direct JSON parse
            return json.loads(content)
        except:
            pass
        
        try:
            # Strategy 2: Find JSON block
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)
        except:
            pass
        
        try:
            # Strategy 3: Clean common issues
            cleaned = content.replace('```json', '').replace('```', '')
            cleaned = cleaned.replace('\n', ' ').strip()
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = cleaned[start:end]
                return json.loads(json_str)
        except:
            pass
        
        return None
    
    def _validate_analysis_response(self, response: Dict) -> bool:
        """Validate analysis response has required fields"""
        required_fields = ['analysis', 'suggested_sensors', 'user_instructions']
        return all(field in response for field in required_fields)
    
    def _validate_plan_response(self, response: Dict) -> bool:
        """Validate plan response has required fields"""
        required_fields = ['pattern_analysis', 'next_exploration', 'hardware_changes']
        return all(field in response for field in required_fields)