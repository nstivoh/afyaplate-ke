# backend/app/services/algo_service.py
import random
from typing import List, Dict, Any, Optional
from app.db.database import SessionLocal
from app.models.sql_models import SQLFood
from app.schemas.planner import PlannerRequest, PlannerResponse, Meal, MealItem, DailySummary, MacroNutrients


# Realistic Kenyan meal templates: each entry is (role, keywords, portion_range_g)
BREAKFAST_TEMPLATE = [
    ("starch", ["porridge", "uji", "bread", "chapati", "mandazi", "cereal", "millet", "sorghum"], (150, 500)),
    ("protein", ["egg", "milk", "yoghurt", "beans", "groundnut"], (100, 400)),
    ("beverage", ["tea", "coffee", "juice", "cocoa"], (200, 500)),
]

LUNCH_TEMPLATE = [
    ("starch", ["ugali", "rice", "chapati", "matoke", "potato", "spaghetti", "maize"], (200, 600)),
    ("protein", ["beans", "lentils", "ndengu", "peas", "githeri", "fish", "beef", "chicken", "egg"], (150, 500)),
    ("vegetable", ["sukuma", "spinach", "cabbage", "kale", "managu", "terere", "kunde"], (100, 350)),
]

DINNER_TEMPLATE = [
    ("starch", ["ugali", "rice", "chapati", "potato", "cassava", "yam", "arrow"], (200, 600)),
    ("protein", ["stew", "beans", "lentils", "ndengu", "fish", "chicken", "beef", "maharagwe", "kamande"], (150, 500)),
    ("vegetable", ["sukuma", "spinach", "cabbage", "pumpkin", "carrot", "tomato"], (100, 350)),
]

SNACK_TEMPLATE = [
    ("snack", ["groundnut", "banana", "mango", "avocado", "sweet potato", "arrowroot", "cassava", "fruit", "biscuit", "mandazi"], (100, 400)),
]


