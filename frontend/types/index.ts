// frontend/types/index.ts
export interface Food {
  food_code: string;
  food_name_english?: string;
  food_name_swahili?: string;
  category?: string;
  display_name?: string;
  energy_kcal?: number;
  protein_g?: number;
  fat_g?: number;
  carbs_g?: number;
  fibre_g?: number;
  calcium_mg?: number;
  iron_mg?: number;
  zinc_mg?: number;
}

export type { Client } from './client';
