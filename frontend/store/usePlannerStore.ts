import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { PlannerResponse } from '@/types/api';

interface PlannerState {
  plan: PlannerResponse | null;
  setPlan: (plan: PlannerResponse | null) => void;
  clearPlan: () => void;
}

export const usePlannerStore = create<PlannerState>()(
  persist(
    (set) => ({
      plan: null,
      setPlan: (plan) => set({ plan }),
      clearPlan: () => set({ plan: null }),
    }),
    {
      name: 'planner-storage', // name of the item in the storage (must be unique)
    }
  )
);
