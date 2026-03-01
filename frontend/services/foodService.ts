// frontend/services/foodService.ts
import { Food } from "@/types";
import { fetchWithRetry } from "@/lib/fetchWithRetry";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export async function searchFoods(query: string = "", limit: number = 20): Promise<Food[]> {
  const params = new URLSearchParams({
    query,
    limit: String(limit),
  });

  const response = await fetchWithRetry(`${API_BASE_URL}/foods/?${params.toString()}`);

  if (!response.ok) {
    throw new Error("Failed to fetch foods from the AfyaPlate API.");
  }

  return response.json();
}