class AlgoService:
    def __init__(self):
        pass

    def _load_all_foods(self, dietary_restrictions: str = "") -> List[SQLFood]:
        """Load all foods and apply dietary filtering."""
        with SessionLocal() as db:
            foods = db.query(SQLFood).filter(SQLFood.energy_kcal > 0).all()
            db.expunge_all()

        forbidden_keywords = []
        if dietary_restrictions:
            dr = dietary_restrictions.lower()
            if "vegetarian" in dr or "vegan" in dr:
                forbidden_keywords.extend(["beef", "chicken", "fish", "meat", "pork", "mbuzi", "nyama", "goat", "lamb", "sausage", "bacon"])
            if "gluten-free" in dr or "gluten free" in dr:
                forbidden_keywords.extend(["bread", "wheat", "chapati", "mandazi", "cake", "pasta", "spaghetti", "biscuit"])

        if forbidden_keywords:
            foods = [f for f in foods if not any(kw in (f.display_name or "").lower() for kw in forbidden_keywords)]

        return foods

    def _find_foods_for_role(self, all_foods: List[SQLFood], keywords: List[str], limit: int = 3) -> List[SQLFood]:
        """Find foods matching keywords for a specific meal role."""
        matched = [f for f in all_foods if any(k in (f.display_name or "").lower() for k in keywords)]
        if len(matched) < limit:
            # Supplement with random foods if not enough matches
            remaining = [f for f in all_foods if f not in matched]
            matched.extend(random.sample(remaining, min(limit - len(matched), len(remaining))))
        return random.sample(matched, min(limit, len(matched)))

    def _get_meal_template(self, meal_index: int, meals_count: int):
        """Get the appropriate meal template based on meal index."""
        if meal_index == 0:
            return "Breakfast", BREAKFAST_TEMPLATE
        elif meal_index == meals_count - 1:
            return "Dinner", DINNER_TEMPLATE
        elif meal_index == 1:
            return "Lunch", LUNCH_TEMPLATE
        else:
            return "Snack", SNACK_TEMPLATE

    def generate_algorithmic_plan(self, request: PlannerRequest) -> PlannerResponse:
        """
        Generate a realistic Kenyan meal plan using structured templates.
        """
        target_cals = request.target_calories
        target_prot = request.protein_grams or int(target_cals * 0.15 / 4)
        target_fat = request.fat_grams or int(target_cals * 0.30 / 9)
        target_carb = request.carb_grams or int(target_cals * 0.55 / 4)

        meals_count = request.num_meals
        dr_string = ", ".join(request.dietary_restrictions) if request.dietary_restrictions else ""
        all_foods = self._load_all_foods(dietary_restrictions=dr_string)

        if not all_foods:
            raise ValueError("No foods available in the database. Please seed the database first.")

        meals_data = []
        # Distribute calories: breakfast ~25%, lunch ~35%, dinner ~30%, snacks ~10%
        cal_distribution = self._get_calorie_distribution(meals_count, target_cals)

        current_total_cals = 0
        current_total_prot = 0.0
        current_total_fat = 0.0
        current_total_carb = 0.0

        used_foods = set()  # Track used foods to avoid repetition

        for i in range(meals_count):
            meal_name, template = self._get_meal_template(i, meals_count)
            meal_cal_target = cal_distribution[i]
            meal_items = []
            meal_cals = 0
            meal_prot = 0.0
            meal_fat = 0.0
            meal_carb = 0.0

            for role, keywords, portion_range in template:
                # Find a food for this role that hasn't been used yet
                candidates = self._find_foods_for_role(all_foods, keywords, limit=5)
                candidates = [c for c in candidates if c.id not in used_foods] or candidates

                if not candidates:
                    continue

                food = random.choice(candidates)
                used_foods.add(food.id)

                # Calculate portion to fit calorie budget for this role
                role_cal_budget = meal_cal_target / len(template)
                if food.energy_kcal and food.energy_kcal > 0:
                    ideal_portion = (role_cal_budget / food.energy_kcal) * 100
                    # Round to nearest 25g for realism
                    ideal_portion = round(ideal_portion / 25) * 25
                    # Clamp to reasonable range
                    portion_g = max(portion_range[0], min(portion_range[1], int(ideal_portion)))
                else:
                    portion_g = random.randint(*portion_range)

                multiplier = portion_g / 100.0
                item_cals = int((food.energy_kcal or 0) * multiplier)
                item_prot = round((food.protein_g or 0) * multiplier, 1)
                item_fat = round((food.fat_g or 0) * multiplier, 1)
                item_carb = round((food.carbs_g or 0) * multiplier, 1)

                # Format quantity nicely
                if portion_g >= 200:
                    qty_str = f"{portion_g}g (~{round(portion_g/250, 1)} cups)"
                else:
                    qty_str = f"{portion_g}g"

                meal_items.append(
                    MealItem(
                        food_name=food.display_name or food.food_name_english or "Unknown Food",
                        quantity=qty_str,
                        calories=item_cals,
                        macros=MacroNutrients(
                            protein_g=item_prot,
                            fat_g=item_fat,
                            carbs_g=item_carb
                        )
                    )
                )

                meal_cals += item_cals
                meal_prot += item_prot
                meal_fat += item_fat
                meal_carb += item_carb

            if meal_items:
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

    def _get_calorie_distribution(self, meals_count: int, total_cals: int) -> List[int]:
        """Distribute calories across meals realistically."""
        if meals_count == 1:
            return [total_cals]
        elif meals_count == 2:
            return [int(total_cals * 0.45), int(total_cals * 0.55)]
        elif meals_count == 3:
            return [int(total_cals * 0.25), int(total_cals * 0.40), int(total_cals * 0.35)]
        elif meals_count == 4:
            return [int(total_cals * 0.25), int(total_cals * 0.35), int(total_cals * 0.10), int(total_cals * 0.30)]
        else:
            # 5 meals: breakfast, lunch, snack, snack, dinner
            return [
                int(total_cals * 0.22),
                int(total_cals * 0.30),
                int(total_cals * 0.08),
                int(total_cals * 0.08),
                int(total_cals * 0.32),
            ]
