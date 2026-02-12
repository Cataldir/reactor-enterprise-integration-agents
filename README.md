# 🚀 Reactor Enterprise Integration Agents

A comprehensive repository demonstrating **Enterprise Integration Patterns** using **Azure AI Foundry Agents (v2 SDK)** and **Azure Event Hubs**.

## 📺 YouTube Series: "Deep Dive em Integrações Empresariais para Aplicações de AI"

This repository contains complete, production-ready examples of four core enterprise integration patterns, each enhanced with **cognitive capabilities** from AI agents.

## 🎯 What's Inside?

Four distinct integration patterns, each in its own folder with:
- ✅ Complete source code with Azure AI Foundry integration
- ✅ Dockerfile (base + development images)
- ✅ MCP (Model Context Protocol) integration layer
- ✅ FastAPI REST API endpoints
- ✅ Comprehensive README with YouTube presentation style
- ✅ Real-world use cases and examples

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Azure AI Foundry                          │
│              (AI Agents - v2 SDK)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Integration Layer                          │
│         (Model Context Protocol + FastAPI)                  │
└────────┬────────────────────────────────────────────────────┘
         │
         ├────────────┬────────────┬────────────┬─────────────┐
         │            │            │            │             │
         ▼            ▼            ▼            ▼             ▼
┌──────────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
│   Pattern 1  │ │Pattern 2│ │Pattern 3│ │Pattern 4 │ │  Shared  │
│   Message    │ │ Pipes & │ │ Pub/Sub │ │ Command  │ │ Utils    │
│   Queue      │ │ Filters │ │         │ │ Messages │ │          │
└──────────────┘ └─────────┘ └─────────┘ └──────────┘ └──────────┘
         │            │            │            │
         └────────────┴────────────┴────────────┘
                       │
                       ▼
         ┌─────────────────────────┐
         │   Azure Event Hubs      │
         │   (Message Broker)      │
         └─────────────────────────┘
```

## 📁 Repository Structure

```
reactor-enterprise-integration-agents/
├── shared/                          # Shared utilities
│   ├── mcp/                        # MCP integration layer
│   │   ├── __init__.py            # Base MCP classes
│   │   └── fastapi_mcp.py         # FastAPI MCP server
│   └── utils/                      # Common utilities
│       ├── agent_utils.py         # Agent management
│       └── eventhub_utils.py      # Event Hub integration
├── pattern-1-message-queue/        # Pattern 1: Message Queue
│   ├── main.py                    # Core implementation
│   ├── api.py                     # REST API server
│   ├── Dockerfile                 # Container configuration
│   └── README.md                  # Pattern documentation
├── pattern-2-pipes-filters/        # Pattern 2: Pipes and Filters
│   ├── main.py                    # Core implementation
│   ├── api.py                     # REST API server
│   ├── Dockerfile                 # Container configuration
│   └── README.md                  # Pattern documentation
├── pattern-3-pubsub/              # Pattern 3: Pub/Sub
│   ├── main.py                    # Core implementation
│   ├── api.py                     # REST API server
│   ├── Dockerfile                 # Container configuration
│   └── README.md                  # Pattern documentation
├── pattern-4-command-messages/     # Pattern 4: Command Messages
│   ├── main.py                    # Core implementation
│   ├── api.py                     # REST API server
│   ├── Dockerfile                 # Container configuration
│   └── README.md                  # Pattern documentation
├── ARCHITECTURE.md                # Detailed architecture guide
├── pyproject.toml                 # Python project configuration
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Development dependencies
├── .env.example                   # Environment variables template
└── README.md                      # This file
```

## 🎓 The Four Patterns

### 1️⃣ Message Queue Monitor and Executor
**Port: 8000** | [📖 Documentation](pattern-1-message-queue/README.md)

AI agents monitor message queues and intelligently process tasks. Perfect for:
- Task distribution and processing
- Work queue management
- Background job processing

### 2️⃣ Pipes and Filters with Cognitive Capabilities
**Port: 8001** | [📖 Documentation](pattern-2-pipes-filters/README.md)

Sequential or parallel processing pipeline where each filter is an AI agent. Perfect for:
- Data transformation pipelines
- Content processing workflows
- Multi-stage analysis

### 3️⃣ Publish/Subscribe with AI Subscribers
**Port: 8002** | [📖 Documentation](pattern-3-pubsub/README.md)

Event-driven architecture with AI agents as intelligent subscribers. Perfect for:
- Event-driven microservices
- Real-time analytics
- Multi-consumer event processing

### 4️⃣ Command Messages with Async Pipelines
**Port: 8003** | [📖 Documentation](pattern-4-command-messages/README.md)

Command-driven architecture with asynchronous execution. Perfect for:
- Long-running operations
- Trackable command execution
- Async request/response

## 🚀 Quick Start

### Prerequisites

1. **Azure Services:**
   - Azure AI Foundry project with deployed model
   - Azure Event Hub namespace and hub

2. **Local Environment:**
   - Python 3.11+
   - Docker (optional)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Cataldir/reactor-enterprise-integration-agents.git
cd reactor-enterprise-integration-agents
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your Azure credentials
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Running Individual Patterns

Each pattern can run independently:

```bash
# Pattern 1: Message Queue
cd pattern-1-message-queue
python api.py  # Starts on port 8000

