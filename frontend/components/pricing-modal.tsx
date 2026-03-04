"use client";

import React, { useState } from "react";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useSubscription } from "@/contexts/SubscriptionContext";
import {
    Smartphone,
    CreditCard,
    Bitcoin,
    Check,
    Loader2,
    Sparkles,
    Zap,
    Users,
    FileText,
    Clock,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

type PaymentTab = "mpesa" | "card" | "crypto";
type Status = "idle" | "loading" | "success" | "error";

interface PricingModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

const PRO_FEATURES = [
    { icon: Zap, label: "AI Meal Planner (all LLM providers)" },
    { icon: Users, label: "Unlimited client profiles" },
    { icon: FileText, label: "PDF export with your branding" },
    { icon: Clock, label: "12-month meal plan history" },
    { icon: Sparkles, label: "Priority support" },
];

export function PricingModal({ open, onOpenChange }: PricingModalProps) {
    const { token, plan, isActive, trialDaysLeft, startTrial, refresh } = useSubscription();
    const [tab, setTab] = useState<PaymentTab>("mpesa");
    const [phone, setPhone] = useState("+254");
    const [email, setEmail] = useState("");
    const [status, setStatus] = useState<Status>("idle");
    const [errorMsg, setErrorMsg] = useState("");

    const trialAvailable = plan === "free";
    const trialExpired = plan === "trial" && !isActive;

    // ── Trial ─────────────────────────────────────────────────────────────────
    const handleTrial = async () => {
        setStatus("loading");
        setErrorMsg("");
        try {
            await startTrial();
            setStatus("success");
        } catch (e: any) {
            setErrorMsg(e.message);
            setStatus("error");
        }
    };

    // ── Upgrade helper (after payment confirmed) ──────────────────────────────
    const upgradeSubscription = async (method: string, ref: string) => {
        if (!token) return;
        const res = await fetch(`${API_BASE}/subscription/upgrade`, {
            method: "POST",
            headers: { "Content-Type": "application/json", "x-user-token": token },
            body: JSON.stringify({ payment_method: method, payment_ref: ref }),
        });
        if (!res.ok) throw new Error("Failed to activate Pro.");
        await refresh();
    };

    // ── M-Pesa ────────────────────────────────────────────────────────────────
    const handleMpesa = async () => {
        setStatus("loading");
        setErrorMsg("");
        try {
            const res = await fetch(`${API_BASE}/payments/stk-push`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ phone_number: phone, amount: 500 }),
            });
            if (!res.ok) {
                const d = await res.json().catch(() => ({}));
                throw new Error(d?.detail || "M-Pesa request failed.");
            }
            const data = await res.json();
            // Optimistically upgrade — in production wait for callback
            await upgradeSubscription("mpesa", data.CheckoutRequestID || "mpesa-ref");
            setStatus("success");
        } catch (e: any) {
            setErrorMsg(e.message);
            setStatus("error");
        }
    };

    // ── Card (Flutterwave) ────────────────────────────────────────────────────
    const handleCard = async () => {
        if (!email) { setErrorMsg("Please enter your email."); return; }
        setStatus("loading");
        setErrorMsg("");
        try {
            const res = await fetch(`${API_BASE}/payments/card-checkout`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    amount: 500,
                    currency: "KES",
                    email,
                    user_token: token,
                    redirect_url: `${window.location.origin}/?payment=success`,
                }),
            });
            if (!res.ok) {
                const d = await res.json().catch(() => ({}));
                throw new Error(d?.detail || "Card payment setup failed.");
            }
            const data = await res.json();
            // Redirect to Flutterwave hosted page
            window.location.href = data.payment_url;
        } catch (e: any) {
            setErrorMsg(e.message);
            setStatus("error");
        }
    };

    // ── Crypto ────────────────────────────────────────────────────────────────
    const handleCrypto = async () => {
        setStatus("loading");
        setErrorMsg("");
        try {
            const res = await fetch(`${API_BASE}/payments/crypto-checkout`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    amount_usd: 5,
                    user_token: token,
                    redirect_url: `${window.location.origin}/?payment=success`,
                    cancel_url: window.location.href,
                }),
            });
            if (!res.ok) {
                const d = await res.json().catch(() => ({}));
                throw new Error(d?.detail || "Crypto payment setup failed.");
            }
            const data = await res.json();
            window.location.href = data.payment_url;
        } catch (e: any) {
            setErrorMsg(e.message);
            setStatus("error");
        }
    };

    const tabs: { id: PaymentTab; label: string; icon: React.ElementType }[] = [
        { id: "mpesa", label: "M-Pesa", icon: Smartphone },
        { id: "card", label: "Card", icon: CreditCard },
        { id: "crypto", label: "Crypto", icon: Bitcoin },
    ];

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[520px] p-0 overflow-hidden">
                {/* Header */}
                <div className="bg-gradient-to-br from-primary/20 to-primary/5 p-6 pb-4">
                    <DialogHeader>
                        <div className="flex items-center gap-2 mb-1">
                            <Sparkles className="h-5 w-5 text-primary" />
                            <Badge variant="secondary" className="text-xs">AfyaPlate Pro</Badge>
                        </div>
                        <DialogTitle className="text-2xl font-bold">
                            {isActive
                                ? `Pro Active — ${trialDaysLeft > 0 ? `${trialDaysLeft} trial days left` : "🎉"}`
                                : trialExpired
                                    ? "Trial Ended — Upgrade to Continue"
                                    : "Upgrade to AfyaPlate Pro"}
                        </DialogTitle>
                        <DialogDescription className="text-sm mt-1">
                            KES 500 / month &nbsp;·&nbsp; Cancel anytime
                        </DialogDescription>
                    </DialogHeader>

                    {/* Feature list */}
                    <ul className="mt-4 space-y-1.5">
                        {PRO_FEATURES.map(({ icon: Icon, label }) => (
                            <li key={label} className="flex items-center gap-2 text-sm">
                                <Check className="h-4 w-4 text-primary shrink-0" />
                                {label}
                            </li>
                        ))}
                    </ul>
                </div>

                <div className="p-6 pt-4 space-y-4">
                    {/* Success state */}
                    {status === "success" ? (
                        <div className="text-center py-6 space-y-2">
                            <div className="text-4xl">🎉</div>
                            <p className="font-bold text-lg text-primary">
                                {trialAvailable ? "Trial Started!" : "Welcome to Pro!"}
                            </p>
                            <p className="text-sm text-muted-foreground">
                                {trialAvailable
                                    ? "You have 14 days of full Pro access — enjoy!"
                                    : "Check your phone for the M-Pesa prompt."}
                            </p>
                            <Button className="mt-4 w-full" onClick={() => onOpenChange(false)}>
                                Get Started
                            </Button>
                        </div>
                    ) : (
                        <>
                            {/* Free trial CTA (only for free users) */}
                            {trialAvailable && (
                                <div className="rounded-lg border border-primary/30 bg-primary/5 p-4">
                                    <p className="text-sm font-semibold mb-1">Try Free for 14 Days</p>
                                    <p className="text-xs text-muted-foreground mb-3">
                                        No payment required. Full Pro access, cancel anytime.
                                    </p>
                                    <Button
                                        className="w-full"
                                        variant="default"
                                        disabled={status === "loading"}
                                        onClick={handleTrial}
                                    >
                                        {status === "loading" ? (
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        ) : null}
                                        Start Free Trial
                                    </Button>
                                    {status === "error" && <p className="text-xs text-red-500 mt-2">{errorMsg}</p>}

                                    <div className="flex items-center gap-2 my-3">
                                        <div className="h-px flex-1 bg-border" />
                                        <span className="text-xs text-muted-foreground">or pay now</span>
                                        <div className="h-px flex-1 bg-border" />
                                    </div>
                                </div>
                            )}

                            {/* Payment tabs */}
                            <div>
                                <div className="flex rounded-lg border overflow-hidden mb-4">
                                    {tabs.map(({ id, label, icon: Icon }) => (
                                        <button
                                            key={id}
                                            className={`flex-1 flex items-center justify-center gap-1.5 py-2 text-sm font-medium transition-colors ${tab === id
                                                    ? "bg-primary text-primary-foreground"
                                                    : "hover:bg-muted text-muted-foreground"
                                                }`}
                                            onClick={() => { setTab(id); setStatus("idle"); setErrorMsg(""); }}
                                        >
                                            <Icon className="h-4 w-4" />
                                            {label}
                                        </button>
                                    ))}
                                </div>

                                {/* M-Pesa */}
                                {tab === "mpesa" && (
                                    <div className="space-y-3">
                                        <p className="text-xs text-muted-foreground">
                                            Enter your Safaricom number. You'll get an STK push prompt instantly.
                                        </p>
                                        <Input
                                            value={phone}
                                            onChange={(e) => setPhone(e.target.value)}
                                            placeholder="+254712345678"
                                        />
                                        <Button className="w-full" onClick={handleMpesa} disabled={status === "loading"}>
                                            {status === "loading" ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                                            Pay KES 500 with M-Pesa
                                        </Button>
                                    </div>
                                )}

                                {/* Card */}
                                {tab === "card" && (
                                    <div className="space-y-3">
                                        <p className="text-xs text-muted-foreground">
                                            Pay with Visa, Mastercard or mobile money via Flutterwave. Secure hosted checkout.
                                        </p>
                                        <Input
                                            type="email"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            placeholder="your@email.com"
                                        />
                                        <Button className="w-full" onClick={handleCard} disabled={status === "loading"}>
                                            {status === "loading" ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                                            Pay KES 500 by Card
                                        </Button>
                                    </div>
                                )}

                                {/* Crypto */}
                                {tab === "crypto" && (
                                    <div className="space-y-3">
                                        <p className="text-xs text-muted-foreground">
                                            Pay ~$5 USD in BTC, ETH, USDC, or other cryptocurrencies via Coinbase Commerce.
                                        </p>
                                        <Button className="w-full" onClick={handleCrypto} disabled={status === "loading"}>
                                            {status === "loading" ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                                            Pay with Crypto (~$5 USD)
                                        </Button>
                                    </div>
                                )}

                                {status === "error" && (
                                    <p className="text-xs text-red-500 mt-2">{errorMsg}</p>
                                )}
                            </div>

                            <p className="text-center text-[10px] text-muted-foreground pt-1">
                                Secure payment · No recurring auto-charge · Renew manually each month
                            </p>
                        </>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
