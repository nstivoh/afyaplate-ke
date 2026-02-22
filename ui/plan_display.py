# filepath: ui/plan_display.py
import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, Any

def display_plan_visualizations(meal_plan: Dict[str, Any]):
    """
    Renders interactive Plotly charts for the meal plan's nutritional and cost breakdowns.

    Args:
        meal_plan (Dict[str, Any]): The meal plan dictionary from MealPlannerLLM.
    """
    if not meal_plan or 'days' not in meal_plan:
        st.info("No plan data to display.")
        return

    try:
        # --- Data Preparation ---
        # Use a list to collect daily data records
        daily_records = []
        for day in meal_plan.get('days', []):
            record = {"Day": f"Day {day.get('day', 'N/A')}"}
            # Flatten the daily_totals dictionary into the record
            totals = day.get('daily_totals', {})
            record.update(totals)
            daily_records.append(record)
        
        if not daily_records:
            st.warning("Plan generated, but no daily data available to visualize.")
            return

        df = pd.DataFrame(daily_records)
        df.set_index("Day", inplace=True)

        st.subheader("📊 Plan Analysis")

        # --- Charting ---
        # Selectbox to choose the chart view
        chart_view = st.selectbox(
            "Select View:", 
            ["Nutrient Breakdown", "Cost Analysis"],
            key="plan_display_view"
        )
        
        if chart_view == "Nutrient Breakdown":
            # Filter for numeric columns that are not cost-related
            nutrient_cols = [col for col in df.columns if df[col].dtype in ['float64', 'int64'] and 'cost' not in col.lower()]
            if not nutrient_cols:
                st.warning("No nutrient data found in the plan to display.")
                return

            # Let user select which nutrient to view
            selected_nutrient = st.selectbox(
                "Select Nutrient to Compare:",
                options=nutrient_cols,
                format_func=lambda x: x.replace('_', ' ').title() # E.g., 'carbohydrates' -> 'Carbohydrates'
            )

            fig_nutrients = px.bar(
                df,
                y=selected_nutrient,
                x=df.index,
                title=f"Daily {selected_nutrient.replace('_', ' ').title()} Overview",
                labels={"y": selected_nutrient.replace('_', ' ').title(), "x": "Day"},
                text_auto='.2s'
            )
            fig_nutrients.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
            fig_nutrients.update_layout(
                uniformtext_minsize=8, 
                uniformtext_mode='hide',
                xaxis_title=None
            )
            st.plotly_chart(fig_nutrients, use_container_width=True)

        elif chart_view == "Cost Analysis":
            cost_col = None
            # Find the cost column, case-insensitive
            for col in df.columns:
                if 'cost' in col.lower():
                    cost_col = col
                    break
            
            if not cost_col:
                st.warning("No cost data found in the plan to display.")
                return

            total_cost = df[cost_col].sum()
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Total Estimated Cost", f"KSh {total_cost:,.0f}")
                st.metric("Average Daily Cost", f"KSh {df[cost_col].mean():,.0f}")

            with col2:
                fig_cost_pie = px.pie(
                    df,
                    values=cost_col,
                    names=df.index,
                    title="Cost Distribution Per Day",
                    hole=0.4,
                )
                fig_cost_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_cost_pie, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred while creating visualizations: {e}")
        st.info("Ensure the meal plan was generated correctly.")


if __name__ == '__main__':
    # Mock data for testing this component directly
    st.set_page_config(layout="wide")
    st.title("Plan Display Component Test")

    mock_plan_data = {
        'days': [
            {'day': 1, 'daily_totals': {'calories': 1850, 'protein': 90, 'carbohydrates': 210, 'sodium': 2200, 'estimated_cost': 480}},
            {'day': 2, 'daily_totals': {'calories': 1790, 'protein': 85, 'carbohydrates': 200, 'sodium': 1900, 'estimated_cost': 510}},
            {'day': 3, 'daily_totals': {'calories': 1920, 'protein': 95, 'carbohydrates': 225, 'sodium': 2400, 'estimated_cost': 450}}
        ]
    }
    
    display_plan_visualizations(mock_plan_data)
