# WebGate

嵌入网站的 A2A 管道 —— 让 agent 发现并连接网站自部署的 agent。

## 理念

每个网站有一个固定的 agent 管道，跟着域名走。就像每个网站都有 HTTPS 证书、robots.txt、Open Graph 标签一样自然。

WebGate 不管 agent 怎么通信、谈什么、用什么框架。只管一件事：**门在哪**。

## 商家接入

总共两件事：**放一个 JSON 文件** + **让你的 agent 能收 HTTP 消息**。

### 第一步：放 webgate.json

在你网站的根路径放一个文件：

```
/.well-known/webgate.json
```

内容：

```json
{
  "version": "1.0",
  "endpoint": "https://你的agent地址/receive"
}
```

`endpoint` 填什么，取决于你的 agent 怎么接收消息。下面按情况说。

### 第二步：让 agent 能收消息

你的 agent 是什么形态，决定了 endpoint 填什么、要不要加 adapter。

---

#### 情况 A：agent 已经有 HTTP 接口

如果你的 agent 本来就能通过 HTTP 收消息（大多数情况），endpoint 直接填它的 URL。

**Hermes / OpenClaw**

Hermes gateway 已经是一个 HTTP 服务。假设跑在 `https://agent.shop.com:3000`，直接填：

```json
{
  "version": "1.0",
  "endpoint": "https://agent.shop.com:3000/api/message"
}
```

完成。外部 agent 的消息直接打到你的 Hermes gateway。

**Dify / Coze / FastGPT / 扣子**

这些平台都有 Webhook 功能。你在平台上配好 bot，拿到 webhook URL：

```json
{
  "version": "1.0",
  "endpoint": "https://api.dify.ai/v1/chat-messages?bot=你的bot-id"
}
```

完成。不需要写代码。

**自建 API 服务（FastAPI / Flask / Express / Spring）**

你已经有一个 HTTP server，加一个 POST 路由就行：

```python
# 在你现有的 FastAPI 服务里加一个路由
@app.post("/receive")
async def receive(request: Request):
    message = await request.json()
    reply = your_agent.process(message["content"])
    return {"from": "your-agent", "content": reply}
```

endpoint 填你服务的地址：`https://your-server.com/receive`

---

#### 情况 B：agent 没有 HTTP 接口

如果你的 agent 是本地跑的脚本、CLI 工具、或者只是一个 Python 函数，没有 HTTP 接口——加一个 adapter。

adapter 就是一个最小的 HTTP server，收到消息后调你的 agent，把回复返回。

**Python agent（本地函数）**

```python
from fastapi import FastAPI, Request

app = FastAPI()

# 你原有的 agent，完全不用改
from my_agent import chat  # 不管它内部怎么实现的

@app.post("/receive")
async def receive(request: Request):
    message = await request.json()
    content = message["content"]
    reply = chat(content)  # 调你自己的 agent
    return {"from": "shop-agent", "content": reply}
```

启动：`uvicorn adapter:app --port 9001`

webgate.json 填：`http://localhost:9001/receive`

**CLI agent（命令行工具）**

```python
import subprocess
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/receive")
async def receive(request: Request):
    message = await request.json()
    content = message["content"]
    
    # 调你的 CLI agent
    result = subprocess.run(
        ["my-agent", content],
        capture_output=True, text=True
    )
    return {"from": "shop-agent", "content": result.stdout}
```

**这就是全部。adapter 不关心你的 agent 是什么、怎么实现的。它只做一件事：HTTP 进，调 agent，HTTP 出。**

---

#### 接入总结

```
你的 agent 有 HTTP 接口吗？
├── 有 → endpoint 直接填那个 URL，完事
└── 没有 → 写一个 adapter（上面那段代码），endpoint 填 adapter 的地址
```

你的 agent 的知识库、prompt、工具、能力——全部不需要改。WebGate 只是在前面加了一扇门。

### 第三步（可选）：配置自己的 agent

上面的 adapter 只是转发。如果你想控制 agent 的行为，在 adapter 里加逻辑：

**接知识库**

```python
@app.post("/receive")
async def receive(request: Request):
    message = await request.json()
    
    # 先查知识库
    results = knowledge_db.search(message["content"])
    
    # 带上下文调 agent
    reply = agent.chat(f"参考信息：{results}\n\n客户问题：{message['content']}")
    return {"from": "shop-agent", "content": reply}
```

**接业务系统**

```python
@app.post("/receive")
async def receive(request: Request):
    message = await request.json()
    
    # 判断意图
    if "价格" in message["content"]:
        prices = erp.get_prices(extract_product(message))
        return {"from": "shop-agent", "content": prices}
    
    if "运费" in message["content"]:
        shipping = logistics.calculate(extract_address(message))
        return {"from": "shop-agent", "content": shipping}
    
    # 默认走 agent
    reply = agent.chat(message["content"])
    return {"from": "shop-agent", "content": reply}
```

**多 agent 路由**

```python
@app.post("/receive")
async def receive(request: Request):
    message = await request.json()
    
    # 按场景分派到不同 agent
    intent = classifier.classify(message["content"])
    
    agents = {
        "sales": sales_agent,
        "support": support_agent,
        "order": order_agent,
        "vip": vip_agent,
    }
    
    agent = agents.get(intent, default_agent)
    reply = agent.handle(message["content"])
    return {"from": "shop-agent", "content": reply}
```

这些全是**你自己的事**。WebGate 不管。WebGate 只保证外部 agent 能找到你的门。

---

## Agent 访问

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

## 与 Gaggle 的关系

WebGate 和 [Gaggle](https://github.com/Zhifeng-Niu/Gaggle) 出自同一个初衷：**让 agent 与 agent 之间能够连接业务**。

但它们解决的是不同层面的问题：

```
Gaggle = 交易所（集中）
  Agent 聚在一起，发布需求和能力，自动匹配，进入 Space 实时磋商，达成共识协议。
  是生态级基础设施——协商协议、信誉系统、审计追踪、支付结算全都有。
  场景：需要撮合的多方谈判、复杂的 B2B 协商、需要信任机制的交易。

WebGate = 门牌号（分散）
  每个网站放一个 JSON 文件，声明自己的 agent 在哪。
  不撮合、不协商、不管信任——只管"门在哪"。
  场景：商家独立站接入、服务商/渠道商/供应商对外接待 agent、任何网站的 agent 入口。
```

类比：

- Gaggle 像**证券交易所**——撮合、谈判、清算、监管，一整套。
- WebGate 像**每个店铺门口挂的营业牌**——告诉你这家店开着门，agent 在里面，进来谈。

两者互补，不冲突。一个 Gaggle 上的 agent 可以通过 WebGate 去访问某个商家的网站谈业务；一个接了 WebGate 的商家也可以用 Gaggle 来处理复杂的多方协商。

**Gaggle 是生态级的 infra，WebGate 是更广泛且适配当下互联网形态的方式。**

两个项目都开源：[Gaggle](https://github.com/Zhifeng-Niu/Gaggle) · [WebGate](https://github.com/Zhifeng-Niu/webgate)

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
