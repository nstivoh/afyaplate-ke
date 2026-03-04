export interface Client {
    id: string | number;
    name: string;
    email?: string;
    notes?: string;
    age: number | null;
    weight_kg: number | null;
    health_goal: string | null;
    target_calories: number | null;
    protein_grams: number | null;
    fat_grams: number | null;
    carb_grams: number | null;
    dietary_restrictions: string | null;
}
