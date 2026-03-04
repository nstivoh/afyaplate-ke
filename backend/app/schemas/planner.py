from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class PlannerRequest(BaseModel):
    target_calories: int = Field(..., example=2200, description="Target daily calories")
    protein_grams: Optional[int] = Field(None, example=150, description="Target daily protein in grams")
    fat_grams: Optional[int] = Field(None, example=70, description="Target daily fat in grams")
    carb_grams: Optional[int] = Field(None, example=250, description="Target daily carbohydrates in grams")
    dietary_restrictions: Optional[List[str]] = Field(None, example=["vegetarian", "gluten-free"], description="List of dietary restrictions")
    num_meals: int = Field(3, example=3, description="Number of meals for the day")
    llm_provider: str = Field(..., example="gemini", description="AI Provider (e.g. gemini, openai, anthropic, groq)")
    llm_model: str = Field(..., example="gemini-1.5-flash", description="Specific Model mapping string")
    llm_api_key: Optional[str] = Field(None, example="AIzaSy...", description="API Key matching the provider")

class MacroNutrients(BaseModel):
    protein_g: float
    fat_g: float
    carbs_g: float

class MealItem(BaseModel):
    food_name: str = Field(..., example="Sukuma Wiki")
    quantity: str = Field(..., example="2 cups, chopped")
    calories: int = Field(..., example=150)
    macros: MacroNutrients

class Meal(BaseModel):
    meal_name: str = Field(..., example="Lunch")
    items: List[MealItem]
    total_calories: int
    total_macros: MacroNutrients

class DailySummary(BaseModel):
    total_calories: int
    total_macros: MacroNutrients

class PlannerResponse(BaseModel):
    meals: List[Meal]
    daily_summary: DailySummary
