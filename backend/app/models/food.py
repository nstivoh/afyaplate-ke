# backend/app/models/food.py
from pydantic import BaseModel
from typing import Optional

class Food(BaseModel):
    food_code: str
    food_name_english: Optional[str] = None
    food_name_swahili: Optional[str] = None
    category: Optional[str] = None
    display_name: Optional[str] = None
    energy_kcal: Optional[float] = None
    protein_g: Optional[float] = None
    fat_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fibre_g: Optional[float] = None
    calcium_mg: Optional[float] = None
    iron_mg: Optional[float] = None
    zinc_mg: Optional[float] = None

    class Config:
        from_attributes = True
