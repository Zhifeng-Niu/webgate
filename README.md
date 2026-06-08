# WebGate

嵌入网站的 A2A 管道 —— 让 agent 发现并连接网站自部署的 agent。

## 理念

每个网站有一个固定的 agent 管道，跟着域名走。就像每个网站都有 HTTPS 证书、robots.txt、Open Graph 标签一样自然。

WebGate 不管 agent 怎么通信、谈什么、用什么框架。只管一件事：**门在哪**。

## 使用

### 商家接入（2 步）

**1. 在网站根路径放一个 JSON 文件**

```
/.well-known/webgate.json
```

```json
{
  "version": "1.0",
  "endpoint": "https://agent.shop.com/receive"
}
```

**2. 跑一个消息接收端**

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/receive")
async def receive(request: Request):
    message = await request.json()
    # 你的 agent 逻辑
    return {"from": "my-agent", "content": "hello"}
```

到此完成。任何 agent 来到你的网站都能找到你的 agent。

### Agent 访问（2 步）

**Python**

```python
from webgate import visit

response = visit("shop.com", intent="我想谈价格", from_id="my-agent")
```

**TypeScript**

```typescript
import { visit } from "webgate";

const response = await visit("shop.com", "我想谈价格", "my-agent");
```

## 流程

```
agent GET shop.com/.well-known/webgate.json
  → {"version": "1.0", "endpoint": "https://agent.shop.com/receive"}

agent POST https://agent.shop.com/receive
  → {"from": "visitor-agent", "content": "你好，想谈价格"}

merchant agent POST response
  → {"from": "shop-agent", "content": "欢迎，请告诉我商品名"}
```

## 消息格式

每次请求一个 JSON 对象，两个必须字段：

```json
{
  "from": "agent-identity",
  "content": "消息内容（文本或结构化数据）"
}
```

`content` 里放什么由两个 agent 自己约定。WebGate 只负责把消息从 A 递到 B。

## 项目结构

```
spec/           规范（JSON Schema）
sdk/python/     Python SDK
sdk/ts/         TypeScript SDK
widget/         嵌入式 JS widget（待建）
demo/merchant/  商家侧 demo
demo/agent/     agent 侧 demo
```

## 协议

MIT
