from fastapi import APIRouter

from app.api.v1.endpoints import planner, foods, payments

api_router = APIRouter()
api_router.include_router(planner.router, prefix="/planner", tags=["planner"])
api_router.include_router(foods.router, prefix="/foods", tags=["foods"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
