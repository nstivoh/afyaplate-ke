# filepath: core/pdf_report.py
from fpdf import FPDF
from datetime import datetime
import plotly.graph_objects as go
from pathlib import Path
import streamlit as st

class PDFReport(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rdn_name = "Stephen"
        self.rdn_title = "Kenyan Registered Dietitian Nutritionist (RDN)"

    def header(self):
        self.set_font("helvetica", "B", 16)
        # Kenyan flag colors
        self.set_text_color(0, 128, 0) # Green
        self.cell(0, 10, "🇰🇪 AfyaPlate KE", border=False, ln=True, align="L")
        
        self.set_font("helvetica", "", 10)
        self.set_text_color(0, 0, 0) # Black
        self.cell(0, 6, f"Professional Meal Plan by {self.rdn_name} – {self.rdn_title}", border=False, ln=True, align="L")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128)
        footer_text = "100% local • Privacy first • Built in Nairobi on Parrot Sec OS"
        self.cell(0, 10, footer_text, border=False, align="C")
        self.ln(4)
        page_num_text = f"Page {self.page_no()}/{{nb}}"
        self.cell(0, 10, page_num_text, border=False, align="C")

    def client_details_section(self, client_info):
        self.set_font("helvetica", "B", 12)
        self.set_fill_color(240, 242, 246) # Light grey
        self.cell(0, 10, "Client Meal Plan Report", border=1, ln=True, align="C", fill=True)
        
        self.set_font("helvetica", "", 11)
        self.cell(40, 8, "Client Name:", border=False)
        self.cell(0, 8, str(client_info.get('name', 'N/A')), border=False, ln=True)
        
        self.cell(40, 8, "Age:", border=False)
        self.cell(0, 8, str(client_info.get('age', 'N/A')), border=False, ln=True)

        self.cell(40, 8, "Diagnosis/Goal:", border=False)
        self.cell(0, 8, str(client_info.get('condition', 'N/A')), border=False, ln=True)

        self.cell(40, 8, "Report Date:", border=False)
        self.cell(0, 8, datetime.now().strftime("%d %B %Y"), border=False, ln=True)
        self.ln(10)

    def meal_plan_section(self, meal_plan):
        if not meal_plan or 'days' not in meal_plan:
            self.set_font("helvetica", "I", 10)
            self.cell(0, 10, "No meal plan data available.", border=False, ln=True)
            return

        self.set_font("helvetica", "B", 12)
        self.set_fill_color(0, 128, 0) # Green
        self.set_text_color(255, 255, 255) # White
        self.cell(0, 10, f"{len(meal_plan['days'])}-Day Meal Plan", border=1, ln=True, align="C", fill=True)
        self.set_text_color(0, 0, 0)

        for day_plan in meal_plan['days']:
            self.set_font("helvetica", "B", 11)
            self.cell(0, 10, f"Day {day_plan['day']}", border="B", ln=True, align="L")
            self.ln(2)

            meals = day_plan.get('meals', {})
            for meal_type, meal_details in meals.items():
                if not meal_details: continue
                
                self.set_font("helvetica", "B", 10)
                self.cell(30, 6, f"{meal_type.title()}:", border=False)
                self.set_font("helvetica", "", 10)
                self.multi_cell(0, 6, meal_details.get('name', 'N/A'), border=False)
                
                # Ingredients
                self.set_x(self.get_x() + 5) # Indent
                self.set_font("helvetica", "I", 9)
                ingredients = ", ".join(meal_details.get('ingredients', []))
                self.multi_cell(0, 5, f"Ingredients: {ingredients}", border=False)
                self.ln(3)

    def disclaimer_section(self):
        self.ln(15)
        self.set_font("helvetica", "B", 10)
        self.cell(0, 8, "Important Disclaimer", border="T", ln=True, align="L")
        self.set_font("helvetica", "I", 8)
        disclaimer = (
            "This meal plan is a sample guide and should be adapted to individual needs, preferences, and ingredient availability. "
            "Nutrient values are estimates. This document does not constitute medical advice. Consult with a qualified healthcare "
            "professional before making significant dietary changes, especially if you have an underlying medical condition."
        )
        self.multi_cell(0, 5, disclaimer)
        self.ln(5)

    def signature_section(self):
        self.set_font("helvetica", "", 10)
        self.cell(0, 8, "Professionally prepared by,", border="T", ln=True, align="L")
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, self.rdn_name, border=False, ln=True, align="L")
        self.set_font("helvetica", "", 10)
        self.cell(0, 6, self.rdn_title, border=False, ln=True, align="L")

def generate_report(client_info: dict, meal_plan: dict) -> bytes:
    """
    Generates the full PDF report and returns it as a byte string.
    
    Args:
        client_info (dict): Dictionary with client's details.
        meal_plan (dict): The meal plan generated by the LLM.

    Returns:
        bytes: The generated PDF content.
    """
    try:
        pdf = PDFReport()
        pdf.add_page()
        pdf.alias_nb_pages()

        # Add content
        pdf.client_details_section(client_info)
        pdf.meal_plan_section(meal_plan)
        pdf.disclaimer_section()
        pdf.signature_section()
        
        # Output the PDF to a byte string
        return pdf.output(dest='S').encode('latin-1')
        
    except Exception as e:
        st.error(f"An error occurred while generating the PDF: {e}")
        return b""

# To test this file directly
if __name__ == '__main__':
    st.title("PDF Report Generator Test")

    # Mock data for testing
    mock_client = {
        'name': 'Jane Doe',
        'age': 45,
        'condition': 'Hypertension Management'
    }
    mock_plan = {
        "days": [
            {
                "day": 1,
                "meals": {
                    "breakfast": {"name": "Oatmeal with Fruits", "ingredients": ["Oats", "Banana", "Berries"]},
                    "lunch": {"name": "Grilled Chicken Salad", "ingredients": ["Chicken Breast", "Lettuce", "Tomato", "Cucumber"]},
                    "dinner": {"name": "Steamed Fish with Brown Rice and Greens", "ingredients": ["Tilapia", "Brown Rice", "Sukuma Wiki"]}
                }
            }
        ]
    }

    st.subheader("Test Data")
    st.json({"client": mock_client, "plan": mock_plan})

    if st.button("Generate Test PDF Report"):
        pdf_bytes = generate_report(mock_client, mock_plan)
        if pdf_bytes:
            st.success("PDF Generated Successfully!")
            st.download_button(
                label="Download Test PDF",
                data=pdf_bytes,
                file_name="test_report_afyaplate.pdf",
                mime="application/pdf"
            )
        else:
            st.error("PDF generation failed.")
```