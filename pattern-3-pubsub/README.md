# 🎬 Pattern 3: Publish/Subscribe with AI Agents

## 📺 YouTube Presentation Style

What's going on, architects! 🎉 Ready for the MOST scalable integration pattern? Today we're building **Pub/Sub with intelligent AI subscribers**!

## 🎯 What's Pub/Sub All About?

Imagine a **radio station** 📻:
- **Publishers** broadcast messages (like radio shows)
- **Subscribers** tune in to topics they care about
- **No direct connection** between publishers and subscribers
- **Everyone gets the message** who's listening!

Now add AI agents as subscribers = **MIND BLOWN** 🤯

## 🏗️ Architecture Overview

```
                        ┌──────────────────┐
                        │   Azure Event    │
    Publishers ────────>│      Hub         │
                        │   (Message Bus)  │
                        └────────┬─────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
            ┌──────────┐  ┌──────────┐  ┌──────────┐
            │ Customer │  │  Order   │  │Analytics │
            │  Agent   │  │  Agent   │  │  Agent   │
            │          │  │          │  │          │
            │ Topics:  │  │ Topics:  │  │ Topics:  │
            │ Customer │  │ Orders   │  │   All    │
            └──────────┘  └──────────┘  └──────────┘
```

## 🔥 The Enterprise Integration Pattern

**Publish/Subscribe** decouples systems:

1. **Publishers** - Send events without knowing who receives
2. **Topics** - Logical channels for different event types
3. **Subscribers** - Register interest in specific topics
4. **Event Hub** - Routes messages to interested subscribers
5. **Parallel Processing** - Multiple agents process simultaneously

### Why This Pattern Rocks! 🎸

- ✅ **Loose Coupling** - Publishers don't know about subscribers
- ✅ **Scalability** - Add subscribers without changing publishers
- ✅ **Flexibility** - Subscribe to multiple topics
- ✅ **Resilience** - Subscribers can fail independently
- ✅ **Broadcast** - One message reaches many subscribers

## 🛠️ Technologies Used

- **Azure Event Hub** - Pub/Sub message broker 📬
- **Azure AI Foundry Agents** - Intelligent subscribers 🤖
- **Topic-Based Routing** - Smart message delivery 🎯
- **FastAPI + MCP** - REST API with standardized protocol ⚡
- **Async Python** - Concurrent message processing 🚀

## 🚀 Quick Start

### Prerequisites

1. Azure Event Hub configured
2. Azure AI Foundry project
3. Python 3.11+

### Setup

1. **Navigate:**
```bash
cd pattern-3-pubsub
```

2. **Configure:**
```bash
cp ../.env.example .env
# Add your credentials
```

3. **Install:**
```bash
pip install -r ../requirements.txt
```

### 🏃 Running

**Option 1: Demo with Preset Subscribers**
```bash
python main.py
```

**Option 2: REST API**
```bash
python api.py
# OR
uvicorn api:app --port 8002 --reload
```

### 🐳 Docker

**Build:**
```bash
# Production
docker build -t pubsub-agent --target production .

# Development
docker build -t pubsub-agent-dev --target development .
```

**Run:**
```bash
# Production
docker run --env-file .env pubsub-agent

# Development
docker run -p 8002:8002 -v $(pwd):/app/pattern-3-pubsub --env-file .env pubsub-agent-dev
```

## 📡 API Endpoints

### Publish a Message
```bash
POST /publish
{
  "topic": "customer_events",
  "payload": {
    "event_type": "feedback",
    "customer_id": "C123",
    "rating": 5,
    "comment": "Excellent service!"
  }
}
```

### Create Custom Subscriber
```bash
POST /subscribers/create
{
  "name": "Fraud Detection Agent",
  "topics": ["order_events"],
  "instructions": "Analyze orders for fraud patterns..."
}
```

### Create Preset Subscribers
```bash
POST /subscribers/preset/customer-service
POST /subscribers/preset/order-processor
POST /subscribers/preset/analytics
```

### List Subscribers
```bash
GET /subscribers
```

### Start Message Consumers
```bash
POST /consumers/start
```

### List Available Topics
```bash
GET /topics
```

## 💡 How It Works

### 1. Topic Definition
Four topic types available:
- `customer_events` - Customer interactions
- `order_events` - Order processing
- `system_events` - System operations
- `analytics_events` - Business analytics

