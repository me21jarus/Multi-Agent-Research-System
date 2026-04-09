/**
 * SSE streaming client for the research API.
 *
 * Why fetch() instead of EventSource?
 *   EventSource only supports GET requests.
 *   Our endpoint is POST (we send the query in the body).
 *   So we use fetch() with a ReadableStream reader instead.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type ProgressEvent = {
  type: "progress";
  node: string;
  message: string;
};

export type ResultEvent = {
  type: "result";
  data: {
    query: string;
    final_report: string;
    sources: { title: string; url: string }[];
    thread_id: string;
  };
};

export type ErrorEvent = {
  type: "error";
  message: string;
};

export type ResearchEvent = ProgressEvent | ResultEvent | ErrorEvent;

/**
 * Stream research results from the backend.
 *
 * @param query       - The research question
 * @param onEvent     - Callback fired for each SSE event
 * @param onComplete  - Callback fired when the stream ends
 */
export async function streamResearch(
  query: string,
  onEvent: (event: ResearchEvent) => void,
  onComplete: () => void
) {
  const response = await fetch(`${API_BASE}/api/research`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // SSE lines look like: "data: {...}\n\n"
    // Split on double newline to get individual events
    const parts = buffer.split("\n\n");
    buffer = parts.pop() || ""; // keep incomplete last chunk

    for (const part of parts) {
      const line = part.trim();
      if (!line.startsWith("data:")) continue;

      try {
        const json = line.replace(/^data:\s*/, "");
        const event: ResearchEvent = JSON.parse(json);
        onEvent(event);
      } catch {
        // ignore malformed events
      }
    }
  }

  onComplete();
}
