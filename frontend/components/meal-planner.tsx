"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { generateMealPlan } from "@/services/plannerService";
import { PlannerResponse } from "@/types/planner";
const MealPlanDisplay = React.lazy(() => import('./meal-plan-display').then(module => ({ default: module.MealPlanDisplay })));
import { Loader2 } from "lucide-react";

const formSchema = z.object({
  target_calories: z.coerce.number().min(1000, "Must be at least 1000 calories"),
  protein_grams: z.coerce.number().optional(),
  fat_grams: z.coerce.number().optional(),
  carb_grams: z.coerce.number().optional(),
  dietary_restrictions: z.array(z.string()).optional(),
  num_meals: z.coerce.number().min(1, "Must have at least 1 meal").max(5, "Cannot have more than 5 meals"),
});

const dietaryOptions = ["vegetarian", "gluten-free", "vegan", "pescatarian"];

export function MealPlannerForm() {
  const [plan, setPlan] = React.useState<PlannerResponse | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      target_calories: 2200,
      num_meals: 3,
      dietary_restrictions: [],
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsLoading(true);
    setError(null);
    setPlan(null);
    try {
      const response = await generateMealPlan(values);
      setPlan(response);
      localStorage.setItem('latest-meal-plan', JSON.stringify(response));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8 glassmorphism p-8 rounded-lg">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <FormField
              control={form.control}
              name="target_calories"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Target Calories</FormLabel>
                  <FormControl>
                    <Input type="number" placeholder="e.g., 2200" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="num_meals"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Number of Meals</FormLabel>
                  <FormControl>
                    <Input type="number" placeholder="e.g., 3" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="protein_grams"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Protein (g)</FormLabel>
                  <FormControl>
                    <Input type="number" placeholder="Optional" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="fat_grams"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Fat (g)</FormLabel>
                  <FormControl>
                    <Input type="number" placeholder="Optional" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="carb_grams"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Carbs (g)</FormLabel>
                  <FormControl>
                    <Input type="number" placeholder="Optional" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          
          <FormField
            control={form.control}
            name="dietary_restrictions"
            render={() => (
              <FormItem>
                <div className="mb-4">
                  <FormLabel className="text-base">Dietary Restrictions</FormLabel>
                </div>
                <div className="grid grid-cols-2 gap-4">
                {dietaryOptions.map((item) => (
                  <FormField
                    key={item}
                    control={form.control}
                    name="dietary_restrictions"
                    render={({ field }) => {
                      return (
                        <FormItem
                          key={item}
                          className="flex flex-row items-start space-x-3 space-y-0"
                        >
                          <FormControl>
                            <Checkbox
                              checked={field.value?.includes(item)}
                              onCheckedChange={(checked) => {
                                return checked
                                  ? field.onChange([...(field.value || []), item])
                                  : field.onChange(
                                      field.value?.filter(
                                        (value) => value !== item
                                      )
                                    );
                              }}
                            />
                          </FormControl>
                          <FormLabel className="font-normal capitalize">
                            {item}
                          </FormLabel>
                        </FormItem>
                      );
                    }}
                  />
                ))}
                </div>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit" disabled={isLoading} className="w-full text-lg py-6">
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isLoading ? "Generating Your AfyaPlate..." : "Generate Meal Plan"}
          </Button>
        </form>
      </Form>
      
      {error && <div className="mt-8 text-center text-red-500 glassmorphism p-4">{error}</div>}
      
      <React.Suspense fallback={<div className="mt-8 text-center"><Loader2 className="mx-auto h-8 w-8 animate-spin" /></div>}>
        {plan && <MealPlanDisplay plan={plan} />}
      </React.Suspense>
    </div>
  );
}
