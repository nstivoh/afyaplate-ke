# backend/app/api/v1/endpoints/foods.py
from fastapi import APIRouter, Query
from typing import List, Optional
from app.services.food_service import FoodService
from app.models.food import Food

router = APIRouter()
food_service = FoodService()

@router.get("/", response_model=List[Food])
async def search_foods(
    query: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 20,
):
    """
    Search for foods with advanced filtering.
    """
    foods = food_service.search(query=query, category=category, limit=limit)
    return foods
