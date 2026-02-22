# filepath: core/llm_meal_planner.py
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Optional, Tuple, Any

from core.planner_backends import (
    get_backend, 
    MealPlannerBackend, 
    PlannerConnectionError, 
    PlannerModelNotFound,
    PlannerResponseValidationError
)

# --- Pydantic Models for Response Validation (could be moved to a models.py) ---
class MealItem(BaseModel):
    name: str = Field(..., description="Name of the meal, e.g., 'Ugali with Sukuma Wiki and Beef Stew'")
    ingredients: List[str] = Field(..., description="List of ingredients for the meal.")
    nutrients: Dict[str, float] = Field({}, description="Estimated nutrients. E.g., {'calories': 550, 'protein': 30}.")
    cost: Optional[int] = Field(None, description="Estimated cost in KSh.")

class Meals(BaseModel):
    breakfast: MealItem
    lunch: MealItem
    dinner: MealItem
    snacks: Optional[MealItem] = None

class DailyPlan(BaseModel):
    day: int
    meals: Meals
    daily_totals: Dict[str, float] = Field({}, description="Summary of daily totals. E.g., {'calories': 1800, 'protein': 90}.")

class MealPlanResponse(BaseModel):
    days: List[DailyPlan]

# --- Centralized Prompt Definition ---
# Moving the complex instruction set here makes the code cleaner.
PROMPT_INSTRUCTIONS = """
You are Stephen, a highly experienced Kenyan Registered Dietitian Nutritionist (RDN).
Your task is to create a realistic, culturally appropriate, and budget-friendly {days}-day meal plan for a client.

CLIENT DETAILS:
- Age: {age}
- Gender: {gender}
- Primary Health Goal/Condition: {condition}
- Daily Calorie Target: ~{kcal_goal} kcal
- Daily Budget: ~KSh {budget}
- Preferences: {preferences}

INSTRUCTIONS:
1.  **Use ONLY Foods from this List**: You MUST base all meals on the following list of available Kenyan foods. Do not invent foods.
    <food_list>
    {food_list_str}
    </food_list>
2.  **Be Realistic for Kenya**: Meals must be practical and common in Kenya (e.g., githeri, ugali, sukuma wiki, chapati, rice and beans).
3.  **Structure the Output**: Create a plan for {days} days. Each day must have breakfast, lunch, and dinner. You can optionally add a snack.
4.  **Output Format**: You MUST output ONLY a single, valid JSON object that strictly follows this structure. Do not add any text or explanations before or after the JSON object.
5.  **Numeric Values**: All values for nutrients (like 'calories', 'protein') and costs MUST be numbers (integer or float), not strings. For example, `"calories": 550`, not `"calories": "550 kcal"`.
6.  **Nutrient Focus**: Given the client's goal of '{condition}', you MUST include estimates for the following key nutrients in the `nutrients` and `daily_totals` objects: {key_nutrients_str}.

JSON_STRUCTURE:
{{
  "days": [
    {{
      "day": 1,
      "meals": {{
        "breakfast": {{ "name": "...", "ingredients": ["...", "..."], "nutrients": {{"calories": 350, "protein": 15, "carbohydrates": 50}}, "cost": 150 }},
        "lunch": {{ "name": "...", "ingredients": ["...", "..."], "nutrients": {{"calories": 600, "protein": 30, "carbohydrates": 70}}, "cost": 200 }},
        "dinner": {{ "name": "...", "ingredients": ["...", "..."], "nutrients": {{"calories": 550, "protein": 25, "carbohydrates": 65}}, "cost": 180 }},
        "snacks": {{ "name": "...", "ingredients": ["...", "..."], "nutrients": {{"calories": 150, "protein": 5, "carbohydrates": 25}}, "cost": 50 }}
      }},
      "daily_totals": {{ "calories": 1650, "protein": 75, "carbohydrates": 210, "estimated_cost": 580 }}
    }}
  ]
}}

Begin now.
""".strip()


