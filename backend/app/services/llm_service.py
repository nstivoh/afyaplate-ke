import json
import logging
from google import genai
from google.genai import types
from litellm import acompletion
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

    # Use google-genai for Gemini
    if request.llm_provider.lower() == "gemini":
        try:
            client = genai.Client(api_key=request.llm_api_key)
            model_id = request.llm_model if "gemini" in request.llm_model else "gemini-2.0-pro-exp-02-05"
            
            response = client.models.generate_content(
                model=model_id,
                contents=[user_prompt],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json"
                )
            )
            
            plan_data = json.loads(response.text)
            return PlannerResponse(**plan_data)
            
        except Exception as e:
            logger.error(f"Google GenAI error: {e}")
            raise ValueError(f"Gemini API error: {str(e)}")

    # Fallback/LiteLLM for other providers
    litellm_model = f"{request.llm_provider}/{request.llm_model}"

    try:
        response = await acompletion(
            model=litellm_model,
            api_key=request.llm_api_key,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content
        plan_data = json.loads(content)
        return PlannerResponse(**plan_data)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from LLM response: {content}")
        raise ValueError("The AI model failed to return a valid JSON object.") from e
    except Exception as e:
        logger.error(f"LiteLLM completion error: {e}")
        raise

