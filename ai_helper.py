import os
import json
from google import genai

from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

# Load environment
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
def generate_itinerary(destination, duration, budget, interests):
    """Generate a travel itinerary using Google's Gemini API"""
    
    # Create a prompt for the AI
    prompt = f"""
    Create a detailed travel itinerary for a trip to {destination} for {duration} days with a budget of {budget}.
    The traveler is interested in: {interests}.
    
    Format the response as a JSON object with the following structure:
    {{
        "daily_plans": [
            {{
                "day": 1,
                "activities": [
                    {{
                        "time": "Morning",
                        "description": "Activity description",
                        "category": "Activity/Food/Transportation/Accommodation",
                        "estimated_cost": 0
                    }},
                    // More activities for the day
                ]
            }},
            // More days
        ],
        "budget_breakdown": {{
            "Accommodation": 0,
            "Food": 0,
            "Transportation": 0,
            "Activities": 0,
            "Miscellaneous": 0,
            "Total": 0
        }},
        "tips": [
            "Tip 1",
            "Tip 2"
        ]
    }}
    
    Ensure the budget breakdown is realistic and the total matches the sum of all categories.
    Make sure all costs are within the total budget of {budget}.
    Only respond with the JSON object, no additional text.
    """
    
    try:
        # Initialize the Gemini model
        client = genai.Client(api_key=api_key)
        MODEL_ID = "gemini-2.0-flash"
        google_search_tool = Tool(google_search=GoogleSearch())
        # Generate content
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[prompt],
            config=GenerateContentConfig(tools=[google_search_tool], response_modalities=["TEXT"])
        )
        # Extract and parse the JSON response
        response_text = response.text
        
        # Clean up the response if it contains markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
            
        # Parse the JSON
        print(response_text)
        itinerary_data = json.loads(response_text)
        return itinerary_data
    
    except Exception as e:
        print(f"Error generating itinerary: {e}")
        raise Exception(f"Failed to generate itinerary: {str(e)}")
