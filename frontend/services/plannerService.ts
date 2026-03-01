// frontend/services/plannerService.ts
import { PlannerRequest, PlannerResponse } from "@/types/planner";
import { fetchWithRetry } from "@/lib/fetchWithRetry";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export async function generateMealPlan(request: PlannerRequest): Promise<PlannerResponse> {
  const response = await fetchWithRetry(`${API_BASE_URL}/planner/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Failed to generate meal plan." }));
    throw new Error(errorData.detail);
  }

  return response.json();
}
