# filepath: core/llm_meal_planner.py
import streamlit as st
import ollama
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Optional

# --- Pydantic Models for Response Validation ---
class MealItem(BaseModel):
    name: str = Field(..., description="Name of the meal, e.g., 'Ugali with Sukuma Wiki and Beef Stew'")
    ingredients: List[str] = Field(..., description="List of ingredients for the meal.")
    # The LLM may not get these right, but we ask for them.
    nutrients: Dict[str, str] = Field({}, description="Estimated nutrients (e.g., {'calories': '550 kcal', 'protein': '30g'}).")
    cost: Optional[int] = Field(None, description="Estimated cost in KSh.")

class Meals(BaseModel):
    breakfast: MealItem
    lunch: MealItem
    dinner: MealItem
    snacks: Optional[MealItem] = None

class DailyPlan(BaseModel):
    day: int
    meals: Meals
    daily_totals: Dict[str, str] = Field({}, description="Summary of daily nutritional totals.")

class MealPlanResponse(BaseModel):
    days: List[DailyPlan]

# --- Main LLM Interaction Class ---
class MealPlannerLLM:
    def __init__(self, model="deepseekcoderafya"):
        self.model = model
        self.client = ollama.Client()
        self._check_model_availability()

    def _check_model_availability(self):
        """Checks if the specified Ollama model is available."""
        try:
            models = self.client.list().get('models', [])
            model_names = [m['name'] for m in models]
            if not any(self.model in name for name in model_names):
                st.warning(f"Model '{self.model}' not found in Ollama. Please ensure it's pulled and available. Falling back to a generic model if possible.")
        except Exception as e:
            st.error(f"Could not connect to Ollama. Is it running? Error: {e}")
            st.info("Please start Ollama server. E.g., `ollama serve` in your terminal.")

    def generate_meal_plan(self, user_inputs: dict, food_list_str: str):
        """
        Generates a meal plan by calling the Ollama API with a detailed prompt.

        Args:
            user_inputs (dict): A dictionary of user preferences.
            food_list_str (str): A stringified list of available foods from KFCT.

        Returns:
            A parsed JSON object of the meal plan or an error dictionary.
        """
        prompt = self._construct_prompt(user_inputs, food_list_str)

        st.info("Generating your personalized meal plan with the local AI model... This might take a moment.")
        st.write("---")
        st.subheader("🤖 AI Prompt:")
        st.text(prompt)
        st.write("---")
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                format='json' # Ollama's JSON mode is perfect for this
            )
            
            raw_response_content = response['message']['content']
            
            # Validate the response with Pydantic
            try:
                # The response is a JSON string, so we parse it first
                validated_plan = MealPlanResponse.model_validate_json(raw_response_content)
                return validated_plan.model_dump() # Return as dict
            except ValidationError as e:
                st.error("The AI model returned data in an unexpected format. Please try again.")
                st.subheader("Raw AI Response:")
                st.code(raw_response_content, language='json')
                st.subheader("Validation Error:")
                st.text(str(e))
                return {"error": "Invalid JSON structure from LLM.", "details": str(e)}

        except Exception as e:
            st.error(f"Failed to generate meal plan. Error communicating with Ollama: {e}")
            return {"error": str(e)}

    def _construct_prompt(self, user_inputs: dict, food_list_str: str) -> str:
        """
        Builds the detailed prompt for the LLM based on user inputs.
        """
        # Destructure user inputs for clarity
        age = user_inputs.get('age', 30)
        gender = user_inputs.get('gender', 'Female')
        condition = user_inputs.get('condition', 'General Wellness')
        kcal_goal = user_inputs.get('kcal_goal', 2000)
        budget = user_inputs.get('budget', 500)
        days = user_inputs.get('days', 3)
        preferences = user_inputs.get('preferences', 'None')

        prompt = f"""
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
    {food_list_str[:3000]}
    </food_list>
2.  **Be Realistic for Kenya**: Meals must be practical and common in Kenya (e.g., githeri, ugali, sukuma wiki, chapati, rice and beans).
3.  **Structure the Output**: Create a plan for {days} days. Each day must have breakfast, lunch, and dinner. You can optionally add a snack.
4.  **Output Format**: You MUST output ONLY a single, valid JSON object that strictly follows this structure. Do not add any text or explanations before or after the JSON object.

JSON_STRUCTURE:
{{
  "days": [
    {{
      "day": 1,
      "meals": {{
        "breakfast": {{ "name": "...", "ingredients": ["...", "..."], "nutrients": {{"calories": "...", "protein": "..."}}, "cost": ... }},
        "lunch": {{ "name": "...", "ingredients": ["...", "..."], "nutrients": {{"calories": "...", "protein": "..."}}, "cost": ... }},
        "dinner": {{ "name": "...", "ingredients": ["...", "..."], "nutrients": {{"calories": "...", "protein": "..."}}, "cost": ... }},
        "snacks": {{ "name": "...", "ingredients": ["...", "..."], "nutrients": {{"calories": "...", "protein": "..."}}, "cost": ... }}
      }},
      "daily_totals": {{ "calories": "...", "protein": "...", "estimated_cost": "..." }}
    }}
  ]
}}

Begin now.
"""
        return prompt.strip()

# To test this file directly
if __name__ == '__main__':
    st.title("LLM Meal Planner Test")

    # Mock user inputs and food list for testing
    mock_user_inputs = {
        'age': 35,
        'gender': 'Male',
        'condition': 'Diabetes Type 2',
        'kcal_goal': 1800,
        'budget': 600,
        'days': 1,
        'preferences': 'No red meat'
    }
    mock_food_list = "Ugali (Maize), Sukuma wiki (Kale), Cabbage, Tomatoes, Onions, Carrots, Githeri, Beans, Beef, Chicken, Fish (Tilapia), Rice, Potatoes"

    st.subheader("Test Inputs")
    st.json(mock_user_inputs)

    if st.button("Generate Test Meal Plan"):
        planner = MealPlannerLLM()
        result = planner.generate_meal_plan(mock_user_inputs, mock_food_list)
        
        st.subheader("LLM Output")
        st.json(result)

```