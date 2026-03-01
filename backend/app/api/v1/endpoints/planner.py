from fastapi import APIRouter, HTTPException
from app.schemas.planner import PlannerRequest, PlannerResponse
from app.services import llm_service

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
