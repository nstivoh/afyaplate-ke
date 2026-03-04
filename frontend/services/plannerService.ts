// frontend/services/plannerService.ts
import { PlannerResponse } from '@/types/planner';
import type { MealPlannerFormValues } from '@/components/meal-planner';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export async function generateMealPlan(params: MealPlannerFormValues): Promise<PlannerResponse> {
  const isAlgo = params.llm_provider.toLowerCase() === 'algorithmic';
  const endpoint = isAlgo ? '/planner/generate-algorithmic' : '/planner/generate';

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    let detail = 'Failed to generate meal plan';
    try {
      const errorData = await response.json();
      detail = errorData.detail || detail;
    } catch { }
    throw new Error(detail);
  }

  return response.json();
}
