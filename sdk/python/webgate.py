"""WebGate SDK for Python — discover and message website agents."""

import json
import urllib.request
from typing import Any, Optional


def discover(domain: str, scheme: str = "https", timeout: int = 5) -> dict[str, Any]:
    """Fetch WebGate manifest from a domain.

    Args:
        domain: e.g. "shop.com"
        scheme: "https" or "http"
        timeout: request timeout in seconds

    Returns:
        Parsed webgate.json as dict.

    Raises:
        ValueError: no webgate.json found or invalid format.
        urllib.error.URLError: network error.
    """
    url = f"{scheme}://{domain}/.well-known/webgate.json"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    resp = urllib.request.urlopen(req, timeout=timeout)
    data = json.loads(resp.read().decode())
    if "endpoint" not in data:
        raise ValueError(f"Invalid webgate.json: missing 'endpoint' field")
    return data


def send(endpoint: str, message: dict[str, Any], timeout: int = 30) -> dict[str, Any]:
    """Send a message to a WebGate agent endpoint.

    Args:
        endpoint: agent's receiving URL (from discover())
        message: message payload, must include "from" and "content"
        timeout: request timeout in seconds

    Returns:
        Agent's response as dict.

    Raises:
        ValueError: missing required fields.
        urllib.error.URLError: network error.
    """
    if "from" not in message or "content" not in message:
        raise ValueError("Message must include 'from' and 'content' fields")
    data = json.dumps(message).encode()
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    resp = urllib.request.urlopen(req, timeout=timeout)
    return json.loads(resp.read().decode())


def visit(domain: str, intent: str, from_id: str = "anonymous", scheme: str = "https", **context) -> dict[str, Any]:
    """Discover a WebGate agent and send a first message. One-liner entry point.

    Args:
        domain: website domain to visit
        intent: what the visiting agent wants to do
        from_id: visiting agent's identity
        scheme: "https" or "http"
        **context: additional fields merged into the message

    Returns:
        Agent's response as dict.
    """
    manifest = discover(domain, scheme=scheme)
    message = {"from": from_id, "content": intent, **context}
    return send(manifest["endpoint"], message)
