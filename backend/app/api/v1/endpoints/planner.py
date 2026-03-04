from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi.responses import StreamingResponse
from app.schemas.planner import PlannerRequest, PlannerResponse
from app.services import llm_service, pdf_service
from app.services.algo_service import AlgoService

router = APIRouter()

@router.post("/generate", response_model=PlannerResponse)
async def generate_meal_plan_endpoint(request: PlannerRequest):
    """
    Generate a meal plan based on user requirements.
    """
    try:
        meal_plan = await llm_service.generate_meal_plan(request)
        return meal_plan
    except Exception as e:
        # In a real app, you'd have more specific error handling
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-algorithmic", response_model=PlannerResponse)
async def generate_algorithmic_plan(request: PlannerRequest):
    try:
        algo_service = AlgoService()
        plan = algo_service.generate_algorithmic_plan(request)
        return plan
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export-pdf")
async def export_meal_plan_pdf(plan: PlannerResponse):
    """
    Export a generated meal plan as a PDF.
    """
    try:
        pdf_buffer = pdf_service.generate_meal_plan_pdf(plan)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=afyaplate_meal_plan.pdf"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF Generation failed: {str(e)}")
