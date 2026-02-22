# filepath: components/meal_planner_ui.py
import streamlit as st
import pandas as pd
from io import BytesIO
from core.planner_dispatcher import MealPlanner
from core.planner_backends import PlannerConnectionError, PlannerModelNotFound, PlannerResponseValidationError
from ui.plan_display import display_plan_visualizations
from core.reporting import MealPlanReporter

def show_meal_planner_ui(food_df: pd.DataFrame):
    """
    Renders the Meal Planner UI and handles the interaction logic.
    """
    st.header("🍽️ Automated Meal Planner")
    st.write("Generate a personalized meal plan based on your health goals and locally available Kenyan foods.")

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
                "General Wellness", "Weight Loss", "Weight Gain", "Diabetes Type 2",
                "Hypertension", "Pregnancy", "Anaemia"
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
        
        try:
            # Construct backend configuration from session state
            backend_config = {
                "name": st.session_state.get('planner_backend', 'Ollama').lower(),
                "model": st.session_state.get('ollama_model') if st.session_state.get('planner_backend') == 'Ollama' else 'gemini-1.5-flash',
                "api_key": st.session_state.get('gemini_api_key')
            }
            
            # Check for Gemini API key if that's the selected backend
            if backend_config["name"] == "gemini" and not backend_config["api_key"]:
                st.error("Gemini API key is missing. Please add it in the ⚙️ Settings page.")
                st.stop()

            with st.spinner(f"🧑‍🍳 Initializing the {st.session_state.get('planner_backend', 'Ollama')} planner..."):
                planner = MealPlanner(backend_config=backend_config)
            
            with st.spinner("Generating your personalized meal plan... This may take a moment."):
                meal_plan_response, prompt = planner.generate_meal_plan(user_inputs, food_list_str)

            st.session_state.meal_plan = meal_plan_response
            st.success("Your personalized meal plan has been generated!")

        except (PlannerConnectionError, PlannerModelNotFound) as e:
            st.session_state.meal_plan = None
            st.error(f"A problem occurred with the Automated Planner Backend: {e}")
        except PlannerResponseValidationError as e:
            st.session_state.meal_plan = None
            st.error(f"The planner returned data in an unexpected format. Please try again. Details: {e}")
            with st.expander("Show Raw Planner Output"):
                st.code(e.raw_content, language='json')
        except Exception as e:
            st.session_state.meal_plan = None
            st.error(f"An unexpected error occurred: {e}")


    # --- Display Generated Meal Plan ---
    if st.session_state.meal_plan:
        st.divider()
        st.subheader("Your Custom Meal Plan")

        # --- Download Button ---
        # Generate the PDF in memory
        reporter = MealPlanReporter(st.session_state.meal_plan, st.session_state.last_user_inputs)
        pdf_buffer = BytesIO()
        reporter.generate_report(pdf_buffer)
        pdf_buffer.seek(0)
        
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name="AfyaPlate_Meal_Plan.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        st.caption("Includes daily plan and a consolidated shopping list.")

        plan = st.session_state.meal_plan
        for day_plan in plan.get('days', []):
            with st.expander(f"**Day {day_plan['day']}** - View Day Plan", expanded=day_plan['day']==1):
                display_daily_plan(day_plan)
        
        st.divider()
        # --- Visualizations ---
        display_plan_visualizations(st.session_state.meal_plan)


def display_daily_plan(day_plan):
    """Renders the UI for a single day's meal plan."""
    meals = day_plan.get('meals', {})
    
    # Determine number of columns based on available meals
    meal_types_present = [m for m in ['breakfast', 'lunch', 'dinner', 'snacks'] if m in meals and meals[m]]
    if not meal_types_present:
        st.info("No meals defined for this day.")
        return

    meal_cols = st.columns(len(meal_types_present))
    
    for i, meal_type in enumerate(meal_types_present):
        meal_details = meals[meal_type]
        with meal_cols[i]:
            st.markdown(f"**{meal_type.title()}**")
            with st.container(border=True):
                st.markdown(f"*{meal_details.get('name', 'N/A')}*")
                
                ingredients = meal_details.get('ingredients', [])
                if ingredients:
                    st.markdown("\n".join(f"- <small>{ing}</small>" for ing in ingredients), unsafe_allow_html=True)

                if 'cost' in meal_details and meal_details['cost']:
                    st.caption(f"Est. Cost: KSh {meal_details['cost']:.0f}")
                
                # Display key nutrients
                nutrients = meal_details.get('nutrients', {})
                cal_str = f"{nutrients.get('calories', 0):.0f} kcal"
                prot_str = f"{nutrients.get('protein', 0):.0f}g protein"
                st.caption(f"{cal_str}, {prot_str}")
