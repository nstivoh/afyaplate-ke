// frontend/app/planner/page.tsx
import { MealPlannerForm } from "@/components/meal-planner";

export default function PlannerPage() {
  return (
    <main className="flex min-h-screen flex-col items-center p-12 md:p-24">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold tracking-tight text-primary lg:text-5xl">
          AI Meal Planner
        </h1>
        <p className="mt-4 text-lg text-muted-foreground">
          Generate a personalized meal plan based on your needs.
        </p>
      </div>
      <MealPlannerForm />
    </main>
  );
}
