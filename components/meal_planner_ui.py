# filepath: components/meal_planner_ui.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.llm_meal_planner import MealPlannerLLM

def show_meal_planner_ui(food_df: pd.DataFrame):
    """
    Renders the AI Meal Planner UI and handles the interaction logic.
    """
    st.header("🍽️ AI-Powered Meal Planner")
    st.write("Generate a personalized meal plan using a local AI model. The plan will be based on your health goals and the available Kenyan foods.")

    # Initialize session state for the meal plan
    if 'meal_plan' not in st.session_state:
        st.session_state.meal_plan = None
    if 'last_user_inputs' not in st.session_state:
        st.session_state.last_user_inputs = {}

    # --- User Input Form ---
    with st.form("meal_plan_form"):
        st.subheader("Tell us about yourself")
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=1, max_value=100, value=30, step=1)
            kcal_goal = st.slider("Daily Calorie Goal (kcal)", 1000, 4000, 2000, 100)
            days = st.slider("Number of Days for Plan", 1, 7, 3)

        with col2:
            gender = st.selectbox("Gender", ["Female", "Male"])
            budget = st.slider("Approx. Budget per Day (KSh)", 200, 2000, 500, 50)
            
        condition = st.selectbox(
            "Primary Health Goal or Condition",
            [
                "General Wellness", "Weight Loss", "Weight Gain", "Diabetes Type 2 Management",
                "Hypertension (High Blood Pressure)", "Pregnancy", "Anemia Prevention",
                "Child Nutrition (Age 5+)"
            ]
        )
        preferences = st.text_input("Food Preferences or Allergies", "e.g., vegetarian, no pork, allergic to nuts")

        submitted = st.form_submit_button("✨ Generate Meal Plan", use_container_width=True)

    if submitted:
        if food_df.empty:
            st.error("Cannot generate a plan because the food database is empty. Please go to the 'Settings' tab and run the PDF extractor first.")
            return
            
        user_inputs = {
            "age": age, "gender": gender, "condition": condition,
            "kcal_goal": kcal_goal, "budget": budget, "days": days,
            "preferences": preferences if preferences else "None"
        }
        st.session_state.last_user_inputs = user_inputs

        # Prepare food list for the LLM
        food_list_str = ", ".join(food_df['food_name_english'].unique())
        
        # Instantiate and run the LLM planner
        planner = MealPlannerLLM() # Model can be configured in settings later
        with st.spinner("🧠 The AI is thinking..."):
            meal_plan_response = planner.generate_meal_plan(user_inputs, food_list_str)

        if meal_plan_response and "error" not in meal_plan_response:
            st.session_state.meal_plan = meal_plan_response
            st.success("Your personalized meal plan has been generated!")
        else:
            st.session_state.meal_plan = None
            st.error("The AI failed to generate a valid plan. This could be a temporary issue. Please try adjusting your inputs or try again.")

    # --- Display Generated Meal Plan ---
    if st.session_state.meal_plan:
        st.divider()
        st.subheader("Your Custom Meal Plan")

        plan = st.session_state.meal_plan
        for day_plan in plan.get('days', []):
            with st.expander(f"**Day {day_plan['day']}** - View Plan", expanded=day_plan['day']==1):
                display_daily_plan(day_plan)
        
        # --- Shopping List ---
        st.subheader("🛒 Shopping List")
        shopping_list = generate_shopping_list(plan)
        if shopping_list:
            shopping_text = ""
            for item, count in shopping_list.items():
                shopping_text += f"- {item.capitalize()}
"
            st.markdown(shopping_text)
        else:
            st.info("Could not generate a shopping list from the plan.")


def display_daily_plan(day_plan):
    """Renders the UI for a single day's meal plan."""
    meals = day_plan.get('meals', {})
    
    meal_cols = st.columns(len(meals))
    
    for i, (meal_type, meal_details) in enumerate(meals.items()):
        if not meal_details: continue
        with meal_cols[i]:
            st.markdown(f"**{meal_type.title()}**")
            with st.container(border=True):
                st.markdown(f"*{meal_details.get('name', 'N/A')}*")
                
                ingredients = meal_details.get('ingredients', [])
                if ingredients:
                    st.markdown("
".join(f"- <small>{ing}</small>" for ing in ingredients), unsafe_allow_html=True)

                if 'cost' in meal_details and meal_details['cost']:
                    st.caption(f"Est. Cost: KSh {meal_details['cost']}")


def generate_shopping_list(plan: dict) -> dict:
    """Generates an aggregated shopping list from the meal plan."""
    if not plan or 'days' not in plan:
        return {}
    
    all_ingredients = []
    for day in plan['days']:
        for meal_type, meal_details in day.get('meals', {}).items():
            if meal_details and 'ingredients' in meal_details:
                all_ingredients.extend([ing.lower().strip() for ing in meal_details['ingredients']])
    
    # Count occurrences of each ingredient
    shopping_dict = {}
    for item in all_ingredients:
        shopping_dict[item] = shopping_dict.get(item, 0) + 1
        
    return shopping_dict
```