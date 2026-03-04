// frontend/services/plannerService.ts
import { PlannerRequest, PlannerResponse } from '@/types/planner';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export async function generateMealPlan(params: MealPlanParams): Promise<PlannerResponse> {
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
    throw new Error('Failed to generate meal plan');
  }

  return response.json();
}
