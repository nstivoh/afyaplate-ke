# backend/app/services/algo_service.py
import random
from typing import List, Dict, Any
from app.db.database import SessionLocal
from app.models.sql_models import SQLFood
from app.schemas.planner import PlannerRequest, PlannerResponse, Meal, MealItem, DailySummary, MacroNutrients

class AlgoService:
    def __init__(self):
        self.db = SessionLocal()

    def _get_random_foods(self, category_keywords: List[str], limit: int = 5) -> List[SQLFood]:
        """Fetch foods that might fit a meal category (rudimentary filter)."""
        # In a real app we'd map KFCT categories better. Here we just grab random foods 
        # that roughly fit the requested categories by string matching, or just pure random.
        foods = self.db.query(SQLFood).all()
        
        # very simple categorization
        filtered = []
        for f in foods:
            name = (f.food_name_english or "").lower()
            if any(k in name for k in category_keywords):
                filtered.append(f)
                
        # Fallback to random if filter returns too few
        if len(filtered) < limit:
            filtered.extend(random.sample(foods, min(limit * 2, len(foods))))
            
        return random.sample(filtered, min(limit, len(filtered)))

    def generate_algorithmic_plan(self, request: PlannerRequest) -> PlannerResponse:
        """
        Greedy randomized approach to hit macros without an LLM.
        """
        # Target definitions
        target_cals = request.target_calories
        target_prot = request.protein_grams or (target_cals * 0.15 / 4) # fallback 15% protein
        target_fat = request.fat_grams or (target_cals * 0.30 / 9)     # fallback 30% fat
        target_carb = request.carb_grams or (target_cals * 0.55 / 4)   # fallback 55% carbs
        
        meals_data = []
        meals_count = request.num_meals
        
        # Divide targets evenly across meals for simplicity
        meal_cal_target = target_cals / meals_count
        
        current_total_cals = 0
        current_total_prot = 0
        current_total_fat = 0
        current_total_carb = 0

        # Simple assignment of keywords based on meal index
        for i in range(meals_count):
            meal_name = f"Meal {i+1}"
            keywords = []
            if i == 0:
                meal_name = "Breakfast"
                keywords = ["porridge", "tea", "bread", "egg", "milk", "uji"]
            elif i == 1:
                meal_name = "Lunch"
                keywords = ["rice", "ugali", "beef", "beans", "sukuma"]
            elif i == meals_count - 1:
                meal_name = "Dinner"
                keywords = ["ugali", "fish", "chicken", "spinach", "stew"]
                
            # Grab some candidate foods for this meal
            candidates = self._get_random_foods(keywords, limit=3)
            meal_items = []
            
            meal_cals = 0
            meal_prot = 0
            meal_fat = 0
            meal_carb = 0
            
            # Greedily add these candidates until we hit the per-meal calorie target
            for food in candidates:
                # Decide a random portion size between 100g and 300g
                portion_g = random.choice([100, 150, 200, 250])
                multiplier = portion_g / 100.0
                
                item_cals = int((food.energy_kcal or 0) * multiplier)
                item_prot = (food.protein_g or 0) * multiplier
                item_fat = (food.fat_g or 0) * multiplier
                item_carb = (food.carbs_g or 0) * multiplier
                
                # Check if adding this blows past the target by more than 20%
                if meal_cals + item_cals > (meal_cal_target * 1.2):
                    continue
                    
                meal_items.append(
                    MealItem(
                        food_name=food.display_name or food.food_name_english or food.food_name_swahili or "Unknown Food",
                        quantity=f"{portion_g}g",
                        calories=item_cals,
                        macros=MacroNutrients(
                            protein_g=round(item_prot, 1),
                            fat_g=round(item_fat, 1),
                            carbs_g=round(item_carb, 1)
                        )
                    )
                )
                
                meal_cals += item_cals
                meal_prot += item_prot
                meal_fat += item_fat
                meal_carb += item_carb
                
            meals_data.append(
                Meal(
                    meal_name=meal_name,
                    items=meal_items,
                    total_calories=int(meal_cals),
                    total_macros=MacroNutrients(
                        protein_g=round(meal_prot, 1),
                        fat_g=round(meal_fat, 1),
                        carbs_g=round(meal_carb, 1)
                    )
                )
            )
            
            current_total_cals += meal_cals
            current_total_prot += meal_prot
            current_total_fat += meal_fat
            current_total_carb += meal_carb

        return PlannerResponse(
            meals=meals_data,
            daily_summary=DailySummary(
                total_calories=int(current_total_cals),
                total_macros=MacroNutrients(
                    protein_g=round(current_total_prot, 1),
                    fat_g=round(current_total_fat, 1),
                    carbs_g=round(current_total_carb, 1)
                )
            )
        )
