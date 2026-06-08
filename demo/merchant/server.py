"""Demo merchant server — a minimal WebGate agent receiver.

Run: uvicorn server:app --port 9001
Then place this at your site root:
  .well-known/webgate.json -> {"version":"1.0","endpoint":"http://localhost:9001/receive"}
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="WebGate Demo Merchant Agent")

# Serve well-known manifest
@app.get("/.well-known/webgate.json")
async def manifest():
    return {"version": "1.0", "endpoint": "http://localhost:9001/receive"}

# Simple in-memory agent that handles basic negotiation
@app.post("/receive")
async def receive(request: Request):
    message = await request.json()

    visitor = message.get("from", "unknown")
    content = message.get("content", "")

    # Agent logic — replace with real agent implementation
    if isinstance(content, str):
        if "价格" in content or "price" in content.lower():
            return {
                "from": "shop-agent",
                "content": {
                    "type": "quote",
                    "message": "欢迎！请告诉我您感兴趣的商品，我可以给您报价。",
                },
            }
        elif "运费" in content or "shipping" in content.lower():
            return {
                "from": "shop-agent",
                "content": {
                    "type": "info",
                    "message": "我们支持全球配送，标准运费 ¥30，满 ¥200 包邮。",
                },
            }
        else:
            return {
                "from": "shop-agent",
                "content": {
                    "type": "ack",
                    "message": f"收到来自 {visitor} 的消息。请问有什么可以帮您？",
                },
            }
    else:
        return {
            "from": "shop-agent",
            "content": {
                "type": "ack",
                "message": f"收到结构化消息。请问有什么可以帮您？",
            },
        }

# Health check
@app.get("/health")
async def health():
    return {"status": "ok"}
