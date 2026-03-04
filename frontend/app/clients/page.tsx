"use client";

import * as React from "react";
import Link from "next/link";
import { useLocalStorage } from "@/hooks/use-local-storage";
// ...
import { Client } from "@/types";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ClientForm } from "@/components/client-form";
import { v4 as uuidv4 } from 'uuid';


export default function ClientsPage() {
  const [clients, setClients] = useLocalStorage<Client[]>("clients", []);
  const [isDialogOpen, setIsDialogOpen] = React.useState(false);
  const [isMounted, setIsMounted] = React.useState(false);

  React.useEffect(() => {
    setIsMounted(true);
  }, []);

  const handleAddClient = (clientData: Omit<Client, "id">) => {
    const newClient = { ...clientData, id: uuidv4() };
    setClients([...clients, newClient]);
    setIsDialogOpen(false);
  };

  if (!isMounted) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        <p className="mt-4 text-lg text-muted-foreground">Loading clients...</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-12 md:p-24">
      <div className="w-full max-w-4xl">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold tracking-tight text-primary lg:text-5xl">
            Client Management
          </h1>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button>Add New Client</Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Add a New Client</DialogTitle>
              </DialogHeader>
              <ClientForm onSubmit={handleAddClient} isSubmitting={false} />
            </DialogContent>
          </Dialog>
        </div>

        <div className="glassmorphism p-4 rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {clients.length > 0 ? (
                clients.map((client) => (
                  <TableRow key={client.id}>
                    <TableCell className="font-medium">{client.name}</TableCell>
                    <TableCell>{client.email}</TableCell>
                    <TableCell>
                      <Link href={`/report/${client.id}`} passHref>
                        <Button variant="outline" size="sm">View Report</Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={3} className="h-24 text-center">
                    No clients found. Add one to get started!
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </main>
  );
}
