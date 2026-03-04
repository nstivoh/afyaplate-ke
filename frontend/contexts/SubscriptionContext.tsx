"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";

// ── Types ─────────────────────────────────────────────────────────────────────
export type Plan = "free" | "trial" | "pro";

export interface SubscriptionState {
    plan: Plan;
    isActive: boolean;       // Pro or active trial
    trialDaysLeft: number;
    expiresAt: string | null;
    token: string | null;
    isLoading: boolean;
    startTrial: () => Promise<void>;
    refresh: () => Promise<void>;
}

// ── Helpers ───────────────────────────────────────────────────────────────────
const TOKEN_KEY = "afyaplate_token";
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

function getOrCreateToken(): string {
    if (typeof window === "undefined") return "";
    let token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
        token = crypto.randomUUID();
        localStorage.setItem(TOKEN_KEY, token);
    }
    return token;
}

// ── Context ───────────────────────────────────────────────────────────────────
const defaultState: SubscriptionState = {
    plan: "free",
    isActive: false,
    trialDaysLeft: 0,
    expiresAt: null,
    token: null,
    isLoading: true,
    startTrial: async () => { },
    refresh: async () => { },
};

const SubscriptionContext = createContext<SubscriptionState>(defaultState);

export function SubscriptionProvider({ children }: { children: React.ReactNode }) {
    const [plan, setPlan] = useState<Plan>("free");
    const [isActive, setIsActive] = useState(false);
    const [trialDaysLeft, setTrialDaysLeft] = useState(0);
    const [expiresAt, setExpiresAt] = useState<string | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    const loadStatus = useCallback(async (tok: string) => {
        try {
            const res = await fetch(`${API_BASE}/subscription/status`, {
                headers: { "x-user-token": tok },
            });
            if (res.ok) {
                const data = await res.json();
                setPlan(data.plan);
                setIsActive(data.is_active);
                setTrialDaysLeft(data.trial_days_left);
                setExpiresAt(data.expires_at);
            }
        } catch {
            // silently fall back to free
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Initialise on mount
    useEffect(() => {
        const tok = getOrCreateToken();
        setToken(tok);
        loadStatus(tok);
    }, [loadStatus]);

    const startTrial = useCallback(async () => {
        const tok = token || getOrCreateToken();
        const res = await fetch(`${API_BASE}/subscription/start-trial`, {
            method: "POST",
            headers: { "x-user-token": tok },
        });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data?.detail || "Failed to start trial.");
        }
        const data = await res.json();
        setPlan(data.plan);
        setIsActive(data.is_active);
        setTrialDaysLeft(data.trial_days_left);
        setExpiresAt(data.expires_at);
    }, [token]);

    const refresh = useCallback(async () => {
        if (token) await loadStatus(token);
    }, [token, loadStatus]);

    return (
        <SubscriptionContext.Provider
            value={{ plan, isActive, trialDaysLeft, expiresAt, token, isLoading, startTrial, refresh }}
        >
            {children}
        </SubscriptionContext.Provider>
    );
}

export function useSubscription() {
    return useContext(SubscriptionContext);
}
