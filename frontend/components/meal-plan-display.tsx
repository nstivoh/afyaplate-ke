"use client";

import * as React from "react";
import { PlannerResponse, Meal, MealItem } from "@/types/planner";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";
import { getPricingData, PricingData } from "@/services/dataService";
import { MacroChart } from "./macro-chart";
import {
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  useSortable,
  rectSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

interface MealPlanDisplayProps {
  plan: PlannerResponse;
}

const SwapSuggestions = ({ item, onSwap }: { item: MealItem, onSwap: (newItemName: string) => void }) => {
  const suggestions: { [key: string]: string[] } = {
    "Sukuma Wiki": ["Spinach", "Cabbage", "Amarnath Greens (Mchicha)"],
    "Ugali": ["Brown Ugali", "Rice", "Chapati"],
    "Chicken Breast": ["Fish (Tilapia)", "Beef (Lean)", "Lentils (Ndengu)"],
  };

  const getSuggestions = (foodName: string) => {
    const key = Object.keys(suggestions).find(k => foodName.toLowerCase().includes(k.toLowerCase()));
    return key ? suggestions[key] : ["No suggestions available"];
  }

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm" className="ml-2">Swap</Button>
      </PopoverTrigger>
      <PopoverContent className="w-48 p-2">
        <ul className="space-y-1">
          {getSuggestions(item.food_name).map(suggestion => (
            <li key={suggestion}>
              <Button variant="ghost" size="sm" className="w-full justify-start" onClick={() => onSwap(suggestion)}>
                {suggestion}
              </Button>
            </li>
          ))}
        </ul>
      </PopoverContent>
    </Popover>
  )
}

const MealCard = ({ meal, onSwapItem, pricingData }: { meal: Meal, onSwapItem: (mealName: string, itemIndex: number, newItemName: string) => void, pricingData: PricingData }) => {

  const findPrice = (foodName: string) => {
    const key = Object.keys(pricingData).find(k => foodName.toLowerCase().includes(k));
    return key ? pricingData[key] : null;
  }

  return (
    <Card className="glassmorphism h-full">
      <CardHeader>
        <CardTitle className="text-xl text-primary">{meal.meal_name}</CardTitle>
        <p className="text-sm text-muted-foreground">{meal.total_calories} calories</p>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {meal.items.map((item, index) => {
            const priceInfo = findPrice(item.food_name);
            return (
              <li key={index} className="flex justify-between items-center text-sm border-b border-border/50 pb-2">
                <div>
                  <p className="font-semibold">{item.food_name}</p>
                  <p className="text-xs text-muted-foreground">{item.quantity}</p>
                  {priceInfo && <p className="text-xs text-primary font-semibold">KES {priceInfo.price} / {priceInfo.unit}</p>}
                </div>
                <SwapSuggestions item={item} onSwap={(newItemName) => onSwapItem(meal.meal_name, index, newItemName)} />
              </li>
            )
          })}
        </ul>
      </CardContent>
    </Card>
  );
};

function SortableMealCard({ meal, onSwapItem, pricingData }: { meal: Meal, onSwapItem: (mealName: string, itemIndex: number, newItemName: string) => void, pricingData: PricingData }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id: meal.meal_name });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <MealCard meal={meal} onSwapItem={onSwapItem} pricingData={pricingData} />
    </div>
  );
}

export function MealPlanDisplay({ plan: initialPlan }: MealPlanDisplayProps) {
  const [plan, setPlan] = React.useState(initialPlan);
  const [pricingData, setPricingData] = React.useState<PricingData>({});

  React.useEffect(() => {
    setPlan(initialPlan);
  }, [initialPlan]);

  React.useEffect(() => {
    getPricingData().then(setPricingData).catch(console.error);
  }, []);

  const sensors = useSensors(useSensor(PointerSensor));

  const [isExporting, setIsExporting] = React.useState(false);

  const exportToPdf = async () => {
    setIsExporting(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/planner/export-pdf", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(plan),
      });

      if (!response.ok) throw new Error("Export failed");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "afyaplate_meal_plan.pdf";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error("PDF Export Error:", err);
      alert("Failed to export PDF. Please try again.");
    } finally {
      setIsExporting(false);
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      setPlan((currentPlan) => {
        const oldIndex = currentPlan.meals.findIndex((m) => m.meal_name === active.id);
        const newIndex = currentPlan.meals.findIndex((m) => m.meal_name === over.id);
        const newMeals = arrayMove(currentPlan.meals, oldIndex, newIndex);
        return { ...currentPlan, meals: newMeals };
      });
    }
  };

  const handleSwapItem = (mealName: string, itemIndex: number, newItemName: string) => {
    setPlan(currentPlan => {
      const newPlan = JSON.parse(JSON.stringify(currentPlan));
      const mealToUpdate = newPlan.meals.find((m: Meal) => m.meal_name === mealName);
      if (mealToUpdate) {
        mealToUpdate.items[itemIndex].food_name = newItemName;
      }
      return newPlan;
    });
  };

  const totalCost = React.useMemo(() => {
    let cost = 0;
    plan.meals.forEach(meal => {
      meal.items.forEach(item => {
        const key = Object.keys(pricingData).find(k => item.food_name.toLowerCase().includes(k));
        if (key) {
          const priceInfo = pricingData[key];
          if (priceInfo.unit === 'piece') {
            const quantity = parseInt(item.quantity.split(' ')[0]) || 1;
            cost += priceInfo.price * quantity;
          }
        }
      });
    });
    return cost;
  }, [plan, pricingData]);

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={plan.meals.map(m => m.meal_name)} strategy={rectSortingStrategy}>
        <div className="mt-12 w-full">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold">Your Daily Meal Plan</h2>
            <Button onClick={exportToPdf} disabled={isExporting} variant="default" className="bg-primary text-white">
              {isExporting ? "Exporting..." : "Download PDF"}
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {plan.meals.map((meal) => (
              <SortableMealCard key={meal.meal_name} meal={meal} onSwapItem={handleSwapItem} pricingData={pricingData} />
            ))}
          </div>
          <div className="mt-8 p-6 glassmorphism rounded-lg">
            <h3 className="text-2xl font-bold text-center">Daily Summary</h3>
            <div className="flex flex-col md:flex-row items-center justify-center gap-8 mt-4">
              <div className="w-full md:w-1/2">
                <MacroChart macros={plan.daily_summary.total_macros} />
              </div>
              <div className="flex flex-wrap justify-center gap-8">
                <div>
                  <p className="font-semibold text-lg">{plan.daily_summary.total_calories}</p>
                  <p className="text-sm text-muted-foreground">Total Calories</p>
                </div>
                <div>
                  <p className="font-semibold text-lg text-primary">KES {totalCost.toFixed(2)}</p>
                  <p className="text-sm text-muted-foreground">Est. Daily Cost</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </SortableContext>
    </DndContext>
  );
}
