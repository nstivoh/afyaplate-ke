// frontend/types/planner.ts

export interface PlannerRequest {
  target_calories: number;
  protein_grams?: number;
  fat_grams?: number;
  carb_grams?: number;
  dietary_restrictions?: string[];
  num_meals?: number;
  llm_provider: string;
  llm_model: string;
  llm_api_key?: string;
}

export interface MacroNutrients {
  protein_g: number;
  fat_g: number;
  carbs_g: number;
}

export interface MealItem {
  food_name: string;
  quantity: string;
  calories: number;
  macros: MacroNutrients;
}

export interface Meal {
  meal_name: string;
  items: MealItem[];
  total_calories: number;
  total_macros: MacroNutrients;
}

export interface DailySummary {
  total_calories: number;
  total_macros: MacroNutrients;
}

export interface PlannerResponse {
  meals: Meal[];
  daily_summary: DailySummary;
}
