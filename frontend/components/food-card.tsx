// frontend/components/food-card.tsx
"use client";

import * as React from "react";
import { Food } from "@/types";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";

interface FoodCardProps {
  food: Food;
}

export function FoodCard({ food }: FoodCardProps) {
  const [portionSize, setPortionSize] = React.useState(100);
  const [showDetails, setShowDetails] = React.useState(false);

  const calc = (value: number | undefined) => {
    if (value === undefined || value === null) return "0";
    return ((value / 100) * portionSize).toFixed(1);
  };

  const calories = ((food.energy_kcal || 0) / 100 * portionSize).toFixed(0);

  return (
    <Card className="glassmorphism flex flex-col overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-sm font-bold text-primary line-clamp-2 flex-1" title={food.display_name || food.food_name_english}>
            {food.display_name || food.food_name_english}
          </CardTitle>
          {food.category && (
            <Badge variant="secondary" className="text-[10px] shrink-0 whitespace-nowrap">
              {food.category}
            </Badge>
          )}
        </div>
        {food.food_name_swahili && (
          <p className="text-xs text-muted-foreground mt-1">{food.food_name_swahili}</p>
        )}
      </CardHeader>
      <CardContent className="flex-grow pt-0">
        {/* Primary macros — always visible */}
        <div className="grid grid-cols-4 gap-2 text-center mb-3">
          <div className="bg-primary/5 rounded-lg p-2">
            <p className="text-lg font-bold text-primary">{calories}</p>
            <p className="text-[10px] text-muted-foreground">kcal</p>
          </div>
          <div className="bg-green-500/5 rounded-lg p-2">
            <p className="text-lg font-bold text-green-600">{calc(food.protein_g)}</p>
            <p className="text-[10px] text-muted-foreground">Protein</p>
          </div>
          <div className="bg-amber-500/5 rounded-lg p-2">
            <p className="text-lg font-bold text-amber-600">{calc(food.carbs_g)}</p>
            <p className="text-[10px] text-muted-foreground">Carbs</p>
          </div>
          <div className="bg-rose-500/5 rounded-lg p-2">
            <p className="text-lg font-bold text-rose-600">{calc(food.fat_g)}</p>
            <p className="text-[10px] text-muted-foreground">Fat</p>
          </div>
        </div>

        {/* Expandable minerals section */}
        <button
          className="text-xs text-muted-foreground hover:text-primary transition-colors w-full text-left mb-2"
          onClick={() => setShowDetails(!showDetails)}
        >
          {showDetails ? "▾ Hide details" : "▸ More nutrients"}
        </button>

        {showDetails && (
          <div className="grid grid-cols-4 gap-2 text-center text-xs mb-3 animate-in fade-in-0 slide-in-from-top-1 duration-200">
            <div>
              <p className="font-semibold">{calc(food.fibre_g)}g</p>
              <p className="text-muted-foreground">Fibre</p>
            </div>
            <div>
              <p className="font-semibold">{calc(food.calcium_mg)}mg</p>
              <p className="text-muted-foreground">Calcium</p>
            </div>
            <div>
              <p className="font-semibold">{calc(food.iron_mg)}mg</p>
              <p className="text-muted-foreground">Iron</p>
            </div>
            <div>
              <p className="font-semibold">{calc(food.zinc_mg)}mg</p>
              <p className="text-muted-foreground">Zinc</p>
            </div>
          </div>
        )}

        {/* Portion slider */}
        <div className="mt-auto">
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-xs text-muted-foreground">Portion</span>
            <span className="text-xs font-bold text-primary">{portionSize}g</span>
          </div>
          <Slider
            defaultValue={[100]}
            max={500}
            step={5}
            onValueChange={(value) => setPortionSize(value[0])}
          />
        </div>
      </CardContent>
    </Card>
  );
}
