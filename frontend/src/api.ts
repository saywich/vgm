export interface User {
  id: string;
  username: string;
  display_name: string;
  bio: string;
}
export interface Video {
  platform: "youtube" | "tiktok" | "instagram";
  video_id: string;
  canonical_url: string;
  embed_url: string;
}
export interface Conversation {
  id: string;
  peer: User;
  updated_at: string;
  last_text: string | null;
  last_kind: string | null;
}
export interface Message {
  id: number;
  client_id: string;
  conversation_id: string;
  sender_id: string;
  kind: "text" | "video";
  text: string;
  video: Video | null;
  created_at: string;
}
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}
export async function api<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api${path}`, {
      ...options,
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-VGM-Request": "1",
        ...options.headers,
      },
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError")
      throw error;
    throw new ApiError(
      0,
      "Cannot connect. Check your connection and try again.",
    );
  }
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401 && !path.startsWith("/auth/"))
      window.dispatchEvent(new Event("session-expired"));
    throw new ApiError(
      response.status,
      data?.error?.message || `Request failed (${response.status})`,
    );
  }
  return data as T;
}