### 2. Subscriber Registration
Agents subscribe to topics they care about:
```python
subscriber = AgentSubscriber(
    name="Customer Service",
    subscribed_topics=[TopicType.CUSTOMER_EVENTS],
    processing_instructions="Handle customer issues..."
)
```

### 3. Message Publishing
Publishers send to topics:
```python
message = Message(
    topic=TopicType.CUSTOMER_EVENTS,
    payload={"customer_id": "C123", ...}
)
await broker.publish(message)
```

### 4. Intelligent Processing
- Event Hub broadcasts to all subscribers
- Each agent checks if it's subscribed to the topic
- Interested agents process in parallel
- Each provides unique insights from their perspective

## 🎓 Key Concepts

### AgentSubscriber
AI-powered subscriber:
- **Subscribes** to specific topics
- **Filters** messages by interest
- **Processes** using AI cognition
- **Tracks** metrics

### PubSubBroker
Message orchestrator:
- **Manages** subscriber registry
- **Routes** messages to Event Hub
- **Coordinates** parallel processing
- **Handles** failures gracefully

### Topic-Based Routing
Messages flow based on topics:
```
customer_events → Customer Service Agent
customer_events → Analytics Agent
order_events    → Order Processing Agent
order_events    → Analytics Agent
```

## 📊 Real-World Use Cases

Perfect for:

1. 🎫 **Event-Driven Architecture**
   - Microservices communicate via events
   - Each service is a subscriber

2. 📊 **Real-Time Analytics**
   - Analytics agents subscribe to all topics
   - Process events for insights

3. 🔔 **Notification Systems**
   - Different agents for email, SMS, push
   - Subscribe to relevant events

4. 🛡️ **Security Monitoring**
   - Security agents subscribe to all topics
   - Detect threats in real-time

5. 🔄 **Data Synchronization**
   - Multiple databases as subscribers
   - Stay in sync automatically

## 🎯 Advanced Features

### Multi-Topic Subscription
One agent, multiple topics:
```python
analytics_agent.subscribed_topics = [
    TopicType.CUSTOMER_EVENTS,
    TopicType.ORDER_EVENTS,
    TopicType.SYSTEM_EVENTS,
]
```

### Parallel Processing
Multiple agents process same message:
- Customer Service analyzes customer sentiment
- Analytics extracts metrics
- Fraud Detection checks for anomalies

All simultaneously! ⚡

### Dynamic Subscriber Management
- Add subscribers at runtime
- Remove subscribers without affecting others
- Update subscriptions dynamically

## 🔐 Best Practices

1. ✅ **Topic Design** - Clear, logical topic hierarchy
2. ✅ **Idempotency** - Subscribers handle duplicates
3. ✅ **Error Handling** - One subscriber failure doesn't affect others
4. ✅ **Message Schema** - Consistent message format
5. ✅ **Monitoring** - Track subscriber health and performance

## 📈 Monitoring & Metrics

Track important metrics:
- Messages published per topic
- Subscriber processing time
- Success/failure rates
- Message throughput

```python
subscriber_info = {
    "name": subscriber.name,
    "processed_count": subscriber.processed_count,
    "subscribed_topics": subscriber.subscribed_topics,
}
```

## 🆚 Pub/Sub vs Other Patterns

| Pattern | Coupling | Scalability | Use Case |
|---------|----------|-------------|----------|
| **Pub/Sub** | Loose | High | Event broadcasting |
| **Queue** | Tight | Medium | Task distribution |
| **Pipes** | Medium | Medium | Sequential processing |

## 🎬 What's Coming!

Next up:
- **Pattern 4**: Command Messages with async pipelines
- Complete architecture documentation
- Docker Compose for all patterns

## 🙏 Before You Go!

- 👍 Like if you learned something new
- 💬 Comment your Pub/Sub use cases
- 📢 Share with your team
- 🔔 Subscribe for Pattern 4!

---

**🔗 Resources:**
- [Pub/Sub Pattern](https://www.enterpriseintegrationpatterns.com/patterns/messaging/PublishSubscribeChannel.html)
- [Azure Event Hubs](https://learn.microsoft.com/azure/event-hubs/)
- [Azure AI Foundry](https://learn.microsoft.com/azure/ai-studio/)

**#PubSub #EventDriven #AzureEventHub #AIAgents #Microservices #CloudArchitecture**
