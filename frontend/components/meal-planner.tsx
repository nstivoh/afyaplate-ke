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
import { usePlannerStore } from "@/store/usePlannerStore";
import { ClientSelector } from "@/components/client-selector";
import { Client } from "@/types/client";
const MealPlanDisplay = React.lazy(() => import('./meal-plan-display').then(module => ({ default: module.MealPlanDisplay })));
import { Loader2 } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const formSchema = z.object({
  target_calories: z.coerce.number().min(1000, "Must be at least 1000 calories"),
  protein_grams: z.coerce.number().optional(),
  fat_grams: z.coerce.number().optional(),
  carb_grams: z.coerce.number().optional(),
  dietary_restrictions: z.array(z.string()).default([]),
  num_meals: z.coerce.number().min(1, "Must have at least 1 meal").max(5, "Cannot have more than 5 meals"),
  llm_api_key: z.string().optional(),
  llm_provider: z.string().min(1, "Provider is Required"),
  llm_model: z.string().min(1, "Model is Required"),
});

export type MealPlannerFormValues = z.infer<typeof formSchema>;

const dietaryOptions = ["vegetarian", "gluten-free", "vegan", "pescatarian"];

export function MealPlannerForm() {
  const { plan, setPlan } = usePlannerStore();
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema) as any,
    defaultValues: {
      target_calories: 2200,
      num_meals: 3,
      dietary_restrictions: [],
      llm_api_key: "",
      llm_provider: "gemini",
      llm_model: "gemini-2.5-flash",
    },
  });

  async function onSubmit(values: MealPlannerFormValues) {
    setIsLoading(true);
    setError(null);
    setPlan(null);
    try {
      const payload = { ...values };
      if (!payload.llm_api_key) {
        delete payload.llm_api_key;
      }

      const response = await generateMealPlan(payload as any);
      setPlan(response);
      localStorage.setItem('latest-meal-plan', JSON.stringify(response));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  const handleClientSelect = (client: Client) => {
    form.setValue("target_calories", client.target_calories ?? 2200);
    form.setValue("num_meals", 3);

    // Explicit undefined casting for optional fields
    form.setValue("protein_grams", client.protein_grams ?? undefined);
    form.setValue("fat_grams", client.fat_grams ?? undefined);
    form.setValue("carb_grams", client.carb_grams ?? undefined);

    if (client.dietary_restrictions && client.dietary_restrictions.length > 0) {
      const restrictions = client.dietary_restrictions.split(',').map(r => r.trim());
      form.setValue("dietary_restrictions", restrictions);
    } else {
      form.setValue("dietary_restrictions", []);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="glassmorphism p-8 rounded-lg mb-8">
        <ClientSelector onSelectClient={handleClientSelect} />

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <FormField
                control={form.control}
                name="target_calories"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Target Calories</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        placeholder="e.g., 2200"
                        name={field.name}
                        onBlur={field.onBlur}
                        disabled={field.disabled}
                        ref={field.ref}
                        value={field.value ?? ""}
                        onChange={(e) => field.onChange(e.target.value === "" ? "" : Number(e.target.value))}
                      />
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
                      <Input
                        type="number"
                        placeholder="e.g., 3"
                        name={field.name}
                        onBlur={field.onBlur}
                        disabled={field.disabled}
                        ref={field.ref}
                        value={field.value ?? ""}
                        onChange={(e) => field.onChange(e.target.value === "" ? "" : Number(e.target.value))}
                      />
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
                      <Input
                        type="number"
                        placeholder="Optional"
                        name={field.name}
                        onBlur={field.onBlur}
                        disabled={field.disabled}
                        ref={field.ref}
                        value={field.value ?? ""}
                        onChange={(e) => field.onChange(e.target.value === "" ? undefined : Number(e.target.value))}
                      />
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
                      <Input
                        type="number"
                        placeholder="Optional"
                        name={field.name}
                        onBlur={field.onBlur}
                        disabled={field.disabled}
                        ref={field.ref}
                        value={field.value ?? ""}
                        onChange={(e) => field.onChange(e.target.value === "" ? undefined : Number(e.target.value))}
                      />
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
                      <Input
                        type="number"
                        placeholder="Optional"
                        name={field.name}
                        onBlur={field.onBlur}
                        disabled={field.disabled}
                        ref={field.ref}
                        value={field.value ?? ""}
                        onChange={(e) => field.onChange(e.target.value === "" ? undefined : Number(e.target.value))}
                      />
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
            <div className="glassmorphism p-6 rounded-lg mt-8 space-y-6">
              <h3 className="text-xl font-bold text-primary mb-4">AI Configuration</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <FormField
                  control={form.control}
                  name="llm_provider"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Provider</FormLabel>
                      <FormControl>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select Provider" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="gemini">Google Gemini</SelectItem>
                            <SelectItem value="openai">OpenAI (ChatGPT)</SelectItem>
                            <SelectItem value="anthropic">Anthropic (Claude)</SelectItem>
                            <SelectItem value="groq">Groq</SelectItem>
                            <SelectItem value="qwen">Qwen</SelectItem>
                            <SelectItem value="algorithmic">Algorithmic Planner (Free / Offline)</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="llm_model"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Model String</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. gemini-1.5-pro" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            <Button type="submit" disabled={isLoading} className="w-full text-lg py-6 mt-8">
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {isLoading ? "Generating Your AfyaPlate..." : "Generate Meal Plan"}
            </Button>
          </form>
        </Form>
      </div>

      {error && <div className="mt-8 text-center text-red-500 glassmorphism p-4">{error}</div>}

      <React.Suspense fallback={<div className="mt-8 text-center"><Loader2 className="mx-auto h-8 w-8 animate-spin" /></div>}>
        {plan && <MealPlanDisplay plan={plan} />}
      </React.Suspense>
    </div>
  );
}
