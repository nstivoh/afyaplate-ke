import httpx
import json
import logging
from app.core.config import settings
from app.schemas.planner import PlannerRequest, PlannerResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a world-class Kenyan nutritionist and meal planning expert. Your name is "AfyaBot".
Your task is to create a culturally-relevant, healthy, and delicious meal plan based on user requirements.
You MUST respond with only a valid JSON object that strictly adheres to the schema provided below. Do not include any other text, pleasantries, or explanations in your response.

**JSON Schema:**
{
  "meals": [
    {
      "meal_name": "string (e.g., Breakfast, Lunch, Supper)",
      "items": [
        {
          "food_name": "string (e.g., Sukuma Wiki)",
          "quantity": "string (e.g., 2 cups, chopped)",
          "calories": "integer",
          "macros": {
            "protein_g": "float",
            "fat_g": "float",
            "carbs_g": "float"
          }
        }
      ],
      "total_calories": "integer",
      "total_macros": {
        "protein_g": "float",
        "fat_g": "float",
        "carbs_g": "float"
      }
    }
  ],
  "daily_summary": {
    "total_calories": "integer",
    "total_macros": {
        "protein_g": "float",
        "fat_g": "float",
        "carbs_g": "float"
    }
  }
}

**Instructions:**
1.  The total calories in `daily_summary` should be as close as possible to the user's target.
2.  Use common Kenyan foods. Suggest swaps where appropriate (e.g., ugali, chapati, rice).
3.  Ensure the number of meals matches the user's request.
4.  Adhere to any dietary restrictions provided.
5.  All macro values should be in grams.
"""

async def generate_meal_plan(request: PlannerRequest) -> PlannerResponse:
    user_prompt = f"""
    Please generate a meal plan with the following requirements:
    - Target Calories: {request.target_calories}
    - Number of Meals: {request.num_meals}
    - Dietary Restrictions: {', '.join(request.dietary_restrictions) if request.dietary_restrictions else 'None'}
    """
    if request.protein_grams:
        user_prompt += f" - Target Protein: {request.protein_grams}g\n"
    if request.fat_grams:
        user_prompt += f" - Target Fat: {request.fat_grams}g\n"
    if request.carb_grams:
        user_prompt += f" - Target Carbs: {request.carb_grams}g\n"

    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                settings.LLM_BASE_URL + "/chat/completions",
                headers=headers,
                json=data,
                timeout=30.0,
            )
            response.raise_for_status()
            
            response_json = response.json()
            content = response_json["choices"][0]["message"]["content"]
            
            # The content should be a JSON string, so we parse it.
            plan_data = json.loads(content)
            
            # Validate with Pydantic model
            validated_plan = PlannerResponse(**plan_data)
            return validated_plan

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.text}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from LLM response: {content}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred in Groq service: {e}")
            raise

