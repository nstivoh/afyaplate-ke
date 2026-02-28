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

interface FoodCardProps {
  food: Food;
}

export function FoodCard({ food }: FoodCardProps) {
  const [portionSize, setPortionSize] = React.useState(100); // Default portion size in grams

  const calculateNutrient = (value: number | undefined) => {
    if (value === undefined) return "N/A";
    return ((value / 100) * portionSize).toFixed(1);
  };

  const calories = (food.energy_kcal / 100 * portionSize).toFixed(0);

  return (
    <Card className="glassmorphism flex flex-col">
      <CardHeader>
        <CardTitle className="text-lg font-bold text-primary h-12">
          {food.food_name_english}
        </CardTitle>
        <p className="text-sm text-muted-foreground">{food.food_name_swahili}</p>
      </CardHeader>
      <CardContent className="flex-grow">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="font-semibold">Calories</p>
            <p>{calories ?? "N/A"} kcal</p>
          </div>
          <div>
            <p className="font-semibold">Protein</p>
            <p>{calculateNutrient(food.protein_g)} g</p>
          </div>
          <div>
            <p className="font-semibold">Carbs</p>
            <p>{calculateNutrient(food.carbs_g)} g</p>
          </div>
          <div>
            <p className="font-semibold">Fat</p>
            <p>{calculateNutrient(food.fat_g)} g</p>
          </div>
        </div>
        <div className="mt-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium">Portion Size</span>
            <span className="text-sm font-bold text-primary">{portionSize}g</span>
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