# Pattern 2: Pipes and Filters
cd pattern-2-pipes-filters
python api.py  # Starts on port 8001

# Pattern 3: Pub/Sub
cd pattern-3-pubsub
python api.py  # Starts on port 8002

# Pattern 4: Command Messages
cd pattern-4-command-messages
python api.py  # Starts on port 8003
```

### Using Docker

Each pattern has its own Dockerfile:

```bash
# Build pattern (example for Pattern 1)
cd pattern-1-message-queue
docker build -t message-queue-agent --target production .

# Run with environment file
docker run --env-file ../.env -p 8000:8000 message-queue-agent
```

## 🔧 Configuration

All patterns use the same environment variables:

```bash
# Azure AI Foundry
PROJECT_CONNECTION_STRING=your_connection_string

# Azure Event Hub
EVENTHUB_CONNECTION_STRING=your_eventhub_connection
EVENTHUB_NAME=your_hub_name

# Model Configuration
MODEL_DEPLOYMENT_NAME=gpt-4

# Logging
LOG_LEVEL=INFO
```

## 📚 Key Technologies

- **Azure AI Foundry (v2 SDK)** - Intelligent AI agents
- **Azure Event Hubs** - Enterprise message broker
- **FastAPI** - Modern web framework
- **MCP (Model Context Protocol)** - Standardized AI communication
- **Python 3.11+** - Modern async Python
- **Docker** - Containerization

## 🎯 Use Cases by Industry

### 🏦 Financial Services
- Transaction processing (Queue)
- Fraud detection pipeline (Pipes & Filters)
- Real-time risk monitoring (Pub/Sub)
- Account operations (Commands)

### 🛒 E-Commerce
- Order processing (Queue)
- Product data enrichment (Pipes & Filters)
- Inventory updates (Pub/Sub)
- Customer actions (Commands)

### 🏥 Healthcare
- Patient record processing (Queue)
- Medical data analysis (Pipes & Filters)
- Alert distribution (Pub/Sub)
- Treatment protocols (Commands)

### 📱 IoT/Smart Devices
- Sensor data processing (Queue)
- Data transformation (Pipes & Filters)
- Device event handling (Pub/Sub)
- Device control (Commands)

## 🔐 Security Best Practices

1. ✅ Use Azure Managed Identity
2. ✅ Store secrets in Azure Key Vault
3. ✅ Enable network isolation
4. ✅ Implement proper authentication
5. ✅ Monitor and audit access
6. ✅ Use least privilege principle

## 📖 Documentation

- [Architecture Guide](ARCHITECTURE.md) - Detailed system architecture
- [Pattern 1 Guide](pattern-1-message-queue/README.md) - Message Queue
- [Pattern 2 Guide](pattern-2-pipes-filters/README.md) - Pipes and Filters
- [Pattern 3 Guide](pattern-3-pubsub/README.md) - Pub/Sub
- [Pattern 4 Guide](pattern-4-command-messages/README.md) - Command Messages

## 🤝 Contributing

This is an educational repository for demonstrating enterprise integration patterns. Feel free to:
- Open issues for questions
- Submit PRs for improvements
- Share your use cases
- Provide feedback

## 📺 YouTube Content

This repository accompanies the YouTube series **"Deep Dive em Integrações Empresariais para Aplicações de AI"**. Each pattern's README is written in a presentation style suitable for video content.

## 📄 License

[MIT License](LICENSE)

## 🙏 Acknowledgments

Built with:
- Azure AI Foundry
- Azure Event Hubs
- FastAPI
- Python Community

---

**🔗 Useful Links:**
- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Azure Event Hubs Documentation](https://learn.microsoft.com/azure/event-hubs/)
- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

**#AzureAI #EnterpriseIntegration #AIAgents #Python #CloudComputing #Microservices**
