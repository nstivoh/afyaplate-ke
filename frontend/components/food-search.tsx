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
    "food_name_swahili"
  ],
  threshold: 0.3,
};

export function FoodSearch() {
  const [query, setQuery] = React.useState("");
  const [results, setResults] = React.useState<Food[]>([]);
  const [allFoods, setAllFoods] = React.useState<Food[]>([]);
  const fuseRef = React.useRef<Fuse<Food> | null>(null);

  React.useEffect(() => {
    async function loadFoods() {
      try {
        const foods = await searchFoods("", 1000); 
        setAllFoods(foods);
        fuseRef.current = new Fuse(foods, fuseOptions);
        setResults(foods.slice(0, 12)); // Show some initial results
      } catch (error) {
        console.error(error);
      }
    }
    loadFoods();
  }, []);

  React.useEffect(() => {
    if (query.trim() === "") {
      setResults(allFoods.slice(0, 12)); // Show initial results when query is cleared
      return;
    }

    if (fuseRef.current) {
      const searchResults = fuseRef.current.search(query);
      setResults(searchResults.map(result => result.item));
    }
  }, [query, allFoods]);

  return (
    <div className="w-full max-w-4xl mx-auto">
      <Input
        type="search"
        placeholder="Search for food (e.g., 'Sukuma Wiki' or 'Kale')"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="w-full text-lg p-6 rounded-full glassmorphism"
      />
      <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {results.map((food) => (
          <FoodCard key={food.food_code} food={food} />
        ))}
      </div>
    </div>
  );
}
