export async function fetchWithRetry(
    url: string | URL | Request,
    options: RequestInit = {},
    retries: number = 3,
    backoff: number = 1000
): Promise<Response> {
    let lastError: Error | unknown;

    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                // We can choose to retry on 5xx errors or network errors
                if (response.status >= 500 && response.status < 600) {
                    throw new Error(`Server Error: ${response.status}`);
                }
                return response; // Not a retriable error (e.g., 400 Bad Request)
            }
            return response;
        } catch (error) {
            lastError = error;
            const isLastAttempt = i === retries - 1;
            if (isLastAttempt) break;

            // Exponential backoff: backoff * 2^i
            const delay = backoff * Math.pow(2, i);
            await new Promise((resolve) => setTimeout(resolve, delay));
        }
    }

    throw lastError instanceof Error
        ? lastError
        : new Error(`Fetch failed after ${retries} retries: ${String(lastError)}`);
}
