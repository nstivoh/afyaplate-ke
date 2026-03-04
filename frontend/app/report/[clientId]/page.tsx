"use client";

import * as React from "react";
import { useParams } from "next/navigation";
import { useLocalStorage } from "@/hooks/use-local-storage";
import { Client } from "@/types";
import { PlannerResponse } from "@/types/planner";
import { Button } from "@/components/ui/button";
import { MealPlanDisplay } from "@/components/meal-plan-display";

export default function ReportPage() {
  const params = useParams();
  const clientId = params.clientId as string;

  const [clients] = useLocalStorage<Client[]>("clients", []);
  const [client, setClient] = React.useState<Client | null>(null);
  const [plan, setPlan] = React.useState<PlannerResponse | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    if (clientId) {
      const foundClient = clients.find(c => c.id === clientId);
      setClient(foundClient || null);
    }
  }, [clientId, clients]);

  React.useEffect(() => {
    const savedPlan = localStorage.getItem(`meal-plan-${clientId}`) || localStorage.getItem('latest-meal-plan');
    if (savedPlan) {
      try {
        setPlan(JSON.parse(savedPlan));
      } catch (e) {
        console.error("Failed to parse saved plan");
      }
    }
    setIsLoading(false);
  }, [clientId]);

  const handlePrint = () => {
    window.print();
  };

  if (isLoading) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        <p className="mt-4 text-lg text-muted-foreground">Loading report...</p>
      </main>
    );
  }

  if (!client) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <p className="text-xl font-semibold">Client not found.</p>
        <Button className="mt-4" onClick={() => window.location.href = '/clients'}>Back to Clients</Button>
      </main>
    );
  }

  if (!plan) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <p className="text-xl font-semibold mb-4">No meal plan found for this client.</p>
        <Button onClick={() => window.location.href = '/planner'}>Generate a Plan</Button>
      </main>
    );
  }

  return (
    <main className="p-8 md:p-12 bg-background text-foreground print:bg-white print:text-black">
      <div className="max-w-4xl mx-auto">
        <header className="flex justify-between items-start mb-12 border-b-4 border-primary pb-4">
          <div>
            <h1 className="text-5xl font-bold text-primary">AfyaPlate KE</h1>
            <p className="text-lg text-muted-foreground">Your Kenyan Nutrition Partner</p>
          </div>
          <div className="text-right">
            <h2 className="text-2xl font-semibold">{client.name}</h2>
            <p className="text-md">{client.email}</p>
          </div>
        </header>

        {plan && <MealPlanDisplay plan={plan} />}

        <div className="mt-12 text-center print:hidden">
          <Button onClick={handlePrint} size="lg">Print Report</Button>
        </div>

        <footer className="mt-16 pt-8 border-t text-center text-xs text-gray-500">
          <p>This meal plan is a suggestion and should be discussed with a qualified nutritionist or doctor.</p>
          <p>&copy; {new Date().getFullYear()} AfyaPlate KE. All rights reserved.</p>
        </footer>
      </div>
    </main>
  );
}