# --- Refactored Main Planner Class (Dispatcher) ---
class MealPlanner:
    """
    Acts as a dispatcher to a selected meal planner backend (e.g., Ollama, Gemini).
    It constructs the prompt, sends it to the backend, and validates the response.
    """
    def __init__(self, backend_config: Dict[str, Any]):
        """
        Args:
            backend_config (Dict[str, Any]): Configuration for the backend,
                e.g., {'name': 'ollama', 'model': 'deepseekcoderafya'}
                e.g., {'name': 'gemini', 'model': 'gemini-1.5-flash', 'api_key': '...'}
        """
        backend_name = backend_config.pop('name', None)
        if not backend_name:
            raise ValueError("Backend name must be specified in backend_config.")
        
        self.backend: MealPlannerBackend = get_backend(backend_name, **backend_config)

    def generate_meal_plan(self, user_inputs: dict, food_list_str: str) -> Tuple[Dict, str]:
        """
        Generates a meal plan using the configured backend.

        Returns:
            A tuple containing:
            - A dictionary of the validated meal plan.
            - The prompt string sent to the backend.
        
        Raises:
            PlannerConnectionError, PlannerModelNotFound, PlannerResponseValidationError
        """
        prompt = self._construct_prompt(user_inputs, food_list_str)
        
        try:
            raw_response_content, metadata = self.backend.generate_plan(prompt)
            
            # Validate the response with Pydantic
            validated_plan = MealPlanResponse.model_validate_json(raw_response_content)
            return validated_plan.model_dump(), prompt
        
        except ValidationError as e:
            # This is a validation error from Pydantic
            raise PlannerResponseValidationError(
                "The planner backend returned data in an unexpected format.",
                raw_response_content,
                e
            )
        except (PlannerConnectionError, PlannerModelNotFound) as e:
            # Re-raise backend-specific errors
            raise e
        except Exception as e:
            # Catch any other unexpected errors during plan generation
            raise PlannerConnectionError(f"An unexpected error occurred during plan generation: {e}")

    def _construct_prompt(self, user_inputs: dict, food_list_str: str) -> str:
        """Builds the detailed prompt from the template and user inputs."""
        # RDN Principle: Tailor nutrient focus to the client's condition.
        condition = user_inputs.get('condition', 'General Wellness')
        nutrient_focus_map = {
            'General Wellness': ['calories', 'protein', 'carbohydrates', 'estimated_cost'],
            'Diabetes Type 2': ['calories', 'carbohydrates', 'sugars', 'protein', 'fats', 'estimated_cost'],
            'Hypertension': ['calories', 'sodium', 'potassium', 'protein', 'estimated_cost'],
            'Anaemia': ['calories', 'iron', 'vitamin_c', 'protein', 'estimated_cost'],
            'Pregnancy': ['calories', 'folate', 'iron', 'calcium', 'protein', 'estimated_cost']
        }
        key_nutrients = nutrient_focus_map.get(condition, nutrient_focus_map['General Wellness'])
        
        # Combine user inputs with other prompt variables
        prompt_vars = {
            **user_inputs,
            'food_list_str': food_list_str[:3000],  # Truncate to avoid excessive length
            'key_nutrients_str': ", ".join(f"'{n}'" for n in key_nutrients)
        }
        
        return PROMPT_INSTRUCTIONS.format(**prompt_vars)

# To test this file directly
if __name__ == '__main__':
    import streamlit as st
    
    st.title("Meal Planner Dispatcher Test")

    # Mock data
    mock_user_inputs = {
        'age': 35, 'gender': 'Male', 'condition': 'Diabetes Type 2',
        'kcal_goal': 1800, 'budget': 600, 'days': 1, 'preferences': 'No red meat'
    }
    mock_food_list = "Ugali (Maize), Sukuma wiki (Kale), Cabbage, Tomatoes, Onions, Carrots, Githeri, Beans, Beef, Chicken, Fish (Tilapia), Rice, Potatoes"

    st.subheader("Test Inputs")
    st.json(mock_user_inputs)

    # --- Backend Selection for Test ---
    backend_choice = st.radio("Select Backend to Test", ('Ollama', 'Gemini'))
    
    if st.button(f"Generate Test Plan with {backend_choice}"):
        backend_config = {}
        if backend_choice == 'Ollama':
            backend_config = {'name': 'ollama', 'model': 'deepseekcoderafya'}
        elif backend_choice == 'Gemini':
            # IMPORTANT: For local testing, use Streamlit secrets or env vars
            # Never hardcode API keys!
            api_key = st.text_input("Enter Gemini API Key for test:", type="password")
            if not api_key:
                st.warning("Please provide a Gemini API key to test.")
                st.stop()
            backend_config = {'name': 'gemini', 'model': 'gemini-1.5-flash', 'api_key': api_key}
        
        try:
            with st.spinner(f"Initializing {backend_choice} backend..."):
                planner = MealPlanner(backend_config)

            with st.spinner("Generating plan..."):
                result, prompt = planner.generate_meal_plan(mock_user_inputs, mock_food_list)
            
            st.success("Meal plan generated successfully!")
            with st.expander("Prompt Sent to Backend"):
                st.text(prompt)
            
            st.subheader("✅ Validated Planner Output")
            st.json(result)

        except (PlannerConnectionError, PlannerModelNotFound) as e:
            st.error(f"A problem occurred with the Planner Backend: {e}")
        except PlannerResponseValidationError as e:
            st.error(f"The planner returned data in an unexpected format. Details: {e}")
            st.subheader("Raw AI Response:")
            st.code(e.raw_content, language='json')
            st.subheader("Validation Error:")
            st.text(str(e.validation_error))
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
