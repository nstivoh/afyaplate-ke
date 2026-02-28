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
  
  React.useEffect(() => {
    if (clientId) {
      const foundClient = clients.find(c => c.id === clientId);
      setClient(foundClient || null);
    }
  }, [clientId, clients]);

  React.useEffect(() => {
    const savedPlan = localStorage.getItem('latest-meal-plan');
    if (savedPlan) {
      setPlan(JSON.parse(savedPlan));
    }
  }, []);

  const handlePrint = () => {
    window.print();
  };

  if (!client || !plan) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <p>Loading report...</p>
      </main>
    );
  }

  return (
    <main className="p-8 md:p-12 bg-white text-black">
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
