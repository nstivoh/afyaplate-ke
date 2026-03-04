// frontend/components/food-search.tsx
"use client";

import * as React from "react";
import { Input } from "@/components/ui/input";
import { searchFoods } from "@/services/foodService";
import { Food } from "@/types";
import Fuse from "fuse.js";
import { FoodCard } from "./food-card";

const fuseOptions = {
  keys: [
    "food_name_english",
    "food_name_swahili",
    "display_name"
  ],
  threshold: 0.3,
};

export function FoodSearch() {
  const [query, setQuery] = React.useState("");
  const [results, setResults] = React.useState<Food[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const foods = await searchFoods(query, 24);
        setResults(foods);
      } finally {
        setIsLoading(false);
      }
    }, 300); // 300ms debounce
    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div className="w-full max-w-4xl mx-auto">
      <Input
        type="search"
        placeholder="Search for food (e.g., 'Sukuma Wiki' or 'Kale')"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="w-full text-lg p-6 rounded-full glassmorphism"
      />

      {isLoading ? (
        <div className="mt-12 flex justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : results.length === 0 && query ? (
        <div className="mt-12 text-center text-muted-foreground glassmorphism p-8 rounded-lg">
          No foods found for "{query}". Try a different search term.
        </div>
      ) : (
        <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {results.map((food, idx) => (
            <FoodCard key={`${food.food_code}-${idx}`} food={food} />
          ))}
        </div>
      )}
    </div>
  );
}
