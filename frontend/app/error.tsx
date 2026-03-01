'use client'; // Error components must be Client Components

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { AlertTriangle } from 'lucide-react';

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        // Log the error to an error reporting service
        console.error('Unhandled app error:', error);
    }, [error]);

    return (
        <div className="flex flex-col items-center justify-center min-h-[70vh] px-4 text-center">
            <div className="glassmorphism p-10 rounded-2xl max-w-lg w-full flex flex-col items-center">
                <AlertTriangle className="h-16 w-16 text-yellow-500 mb-6" />
                <h2 className="text-2xl font-bold mb-4">Something went wrong</h2>
                <p className="text-muted-foreground mb-8">
                    The application encountered an unexpected error. Please check your network connection and try again.
                </p>
                <div className="flex gap-4">
                    <Button
                        onClick={() => reset()}
                        variant="default"
                    >
                        Try again
                    </Button>
                    <Button
                        onClick={() => window.location.href = '/'}
                        variant="outline"
                    >
                        Go to Homepage
                    </Button>
                </div>
                {process.env.NODE_ENV === 'development' && (
                    <div className="mt-8 text-left bg-muted p-4 rounded-md overflow-x-auto w-full text-xs font-mono text-red-500">
                        {error.message}
                    </div>
                )}
            </div>
        </div>
    );
}
