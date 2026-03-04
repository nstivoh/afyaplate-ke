// frontend/services/plannerService.ts
import { PlannerResponse } from '@/types/planner';
import type { MealPlannerFormValues } from '@/components/meal-planner';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export async function generateMealPlan(
  params: MealPlannerFormValues,
  userToken?: string | null,
): Promise<PlannerResponse> {
  const isAlgo = params.llm_provider.toLowerCase() === 'algorithmic';
  const endpoint = isAlgo ? '/planner/generate-algorithmic' : '/planner/generate';

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (userToken) {
    headers['x-user-token'] = userToken;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
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

