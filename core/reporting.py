# filepath: core/reporting.py
import pandas as pd
from collections import Counter
from fpdf import FPDF
from datetime import datetime
from typing import Dict, Any

class MealPlanReporter:
    """
    Generates a PDF report for a given meal plan.
    The report includes daily meal breakdowns and a consolidated shopping list.
    """

    def __init__(self, meal_plan: Dict[str, Any], client_info: Dict[str, Any]):
        """
        Initializes the reporter with the meal plan and client data.

        Args:
            meal_plan (Dict[str, Any]): The meal plan dictionary from MealPlannerLLM.
            client_info (Dict[str, Any]): A dictionary of user-provided information.
        """
        self.meal_plan = meal_plan
        self.client_info = client_info
        self.shopping_list = self._consolidate_shopping_list()

    def _consolidate_shopping_list(self) -> Dict[str, int]:
        """
        Aggregates all ingredients from the meal plan into a single shopping list.
        """
        all_ingredients = []
        for day_plan in self.meal_plan.get('days', []):
            for meal_type, meal_details in day_plan.get('meals', {}).items():
                if meal_details and 'ingredients' in meal_details:
                    all_ingredients.extend([ing.strip().capitalize() for ing in meal_details['ingredients']])
        
        return dict(Counter(all_ingredients))

    def generate_report(self, output_path: str = "AfyaPlate_Meal_Plan.pdf"):
        """
        Generates and saves the PDF report.

        Args:
            output_path (str): The path to save the generated PDF file.
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # --- Header ---
        pdf.set_font('Helvetica', 'B', 20)
        pdf.cell(0, 10, 'AfyaPlate KE - Personalized Meal Plan', 0, 1, 'C')
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 5, f"Generated on: {datetime.now().strftime('%d-%b-%Y')}", 0, 1, 'C')
        pdf.ln(10)

        # --- Client Info ---
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'Client Details', 0, 1)
        pdf.set_font('Helvetica', '', 10)
        # Create a simple table for client info
        client_data = [
            ["Age:", str(self.client_info.get('age', 'N/A'))],
            ["Gender:", self.client_info.get('gender', 'N/A')],
            ["Health Goal:", self.client_info.get('condition', 'N/A')],
            ["Daily Calorie Target:", f"{self.client_info.get('kcal_goal', 'N/A')} kcal"],
            ["Daily Budget:", f"KSh {self.client_info.get('budget', 'N/A')}"]
        ]
        with pdf.table(col_widths=(35, 155)) as table:
            for data_row in client_data:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)
        pdf.ln(10)

        # --- Daily Meal Plan ---
        for day_plan in self.meal_plan.get('days', []):
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, f"Day {day_plan['day']}", 'B', 1)
            pdf.ln(5)

            for meal_type in ['breakfast', 'lunch', 'dinner', 'snacks']:
                if meal_details := day_plan.get('meals', {}).get(meal_type):
                    pdf.set_font('Helvetica', 'B', 11)
                    pdf.cell(0, 8, f"{meal_type.capitalize()}: {meal_details['name']}", 0, 1)
                    
                    pdf.set_font('Helvetica', '', 10)
                    pdf.multi_cell(0, 5, f"  • Ingredients: {', '.join(meal_details['ingredients'])}")
                    
                    # Display nutrients, gracefully handling missing data
                    nutrient_str_parts = []
                    if 'calories' in meal_details.get('nutrients', {}):
                        nutrient_str_parts.append(f"Calories: {meal_details['nutrients']['calories']:.0f} kcal")
                    if 'protein' in meal_details.get('nutrients', {}):
                        nutrient_str_parts.append(f"Protein: {meal_details['nutrients']['protein']:.0f}g")
                    if nutrient_str_parts:
                        pdf.multi_cell(0, 5, f"  • Nutrition: {', '.join(nutrient_str_parts)}")
                    
                    pdf.ln(4)
            
            # Daily Totals
            pdf.set_font('Helvetica', 'I', 10)
            daily_totals = day_plan.get('daily_totals', {})
            total_cost = daily_totals.get('estimated_cost', 0)
            total_calories = daily_totals.get('calories', 0)
            pdf.cell(0, 5, f"Estimated Daily Totals - Cost: KSh {total_cost:.0f}, Calories: {total_calories:.0f} kcal", 0, 1, 'R')
            pdf.ln(5)

        # --- Shopping List ---
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 16)
        pdf.cell(0, 10, 'Consolidated Shopping List', 0, 1, 'C')
        pdf.ln(10)

        pdf.set_font('Helvetica', '', 10)
        # Two columns for shopping list
        col1 = ""
        col2 = ""
        items = sorted(self.shopping_list.items())
        midpoint = len(items) // 2 + (len(items) % 2)
        
        for i, (item, count) in enumerate(items):
            line = f"{item} (x{count})"
            if i < midpoint:
                col1 += line + "
"
            else:
                col2 += line + "
"
                
        # Create a layout with two columns
        pdf.multi_cell(95, 5, col1, 0, 'L')
        pdf.set_y(pdf.get_y() - midpoint * 5) # Reset Y to top of the list
        pdf.set_x(pdf.get_x() + 95)
        pdf.multi_cell(95, 5, col2, 0, 'L')
        
        pdf.ln(15)

        # --- Disclaimer ---
        pdf.set_font('Helvetica', 'I', 8)
        pdf.multi_cell(0, 4, 
            "Disclaimer: This meal plan is a suggestion based on the provided details and "
            "should not be considered a substitute for professional medical advice. Nutrient values are estimates. "
            "Consult a registered dietitian or doctor before making significant dietary changes. "
            "Prices are estimates based on 2026 market data and may vary.", 0, 'C')

        pdf.output(output_path)

if __name__ == '__main__':
    # Mock data for testing
    mock_plan = {
        'days': [{
            'day': 1,
            'meals': {
                'breakfast': {'name': 'Oatmeal with fruit', 'ingredients': ['Oats', 'Banana', 'Milk'], 'nutrients': {'calories': 350, 'protein': 10}},
                'lunch': {'name': 'Rice, Beans, and Sukuma Wiki', 'ingredients': ['Rice', 'Beans', 'Sukuma Wiki', 'Onion', 'Tomatoes'], 'nutrients': {'calories': 600, 'protein': 25}, 'cost': 180},
                'dinner': {'name': 'Ugali with Beef Stew', 'ingredients': ['Maize Flour', 'Beef', 'Tomatoes', 'Onion', 'Carrots'], 'nutrients': {'calories': 700, 'protein': 35}, 'cost': 250},
            },
            'daily_totals': {'calories': 1650, 'protein': 70, 'estimated_cost': 430}
        }]
    }
    mock_client = {'age': 35, 'gender': 'Female', 'condition': 'General Wellness', 'kcal_goal': 1800, 'budget': 500}
    
    print("Generating sample PDF report 'test_report.pdf'...")
    reporter = MealPlanReporter(meal_plan=mock_plan, client_info=mock_client)
    reporter.generate_report("test_report.pdf")
    print("Done.")
