// frontend/services/dataService.ts

import { fetchWithRetry } from "@/lib/fetchWithRetry";

export interface PriceInfo {
  price: number;
  unit: string;
}

export type PricingData = Record<string, PriceInfo>;

export async function getPricingData(): Promise<PricingData> {
  // We are assuming the backend serves the data folder statically for now.
  // In a real app, this should be a dedicated, secured API endpoint.
  const baseUrl = typeof window !== 'undefined' ? '' : (process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000');
  const response = await fetchWithRetry(`${baseUrl}/data/prices_nairobi_2026.json`);

  if (!response.ok) {
    throw new Error("Failed to fetch pricing data.");
  }

  return response.json();
}
