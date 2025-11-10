const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.location.origin;

type RequestOptions = RequestInit & { parseJson?: boolean };

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { parseJson = true, headers, ...rest } = options;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(headers || {})
    }
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }

  if (!parseJson) {
    return (undefined as unknown) as T;
  }

  return (await response.json()) as T;
}
