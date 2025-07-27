import json
import requests
from typing import Dict, List, Tuple

class AICore:
    def __init__(self, api_key: str = None, base_url: str = "http://localhost:1234/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.exploration_history = []
        
    def analyze_sensor_data(self, data: Dict) -> Dict:
        """Analyze current sensor readings and suggest next actions"""
        prompt = f"""
Analyze Arduino sensor data: {json.dumps(data)}

Based on this data, suggest:
1. What new sensors to add
2. What connections to change
3. What logic to implement
4. Questions to explore

Respond in JSON format:
{{
  "analysis": "brief analysis",
  "suggested_sensors": ["sensor1", "sensor2"],
  "suggested_logic": "Arduino code snippet",
  "exploration_question": "What should we explore next?",
  "user_instructions": "Tell user what to connect/change"
}}
"""
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "local-model",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
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
        
        # Fallback response
        return {
            "analysis": "No data received",
            "suggested_sensors": ["temperature"],
            "suggested_logic": "// Basic sensor reading",
            "exploration_question": "Let's start with basic sensors",
            "user_instructions": "Connect a temperature sensor to A0"
        }
    
    def generate_exploration_plan(self, current_sensors: List[str], data_history: List[Dict]) -> Dict:
        """Generate next exploration step based on history"""
        prompt = f"""
Current sensors: {current_sensors}
Recent data: {json.dumps(data_history[-5:] if data_history else [])}

Generate next exploration step:
1. What patterns do you see?
2. What should we explore next?
3. What hardware changes are needed?

JSON response format:
{{
  "pattern_analysis": "what patterns found",
  "next_exploration": "specific next step",
  "hardware_changes": "what user should connect/disconnect",
  "expected_outcome": "what we expect to learn"
}}
"""
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "local-model",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8
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
        
        return {
            "pattern_analysis": "Collecting initial data",
            "next_exploration": "Add more sensors for environmental monitoring",
            "hardware_changes": "Connect light sensor to A1",
            "expected_outcome": "Better understanding of environment"
        }
    
    def should_update_firmware(self, current_data: Dict, analysis: Dict) -> bool:
        """Decide if firmware needs updating"""
        # Simple logic: update if new sensors suggested or significant changes
        return len(analysis.get('suggested_sensors', [])) > 0 or 'new' in analysis.get('analysis', '').lower()