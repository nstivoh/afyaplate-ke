"use client";

import React from "react";
import { Lock } from "lucide-react";
import { useSubscription } from "@/contexts/SubscriptionContext";
import { Button } from "@/components/ui/button";

interface UpgradeGateProps {
    children: React.ReactNode;
    feature: string;          // e.g. "AI Meal Planner"
    onUpgradeClick?: () => void;
}

/**
 * Wraps a Pro-only feature. Free users see a blurred preview with a lock CTA.
 * Active Pro/Trial users see the feature normally.
 */
export function UpgradeGate({ children, feature, onUpgradeClick }: UpgradeGateProps) {
    const { isActive, isLoading, plan } = useSubscription();

    // Don't flash lock while loading
    if (isLoading) return <>{children}</>;

    if (isActive) return <>{children}</>;

    return (
        <div className="relative">
            {/* Blurred preview */}
            <div className="pointer-events-none select-none" style={{ filter: "blur(4px)", opacity: 0.5 }}>
                {children}
            </div>

            {/* Lock overlay */}
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-background/60 backdrop-blur-sm rounded-lg">
                <div className="flex flex-col items-center gap-2 text-center px-6">
                    <div className="p-3 rounded-full bg-primary/10">
                        <Lock className="h-6 w-6 text-primary" />
                    </div>
                    <p className="font-semibold text-sm">{feature} — Pro Feature</p>
                    <p className="text-xs text-muted-foreground max-w-[240px]">
                        {plan === "trial"
                            ? "Your trial has ended. Upgrade to keep access."
                            : "Start your free 14-day trial or upgrade to Pro."}
                    </p>
                </div>
                {onUpgradeClick && (
                    <Button size="sm" onClick={onUpgradeClick}>
                        {plan === "free" ? "Start Free Trial" : "Upgrade to Pro"}
                    </Button>
                )}
            </div>
        </div>
    );
}
