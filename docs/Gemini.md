# Using the `GeminiClient`

## Overview

The `GeminiClient` is a base class designed to handle all interactions with the Google Gemini API. It is built to be **stateful**, meaning it maintains a single, continuous chat session.

Other services (e.g., `SafeTravelService`, `ItineraryService`) should **inherit** from this class to add specific functionality.

## 1\. Setup

### A. Install Dependencies

Install the required Python packages:

```
pip install -r requirements.txt

```

### B. Configure Environment

The client loads settings from environment variables (via `.env` file).

1.  Copy the example file:

    ```
    cp .env.example .env

    ```

2.  Edit your new `.env` file and add your `GEMINI_API_KEY` from Google AI Studio.

3.  You can also change the `GEMINI_MODEL` if needed.

<!-- end list -->

```
# .env
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-flash-latest

```

## 2\. How It Works

The client is designed to be inherited. You should not instantiate `GeminiClient` directly.

### Core Methods

  * `generate_json(prompt, system_context)`: This is the primary async method you will use. It sends a prompt and expects a JSON string in response, which it automatically parses into a Python dictionary.

  * `generate_text(prompt)`: A simpler async method for when you just need a plain text response.

### Usage Example (Inheritance)

Here is how you create a specific service that uses the client.

```
from typing import List, Dict
from src.infrastructure.ai.gemini_client import GeminiClient
from src.domain.value_objects.coordinate import Coordinate

class SafetyPredictor(GeminiClient):
    """
    Specialized service for safety predictions.
    System instruction is set ONCE in __init__, applies to ALL requests.
    """
    
    def __init__(self):
        # Set system instruction when creating the client
        system_instruction = """
        You are a travel safety expert AI for SafeTravel app.
        
        Your role:
        - Analyze locations and routes for safety risks
        - Consider: crime rates, weather, political stability, health risks
        - Provide safety scores from 0-100 (0=dangerous, 100=very safe)
        - Always respond in valid JSON format
        - Be informative but not alarmist
        - Give practical, actionable advice
        
        IMPORTANT: Always return properly formatted JSON. Never include markdown code blocks in your response.
        """
        
        # Pass to parent class - this applies to ALL requests!
        super().__init__(system_instruction=system_instruction)
    
    async def calculate_safety_score(
        self,
        destination: str,
        waypoints: List[Coordinate],
        time_of_travel: str
    ) -> Dict:
        """Calculate safety score for a route"""
        
        waypoint_str = ", ".join([
            f"({wp.latitude}, {wp.longitude})" for wp in waypoints
        ])
        
        # No need to repeat system context - it's already set!
        prompt = f"""
        Analyze the safety of this travel route:
        
        Destination: {destination}
        Waypoints: {waypoint_str}
        Travel Time: {time_of_travel}
        
        Return this JSON format:
        {{
            "safety_score": <number 0-100>,
            "risk_level": "low|medium|high|critical",
            "main_concerns": ["concern1", "concern2"],
            "recommendations": ["recommendation1", "recommendation2"]
        }}
        """
        
        return await self.generate_json(prompt)
    
    async def predict_dangers(
        self,
        location: Coordinate,
        context: Dict
    ) -> List[Dict]:
        """Predict potential dangers at location"""
        
        prompt = f"""
        Predict potential dangers at this location:
        
        Location: ({location.latitude}, {location.longitude})
        Time: {context.get('time_of_day', 'unknown')}
        Weather: {context.get('weather', 'unknown')}
        Activity: {context.get('activity', 'traveling')}
        
        Return JSON array:
        [
            {{
                "danger_type": "type of danger",
                "likelihood": "low|medium|high",
                "description": "brief description",
                "prevention_tips": ["tip1", "tip2"]
            }}
        ]
        """
        
        result = await self.generate_json(prompt)
        return result if isinstance(result, list) else result.get('dangers', [])


```

## 3\. ⚠️ Important Developer Notes

### A. The Client is STATEFUL (Chat Session)

This class is **stateful**. It creates and holds *one* chat session (`self.chat`) for the lifetime of the object.

  * **Pro:** You can have a continuous conversation. `await client.generate_json("My first question")` followed by `await client.generate_json("A follow-up question")` will have memory of the first question.

  * **Con:** This is **not** suitable for web services where one client instance is shared by multiple users. Each user request should ideally be stateless or have its own client instance.

### B. `system_instruction` is PERMANENT

The `system_instruction` is set **once** when the client object is created (e.g., `travel_service = SafeTravelService()`).

  * It **cannot** be changed for that object.
  * It will apply to **every call** (`generate_json`, `generate_text`) made by that object.
  * This is the correct, intended behavior for defining a "persona." If you need a different persona, you must create a new client object.