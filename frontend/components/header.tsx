"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Menu, Sparkles, Clock } from "lucide-react";
import { PricingModal } from "./pricing-modal";
import { useSubscription } from "@/contexts/SubscriptionContext";

export function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [pricingOpen, setPricingOpen] = useState(false);
  const { plan, isActive, trialDaysLeft, isLoading } = useSubscription();

  const isProOrTrial = isActive;

  return (
    <>
      <header className="w-full px-8 py-4 flex justify-between items-center glassmorphism fixed top-0 left-0 right-0 z-50 backdrop-blur-sm">
        <Link href="/" className="text-2xl font-bold text-primary">
          AfyaPlate KE
        </Link>
        <nav className="hidden md:flex gap-6 items-center">
          <Link href="/" className="text-sm font-medium hover:text-primary">
            Food Search
          </Link>
          <Link href="/planner" className="text-sm font-medium hover:text-primary">
            AI Planner
          </Link>
          <Link href="/clients" className="text-sm font-medium hover:text-primary">
            Clients
          </Link>
        </nav>
        <div className="flex items-center gap-3">
          {/* Subscription status badge */}
          {!isLoading && isProOrTrial && (
            <Badge
              variant={plan === "pro" ? "default" : "secondary"}
              className="hidden md:flex items-center gap-1 text-xs cursor-pointer"
              onClick={() => setPricingOpen(true)}
            >
              {plan === "trial" ? (
                <>
                  <Clock className="h-3 w-3" />
                  {trialDaysLeft}d trial
                </>
              ) : (
                <>
                  <Sparkles className="h-3 w-3" />
                  Pro
                </>
              )}
            </Badge>
          )}

          <Button
            onClick={() => setPricingOpen(true)}
            variant={isProOrTrial ? "outline" : "default"}
            size="sm"
          >
            {isLoading ? "..." : isProOrTrial ? "Manage Plan" : "Go Pro"}
          </Button>

          <button className="md:hidden" onClick={() => setMenuOpen(!menuOpen)}>
            <Menu className="h-6 w-6" />
          </button>
        </div>

        {menuOpen && (
          <div className="absolute top-full left-0 right-0 bg-background border-b md:hidden">
            <nav className="flex flex-col p-4 gap-4">
              <Link href="/" onClick={() => setMenuOpen(false)}>Food Search</Link>
              <Link href="/planner" onClick={() => setMenuOpen(false)}>AI Planner</Link>
              <Link href="/clients" onClick={() => setMenuOpen(false)}>Clients</Link>
              <Button onClick={() => { setMenuOpen(false); setPricingOpen(true); }} size="sm">
                {isProOrTrial ? "Manage Plan" : "Go Pro"}
              </Button>
            </nav>
          </div>
        )}
      </header>

      <PricingModal open={pricingOpen} onOpenChange={setPricingOpen} />
    </>
  );
}
