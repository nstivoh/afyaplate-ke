"use client";

import * as React from "react";
import { fetchClients } from "@/services/clientService";
import { Client } from "@/types/client";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";

interface ClientSelectorProps {
    onSelectClient: (client: Client) => void;
}

export function ClientSelector({ onSelectClient }: ClientSelectorProps) {
    const [clients, setClients] = React.useState<Client[]>([]);
    const [isLoading, setIsLoading] = React.useState(true);

    React.useEffect(() => {
        async function loadClients() {
            const data = await fetchClients();
            setClients(data);
            setIsLoading(false);
        }
        loadClients();
    }, []);

    if (isLoading) {
        return <div className="text-sm text-muted-foreground animate-pulse">Loading sample clients...</div>;
    }

    if (clients.length === 0) {
        return null;
    }

    return (
        <div className="flex flex-col space-y-2 pb-6 border-b border-border/50 mb-6">
            <Label htmlFor="client-select" className="text-lg font-semibold text-primary">Load Sample Client Profile</Label>
            <p className="text-sm text-muted-foreground mb-2">Test the form quickly by selecting a pre-configured Kenyan profile from the SQLite database.</p>
            <Select onValueChange={(value) => {
                const client = clients.find(c => c.id.toString() === value);
                if (client) onSelectClient(client);
            }}>
                <SelectTrigger id="client-select" className="w-[280px]">
                    <SelectValue placeholder="Select a sample client" />
                </SelectTrigger>
                <SelectContent>
                    {clients.map((client) => (
                        <SelectItem key={client.id} value={client.id.toString()}>
                            {client.name} - {client.health_goal || "General"}
                        </SelectItem>
                    ))}
                </SelectContent>
            </Select>
        </div>
    );
}
