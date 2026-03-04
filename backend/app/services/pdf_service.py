import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from io import BytesIO
from app.schemas.planner import PlannerResponse

# Setup Jinja2 environment
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(template_dir))

def generate_meal_plan_pdf(plan: PlannerResponse) -> BytesIO:
    """
    Renders a PlannerResponse into a styled PDF using an HTML template.
    """
    template = env.get_template("meal_plan.html")
    
    # Render HTML with plan data
    html_content = template.render(plan=plan.model_dump())
    
    # Convert HTML to PDF in memory
    pdf_buffer = BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    
    return pdf_buffer
