import { FoodSearch } from "@/components/food-search";
import Link from 'next/link';
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight text-primary lg:text-5xl">
          Welcome to AfyaPlate KE
        </h1>
        <p className="mt-4 text-lg text-muted-foreground">
          Your Kenyan Nutrition Partner.
        </p>
        <div className="mt-8 flex justify-center gap-4">
          <Link href="/planner">
            <Button size="lg" className="rounded-full px-8 text-lg shadow-lg">
              Get Started
            </Button>
          </Link>
        </div>
      </div>
      <div className="mt-16 w-full">
        <FoodSearch />
      </div>
    </main>
  );
}
