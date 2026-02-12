# 🏗️ Architecture Documentation

## Enterprise Integration Agents with Azure AI Foundry

This document provides a comprehensive overview of the architecture, design decisions, and implementation details for the enterprise integration patterns using Azure AI Foundry agents.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [System Architecture](#system-architecture)
4. [Components](#components)
5. [Integration Patterns](#integration-patterns)
6. [Data Flow](#data-flow)
7. [Security Architecture](#security-architecture)
8. [Scalability & Performance](#scalability--performance)
9. [Deployment Architecture](#deployment-architecture)
10. [Monitoring & Observability](#monitoring--observability)

---

## Overview

### Purpose

This system demonstrates how **Azure AI Foundry agents** can be integrated into enterprise applications using established **Enterprise Integration Patterns (EIP)**. By combining cognitive capabilities with proven integration patterns, we create intelligent, scalable, and maintainable enterprise solutions.

### Goals

- ✅ Demonstrate practical use of Azure AI Foundry v2 SDK
- ✅ Implement four core enterprise integration patterns
- ✅ Provide production-ready, containerized solutions
- ✅ Establish standardized communication via MCP
- ✅ Enable async, non-blocking operations
- ✅ Facilitate independent scaling of components

---

## Architecture Principles

### 1. Loose Coupling

Components communicate through **Azure Event Hub** and **MCP layer**, not directly:
- Publishers don't know about subscribers
- Filters don't depend on adjacent filters
- Processors are independent of command submitters

### 2. High Cohesion

Each pattern is self-contained:
- Pattern-specific logic stays within pattern folder
- Shared utilities in common location
- Clear separation of concerns

### 3. Asynchronous First

All I/O operations are async:
- Non-blocking Event Hub operations
- Concurrent agent processing
- Parallel pipeline execution

### 4. Cognitive Enhancement

AI agents add intelligence:
- Context-aware processing
- Natural language understanding
- Adaptive decision making
- Learning from interactions

### 5. Observable

Built-in observability:
- Structured logging
- Status tracking
- Metrics collection
- Error handling

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Azure Cloud                                 │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │              Azure AI Foundry Service                        │ │
│  │                                                              │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │   Agent 1   │  │   Agent 2   │  │   Agent N   │        │ │
│  │  │  (GPT-4)    │  │  (GPT-4)    │  │  (GPT-4)    │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  │                                                              │ │
│  └──────────────┬───────────────────────────────────────────────┘ │
│                 │                                                  │
│                 │ Azure AI SDK v2                                  │
│                 ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │              Integration Application Layer                    │ │
│  │                                                              │ │
│  │  ┌─────────────────────────────────────────────────────┐   │ │
│  │  │          MCP Integration Layer                      │   │ │
│  │  │  (Model Context Protocol + FastAPI)                 │   │ │
│  │  └───────┬─────────────────────────────────────────────┘   │ │
│  │          │                                                  │ │
│  │          ├─────────┬──────────┬──────────┬──────────┐     │ │
│  │          ▼         ▼          ▼          ▼          ▼     │ │
│  │  ┌──────────┐ ┌────────┐ ┌────────┐ ┌──────────┐ ┌────┐ │ │
│  │  │Pattern 1 │ │Pattern2│ │Pattern3│ │Pattern 4 │ │Util│ │ │
│  │  │:8000     │ │:8001   │ │:8002   │ │:8003     │ │    │ │ │
│  │  └────┬─────┘ └───┬────┘ └───┬────┘ └────┬─────┘ └────┘ │ │
│  │       │           │          │           │               │ │
│  └───────┼───────────┼──────────┼───────────┼───────────────┘ │
│          │           │          │           │                  │
│          └───────────┴──────────┴───────────┘                  │
│                      │                                          │
│                      ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Azure Event Hub                                │  │
│  │           (Message Broker)                               │  │
│  │                                                          │  │
│  │  Topics: customer_events, order_events, system_events   │  │
│  │  Queues: command_queue, task_queue                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Component Layers

#### Layer 1: Azure AI Foundry
- Hosts AI agents with specialized capabilities
- Provides conversation threads for context
- Executes intelligent processing

#### Layer 2: MCP Integration Layer
- Standardizes communication protocol
- Provides REST API interface
- Handles message routing
- Manages agent interactions

#### Layer 3: Pattern Implementations
- Four independent integration patterns
- Each with own API server
- Containerized for deployment
- Shares common utilities

#### Layer 4: Message Broker
- Azure Event Hub for reliable messaging
- Topic-based routing
- Queue-based task distribution
- Guaranteed delivery

---

## Components

### Shared Components

#### 1. MCP Base Layer (`shared/mcp/__init__.py`)

**Purpose:** Standardize communication between components

**Key Classes:**
- `MCPMessage` - Standard message format
- `MCPAdapter` - Abstract message broker adapter
- `MCPRouter` - Routes messages to handlers

**Design Pattern:** Abstract Factory + Strategy

#### 2. FastAPI MCP (`shared/mcp/fastapi_mcp.py`)

**Purpose:** REST API server for MCP operations

**Features:**
- Message submission endpoint
- Handler registration
- Health checks
- Automatic routing

**Port Allocation:**
- Pattern 1: 8000
- Pattern 2: 8001
- Pattern 3: 8002
- Pattern 4: 8003

#### 3. Agent Utilities (`shared/utils/agent_utils.py`)

**Purpose:** Manage Azure AI Foundry agents

**Functions:**
- `get_project_client()` - Initialize AI client
- `load_env_config()` - Load configuration
- `create_agent()` - Create specialized agents

#### 4. Event Hub Utilities (`shared/utils/eventhub_utils.py`)

**Purpose:** Manage Azure Event Hub integration

**Class: EventHubAdapter**
- `send_event()` - Publish messages
- `receive_events()` - Consume messages
- Connection pooling
- Automatic checkpointing

---

## Integration Patterns

### Pattern 1: Message Queue Monitor and Executor

#### Architecture
```
Producer → Event Hub Queue → AI Agent Monitor → Process & Execute
```

#### Components
- `MessageQueueAgent` - Monitors and processes queue messages
- FastAPI server for message submission
- Event Hub for queue storage

#### Flow
1. Client submits task to API
2. Task queued in Event Hub
3. Agent polls queue
4. Agent processes with AI
5. Result stored and logged

#### Use Cases
- Background job processing
- Task distribution
- Asynchronous operations

---

### Pattern 2: Pipes and Filters

#### Architecture
```
Input → Filter 1 (Agent) → Filter 2 (Agent) → Filter N (Agent) → Output
```

#### Components
- `CognitiveFilter` - AI-powered filter
- `Pipeline` - Sequential orchestration
- `ParallelPipeline` - Concurrent execution
- `PipelineData` - Data container with metadata

#### Flow
1. Input data enters pipeline
2. Each filter transforms data using AI
3. Transformations tracked
4. Final output returned

#### Modes
- **Sequential:** Filters execute one after another
- **Parallel:** Filters execute simultaneously

#### Use Cases
- Data transformation pipelines
- Multi-stage content processing
- ETL operations

---

### Pattern 3: Publish/Subscribe

#### Architecture
```
Publishers → Topics (Event Hub) → Multiple AI Subscriber Agents
```

#### Components
- `AgentSubscriber` - AI agent that subscribes to topics
- `PubSubBroker` - Manages subscriptions and routing
- `Message` - Topic-based message
- `TopicType` - Enum of available topics

#### Flow
1. Publisher sends message to topic
2. Event Hub broadcasts to all subscribers
3. Interested agents process in parallel
4. Each provides unique analysis

#### Topics
- `customer_events` - Customer interactions
- `order_events` - Order processing
- `system_events` - System operations
- `analytics_events` - Business intelligence

#### Use Cases
- Event-driven microservices
- Real-time analytics
- Multi-consumer event processing

---

### Pattern 4: Command Messages

#### Architecture
```
Client → Command (Event Hub) → Processor Agent → Result Tracking
```

#### Components
- `CommandMessage` - Command with parameters and status
- `CommandProcessor` - AI agent that executes commands
- `AsyncCommandPipeline` - Async orchestration
- `CommandStatus` - Lifecycle tracking

#### Flow
1. Client submits command
2. Command queued with unique ID
3. Processor picks up command
4. AI agent executes
5. Status updated
6. Client polls for results

#### Command Types
- `process_data` - Data operations
- `analyze_content` - Content analysis
- `generate_report` - Report creation
- `validate_input` - Validation
- `transform_data` - Transformations

#### Use Cases
- Long-running operations
- Trackable execution
- Auditable commands
- Async request/response

---

## Data Flow

### Message Flow Pattern

All patterns follow similar message flow:

```
┌────────────┐
│   Client   │
└─────┬──────┘
      │ 1. HTTP Request
      ▼
┌────────────────┐
│   FastAPI      │
│   MCP Server   │
└────────┬───────┘
         │ 2. MCP Message
         ▼
┌───────────────────┐
│   Event Hub       │
│   (Async Queue)   │
└────────┬──────────┘
         │ 3. Event Stream
         ▼
┌───────────────────┐
│   Pattern Logic   │
│   (Processor)     │
└────────┬──────────┘
         │ 4. AI Request
         ▼
┌───────────────────┐
│  Azure AI Agent   │
│  (GPT-4)          │
└────────┬──────────┘
         │ 5. AI Response
         ▼
┌───────────────────┐
│   Result Store    │
│   (In-Memory)     │
└───────────────────┘
```

### Data Transformation

#### Pattern 1: Queue Processing
```
Task Description → AI Analysis → Action Recommendations
```

#### Pattern 2: Pipeline Processing
```
Raw Data → Filter 1 → Filter 2 → Filter N → Enriched Data
```

#### Pattern 3: Pub/Sub Processing
```
Event → Topic → [Agent 1, Agent 2, Agent N] → Multiple Analyses
```

#### Pattern 4: Command Processing
```
Command + Parameters → AI Execution → Result + Status
```

---

## Security Architecture

### Authentication & Authorization

1. **Azure Managed Identity**
   - Recommended for production
   - No credential storage
   - Automatic token refresh

2. **Connection Strings**
   - Development/testing
   - Stored in environment variables
   - Never committed to source

### Network Security

```
┌─────────────────────────────────────────┐
│           Azure VNET                    │
│                                         │
│  ┌──────────────┐    ┌──────────────┐ │
│  │  App Service │    │  Event Hub   │ │
│  │  (Private)   │───→│  (Private)   │ │
│  └──────────────┘    └──────────────┘ │
│         │                    │         │
│         └────────┬───────────┘         │
│                  │                     │
│                  ▼                     │
│         ┌──────────────┐              │
│         │  AI Foundry  │              │
│         │  (Private)   │              │
│         └──────────────┘              │
│                                         │
└─────────────────────────────────────────┘
```

### Data Protection

1. **In Transit**
   - TLS 1.2+ for all connections
   - Azure Event Hub encryption
   - HTTPS for APIs

2. **At Rest**
   - Azure storage encryption
   - Event Hub data encryption
   - No PII in logs

### Best Practices

- ✅ Use Azure Key Vault for secrets
- ✅ Enable network isolation
- ✅ Implement least privilege access
- ✅ Audit all operations
- ✅ Rotate credentials regularly
- ✅ Monitor for anomalies

---

## Scalability & Performance

### Horizontal Scaling

Each pattern scales independently:

```
┌─────────────────────────────────────────────┐
│              Load Balancer                  │
└───────┬─────────┬─────────┬────────┬────────┘
        │         │         │        │
        ▼         ▼         ▼        ▼
    ┌────┐    ┌────┐    ┌────┐   ┌────┐
    │ P1 │    │ P1 │    │ P1 │   │ P1 │
    │:8000   │:8000   │:8000   │:8000
    └────┘    └────┘    └────┘   └────┘
```

### Performance Characteristics

#### Pattern 1: Message Queue
- **Throughput:** ~1000 msgs/sec
- **Latency:** 100-500ms per message
- **Bottleneck:** AI agent processing time

#### Pattern 2: Pipes & Filters
- **Sequential:** Sum of filter latencies
- **Parallel:** Max filter latency
- **Bottleneck:** Slowest filter

#### Pattern 3: Pub/Sub
- **Fan-out:** 1:N message delivery
- **Parallel:** All subscribers process concurrently
- **Bottleneck:** Event Hub throughput

#### Pattern 4: Commands
- **Async:** Client doesn't wait
- **Status polling:** Minimal overhead
- **Bottleneck:** Processor count

### Optimization Strategies

1. **Agent Pooling**
   - Reuse agent threads
   - Reduce cold start time

2. **Batching**
   - Batch Event Hub operations
   - Reduce API calls

3. **Caching**
   - Cache agent responses
   - Reduce duplicate processing

4. **Connection Pooling**
   - Reuse connections
   - Reduce handshake overhead

---

## Deployment Architecture

### Container Deployment

Each pattern deploys as a container:

```yaml
# docker-compose.yml
version: '3.8'
services:
  pattern-1:
    build:
      context: .
      dockerfile: pattern-1-message-queue/Dockerfile
    ports:
      - "8000:8000"
    env_file: .env
    
  pattern-2:
    build:
      context: .
      dockerfile: pattern-2-pipes-filters/Dockerfile
    ports:
      - "8001:8001"
    env_file: .env
    
  pattern-3:
    build:
      context: .
      dockerfile: pattern-3-pubsub/Dockerfile
    ports:
      - "8002:8002"
    env_file: .env
    
  pattern-4:
    build:
      context: .
      dockerfile: pattern-4-command-messages/Dockerfile
    ports:
      - "8003:8003"
    env_file: .env
```

### Kubernetes Deployment

```yaml
# pattern-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pattern-1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pattern-1
  template:
    metadata:
      labels:
        app: pattern-1
    spec:
      containers:
      - name: pattern-1
        image: myregistry/pattern-1:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: azure-credentials
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
---
apiVersion: v1
kind: Service
metadata:
  name: pattern-1-service
spec:
  selector:
    app: pattern-1
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
```

### Azure Container Apps

Recommended for serverless deployment:
- Automatic scaling
- Managed infrastructure
- Built-in load balancing
- Pay-per-use pricing

---

## Monitoring & Observability

### Logging Strategy

```python
import logging

# Structured logging
logger.info(
    "Processing message",
    extra={
        "message_id": message.id,
        "pattern": "message-queue",
        "status": "processing",
        "duration_ms": 150,
    }
)
```

### Key Metrics

#### Application Metrics
- Requests per second
- Response time (p50, p95, p99)
- Error rate
- Agent processing time

#### Pattern-Specific Metrics
- Queue depth (Pattern 1)
- Pipeline throughput (Pattern 2)
- Subscriber count (Pattern 3)
- Command status distribution (Pattern 4)

### Monitoring Stack

```
Application → Azure Monitor → Log Analytics
                           → Application Insights
                           → Alerts & Dashboards
```

### Health Checks

Each pattern implements:
- `/health` - Basic health
- `/ready` - Readiness probe
- `/live` - Liveness probe

---

## Conclusion

This architecture provides:
- ✅ **Scalable** - Each component scales independently
- ✅ **Resilient** - Fault isolation between patterns
- ✅ **Observable** - Comprehensive logging and metrics
- ✅ **Secure** - Azure best practices
- ✅ **Maintainable** - Clear separation of concerns
- ✅ **Cognitive** - AI-enhanced processing

The combination of proven enterprise integration patterns with modern AI capabilities creates a powerful foundation for building intelligent enterprise applications.
