import { fetchWithRetry } from '../lib/fetchWithRetry';
import { Client } from '@/types/client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function fetchClients(): Promise<Client[]> {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/clients/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    } catch (error) {
        console.error("Failed to fetch clients:", error);
        return [];
    }
}
