import type { Answer } from "./contract";

export const API = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

// T-clean-1: httpOnly cookie transport. The token is never readable or writable
// from JS — every request carries credentials and the browser attaches the cookie.
export function authHeaders(): HeadersInit {
  return { "Content-Type": "application/json" };
}
export async function api(path: string, init: RequestInit = {}) {
  let r: Response;
  try {
    r = await fetch(`${API}${path}`, {
      credentials: "include",
      ...init,
      headers: { ...authHeaders(), ...(init.headers || {}) },
    });
  } catch {
    throw new ApiError(0, "Network error — is the backend running?");
  }
  if (r.status === 401 && typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
    window.location.href = "/login";
  }
  if (!r.ok) {
    let msg = await r.text();
    try {
      const j = JSON.parse(msg);
      msg = (j as { detail?: string }).detail || msg;
    } catch {
      // Non-JSON error body (proxy/plaintext) — keep raw text, still throw below.
    }
    throw new ApiError(r.status, msg || `Request failed (${r.status})`);
  }
  return r.json();
}
/** Download an authorized file as blob (cookie-attached, never ?token= URLs). */
export async function downloadFile(docId: string, filename: string) {
  const r = await fetch(`${API}/api/v1/knowledge/file/${docId}`, { credentials: "include" });
  if (!r.ok) throw new ApiError(r.status, r.status === 404 ? "File not found or not authorized." : "Download failed.");
  const blob = await r.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 5000);
}
/** T5.2 SSE with JSON fallback. onEvent receives {type, data}. */
export async function askStream(
  body: { session_id: string | null; message: string; attachment_id?: string },
  onEvent: (type: string, data: Record<string, unknown>) => void,
  signal?: AbortSignal,
): Promise<Answer | null> {
  const headers = { ...authHeaders(), Accept: "text/event-stream" };
  let r: Response;
  try {
    r = await fetch(`${API}/api/v1/chat/ask-stream`, { method: "POST", credentials: "include", headers, body: JSON.stringify(body), signal });
  } catch (e) {
    if ((e as Error).name === "AbortError") return null;
    throw new ApiError(0, "Network error — is the backend running?");
  }
  if (!r.ok || !r.body) {
    // Fallback to sync JSON endpoint (T5.2 transport choice per deployment)
    return (await api("/api/v1/chat/ask", { method: "POST", body: JSON.stringify(body), signal })) as Answer;
  }
  const reader = r.body.getReader();
  const dec = new TextDecoder();
  let buf = "", final: Answer | null = null, etype = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let idx: number;
    while ((idx = buf.indexOf("\n\n")) >= 0) {
      const frame = buf.slice(0, idx); buf = buf.slice(idx + 2);
      for (const line of frame.split("\n")) {
        if (line.startsWith("event:")) etype = line.slice(6).trim();
        else if (line.startsWith("data:")) {
          let data: Record<string, unknown> = {};
          try {
            data = JSON.parse(line.slice(5).trim());
          } catch {
            // Truncated SSE frame mid-stream; keep {} and wait for the next frame.
          }
          onEvent(etype || "message", data);
          if (etype === "final") final = data as unknown as Answer;
          if (etype === "error") throw new ApiError(502, String(data.error || "Answer failed — please retry."));
        }
      }
      etype = "";
    }
  }
  return final;
}
