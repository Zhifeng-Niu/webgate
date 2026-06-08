/**
 * WebGate SDK for TypeScript — discover and message website agents.
 */

export interface WebGateManifest {
  version: string;
  endpoint: string;
  [key: string]: unknown;
}

export interface WebGateMessage {
  from: string;
  content: string | object;
  [key: string]: unknown;
}

/**
 * Fetch WebGate manifest from a domain.
 */
export async function discover(domain: string, scheme = "https"): Promise<WebGateManifest> {
  const url = `${scheme}://${domain}/.well-known/webgate.json`;
  const resp = await fetch(url, {
    headers: { Accept: "application/json" },
  });
  if (!resp.ok) {
    throw new Error(`WebGate manifest not found at ${url} (HTTP ${resp.status})`);
  }
  const data: WebGateManifest = await resp.json();
  if (!data.endpoint) {
    throw new Error(`Invalid webgate.json: missing 'endpoint' field`);
  }
  return data;
}

/**
 * Send a message to a WebGate agent endpoint.
 */
export async function send(
  endpoint: string,
  message: WebGateMessage,
  options?: RequestInit,
): Promise<unknown> {
  if (!message.from || !message.content) {
    throw new Error("Message must include 'from' and 'content' fields");
  }
  const resp = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(message),
    ...options,
  });
  return resp.json();
}

/**
 * Discover a WebGate agent and send a first message. One-liner entry point.
 */
export async function visit(
  domain: string,
  intent: string,
  fromId = "anonymous",
  context?: Record<string, unknown>,
): Promise<unknown> {
  const manifest = await discover(domain);
  const message: WebGateMessage = {
    from: fromId,
    content: intent,
    ...context,
  };
  return send(manifest.endpoint, message);
}
