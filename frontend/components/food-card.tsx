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
    <Card className="glassmorphism flex flex-col overflow-hidden hover:shadow-md hover:-translate-y-1 transition-all duration-300">
      <CardHeader className="pb-3">
        <div className="flex flex-col gap-2">
          <CardTitle className="text-sm font-bold text-primary leading-tight" title={food.display_name || food.food_name_english}>
            {food.display_name || food.food_name_english}
          </CardTitle>
          {food.category && (
            <Badge variant="secondary" className="text-[10px] w-fit">
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
        <div className="grid grid-cols-2 gap-2 text-center mb-3">
          <div className="bg-primary/5 rounded-lg p-2.5 flex flex-col items-center justify-center">
            <p className="text-xl font-bold text-primary leading-none">{calories}</p>
            <p className="text-xs text-muted-foreground mt-1">kcal</p>
          </div>
          <div className="bg-green-500/5 rounded-lg p-2.5 flex flex-col items-center justify-center">
            <p className="text-lg font-bold text-green-600 leading-none">{calc(food.protein_g)}<span className="text-xs font-normal">g</span></p>
            <p className="text-xs text-muted-foreground mt-1">Protein</p>
          </div>
          <div className="bg-amber-500/5 rounded-lg p-2.5 flex flex-col items-center justify-center">
            <p className="text-lg font-bold text-amber-600 leading-none">{calc(food.carbs_g)}<span className="text-xs font-normal">g</span></p>
            <p className="text-xs text-muted-foreground mt-1">Carbs</p>
          </div>
          <div className="bg-rose-500/5 rounded-lg p-2.5 flex flex-col items-center justify-center">
            <p className="text-lg font-bold text-rose-600 leading-none">{calc(food.fat_g)}<span className="text-xs font-normal">g</span></p>
            <p className="text-xs text-muted-foreground mt-1">Fat</p>
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
          <div className="grid grid-cols-2 gap-2 text-center mb-3 animate-in fade-in-0 slide-in-from-top-1 duration-200">
            <div className="bg-secondary/20 rounded-lg p-2">
              <p className="font-semibold text-sm leading-none">{calc(food.fibre_g)}<span className="text-xs font-normal text-muted-foreground">g</span></p>
              <p className="text-xs text-muted-foreground mt-1">Fibre</p>
            </div>
            <div className="bg-secondary/20 rounded-lg p-2">
              <p className="font-semibold text-sm leading-none">{calc(food.calcium_mg)}<span className="text-xs font-normal text-muted-foreground">mg</span></p>
              <p className="text-xs text-muted-foreground mt-1">Calcium</p>
            </div>
            <div className="bg-secondary/20 rounded-lg p-2">
              <p className="font-semibold text-sm leading-none">{calc(food.iron_mg)}<span className="text-xs font-normal text-muted-foreground">mg</span></p>
              <p className="text-xs text-muted-foreground mt-1">Iron</p>
            </div>
            <div className="bg-secondary/20 rounded-lg p-2">
              <p className="font-semibold text-sm leading-none">{calc(food.zinc_mg)}<span className="text-xs font-normal text-muted-foreground">mg</span></p>
              <p className="text-xs text-muted-foreground mt-1">Zinc</p>
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
