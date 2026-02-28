"use client";

import Link from "next/link";
import { Button } from "./ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogTrigger,
} from "./ui/dialog";
import { Input } from "./ui/input";

export function Header() {
  return (
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
      <div>
        <Dialog>
          <DialogTrigger asChild>
            <Button>Go Pro</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Get AfyaPlate Pro</DialogTitle>
              <DialogDescription>
                Unlock advanced features, unlimited meal plans, and detailed analytics.
                Pay with M-Pesa to get instant access.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                 <Input id="phone" defaultValue="+254712345678" className="col-span-4" />
              </div>
            </div>
            <DialogFooter>
              <Button type="submit" className="w-full">Pay KES 500 with M-Pesa</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </header>
  );
}
