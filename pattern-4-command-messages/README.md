# 🎬 Pattern 4: Command Messages with Asynchronous Pipelines

## 📺 YouTube Presentation Style

Hey architects! 👨‍💻 Ready for the FINAL pattern? This is where **command-driven architecture meets AI intelligence**! Let's build **Command Messages with Async Pipelines**!

## 🎯 What Are Command Messages?

Think of it like **issuing orders** to your system:
- 📋 **Commands** - Specific actions to execute
- 🤖 **AI Processors** - Intelligent command executors
- ⚡ **Async Processing** - Non-blocking execution
- 📊 **Status Tracking** - Real-time progress monitoring

Commands aren't just data - they're **actionable instructions**! 🎯

## 🏗️ Architecture Overview

```
┌─────────────┐
│   Client    │
│  Submits    │
│  Command    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Command Queue  │
│  (Event Hub)    │
└────────┬────────┘
         │
         ├──────────────────┬──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ Data Processor │  │ Content        │  │ Report         │
│     Agent      │  │ Analyzer       │  │ Generator      │
│                │  │ Agent          │  │ Agent          │
│ Commands:      │  │                │  │                │
│ - Process      │  │ Commands:      │  │ Commands:      │
│ - Transform    │  │ - Analyze      │  │ - Generate     │
└────────────────┘  └────────────────┘  └────────────────┘
         │                  │                  │
         └──────────────────┴──────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    Results    │
                    │   Tracking    │
                    └───────────────┘
```

## 🔥 The Enterprise Integration Pattern

**Command Message** pattern features:

1. **Command** - Explicit instruction with parameters
2. **Processor** - Agent that executes the command
3. **Async Execution** - Non-blocking, parallel processing
4. **Status Updates** - Track command lifecycle
5. **Result Retrieval** - Get outcomes when ready

### Why Command Pattern Rocks! 🎸

- ✅ **Intent-Driven** - Commands express clear intent
- ✅ **Trackable** - Every command has an ID and status
- ✅ **Auditable** - Full command history
- ✅ **Asynchronous** - Don't wait for long operations
- ✅ **Scalable** - Add processors without changing submitters

## 🛠️ Technologies Used

- **Azure Event Hub** - Command queue ⚡
- **Azure AI Foundry Agents** - Command processors 🤖
- **Async Python** - Non-blocking execution 🚀
- **FastAPI + MCP** - REST API with status tracking 📡
- **Command Pattern** - Clean separation of concerns 🎯

## 🚀 Quick Start

### Prerequisites

1. Azure Event Hub configured
2. Azure AI Foundry project
3. Python 3.11+

### Setup

1. **Navigate:**
```bash
cd pattern-4-command-messages
```

2. **Configure:**
```bash
cp ../.env.example .env
# Add credentials
```

3. **Install:**
```bash
pip install -r ../requirements.txt
```

### 🏃 Running

**Option 1: Demo**
```bash
python main.py
```

**Option 2: REST API**
```bash
python api.py
# OR
uvicorn api:app --port 8003 --reload
```

### 🐳 Docker

**Build:**
```bash
# Production
docker build -t command-messages-agent --target production .

# Development
docker build -t command-messages-agent-dev --target development .
```

**Run:**
```bash
# Production
docker run --env-file .env command-messages-agent

# Development
docker run -p 8003:8003 -v $(pwd):/app/pattern-4-command-messages --env-file .env command-messages-agent-dev
```

## 📡 API Endpoints

### Submit Command
```bash
POST /commands/submit
{
  "command_type": "process_data",
  "parameters": {
    "data": [1, 2, 3, 4, 5],
    "operation": "calculate_statistics"
  },
  "metadata": {
    "priority": "high"
  }
}

Response:
{
  "command_id": "uuid-here",
  "command_type": "process_data",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00"
}
```

### Check Command Status
```bash
GET /commands/{command_id}

Response:
{
  "command_id": "uuid",
  "command_type": "process_data",
  "status": "completed",
  "result": {
    "processor": "Data Processor",
    "response": "Statistics calculated...",
    "execution_time": "2024-01-01T00:00:05"
  },
  "error": null,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:05"
}
```

### Create Custom Processor
```bash
POST /processors/create
{
  "name": "Custom Processor",
  "command_types": ["process_data"],
  "instructions": "Process data according to..."
}
```

### Create Preset Processors
```bash
POST /processors/preset/data-processor
POST /processors/preset/content-analyzer
POST /processors/preset/report-generator
POST /processors/preset/validator
```

### List Processors
```bash
GET /processors
```

### Start Pipeline
```bash
POST /pipeline/start
```

### List Command Types
```bash
GET /command-types
```

## 💡 How It Works

### 1. Command Types
Five command types available:
- `process_data` - Data processing operations
- `analyze_content` - Content analysis
- `generate_report` - Report generation
- `validate_input` - Input validation
- `transform_data` - Data transformation

### 2. Command Submission
Client submits command:
```python
command = CommandMessage(
    command_id=uuid.uuid4(),
    command_type=CommandType.PROCESS_DATA,
    parameters={"data": [...], "operation": "..."},
)
await pipeline.submit_command(command)
```

### 3. Async Processing
- Command queued in Event Hub
- Pipeline picks it up
- Routes to appropriate processor
- Processor executes using AI
- Status updated in real-time

### 4. Result Retrieval
- Poll command status endpoint
- Get results when completed
- Handle errors if failed

## 🎓 Key Concepts

### CommandMessage
Complete command specification:
- **command_id** - Unique identifier
- **command_type** - What to do
- **parameters** - How to do it
- **status** - Current state
- **result** - Execution outcome

### CommandProcessor
AI-powered executor:
- Handles specific command types
- Uses AI agent for intelligence
- Updates command status
- Returns structured results

### AsyncCommandPipeline
Orchestration layer:
- Receives commands
- Routes to processors
- Tracks status
- Manages Event Hub communication

## 📊 Real-World Use Cases

Perfect for:

1. 📄 **Document Processing**
   - Command: "process_document"
   - Params: document_id, operations
   - Result: Processed document

2. 🔍 **Search Operations**
   - Command: "search_content"
   - Params: query, filters
   - Result: Search results

3. 📧 **Email Campaigns**
   - Command: "send_campaign"
   - Params: recipients, template
   - Result: Send status

4. 📊 **Report Generation**
   - Command: "generate_report"
   - Params: data_source, format
   - Result: Generated report

5. 🔄 **Data Migration**
   - Command: "migrate_data"
   - Params: source, destination
   - Result: Migration status

## 🎯 Advanced Features

### Command Status Lifecycle
```
PENDING → PROCESSING → COMPLETED
                    ↓
                  FAILED
```

### Multiple Processors per Type
Multiple agents can handle same command type:
- Load balancing
- Redundancy
- Specialization

### Command Metadata
Track additional context:
- Priority levels
- User information
- Correlation IDs
- Tags and labels

### Error Handling
Robust error management:
- Automatic retry logic
- Dead letter queues
- Error notifications
- Detailed error messages

## 🔐 Best Practices

1. ✅ **Idempotency** - Commands can be retried safely
2. ✅ **Timeouts** - Set execution time limits
3. ✅ **Validation** - Validate parameters before processing
4. ✅ **Logging** - Track all command executions
5. ✅ **Monitoring** - Alert on failures and slow commands

## 📈 Monitoring & Metrics

Track key metrics:
- Commands submitted per type
- Average processing time
- Success/failure rates
- Processor utilization
- Queue depth

```python
processor_info = {
    "name": processor.name,
    "command_types": processor.command_types,
    "processed_count": processor.processed_commands,
}
```

## 🆚 Command vs Event Patterns

| Aspect | Command | Event |
|--------|---------|-------|
| **Intent** | Do something | Something happened |
| **Direction** | Point-to-point | Broadcast |
| **Response** | Expected | Optional |
| **Tracking** | By ID | By correlation |

## 🎬 Series Wrap-Up!

We've covered all 4 patterns:
1. ✅ **Message Queue** - Intelligent monitoring
2. ✅ **Pipes & Filters** - Cognitive transformations
3. ✅ **Pub/Sub** - Event-driven agents
4. ✅ **Command Messages** - Async command execution

## 🙏 Thank You!

You made it to the end! 🎉

- 👍 Like if you learned something
- 💬 Comment your favorite pattern
- 📢 Share the entire series
- 🔔 Subscribe for more!

---

**🔗 Resources:**
- [Command Message Pattern](https://www.enterpriseintegrationpatterns.com/patterns/messaging/CommandMessage.html)
- [Azure Event Hubs](https://learn.microsoft.com/azure/event-hubs/)
- [Azure AI Foundry](https://learn.microsoft.com/azure/ai-studio/)
- [Async Python](https://docs.python.org/3/library/asyncio.html)

**#CommandPattern #AsyncProgramming #AIAgents #AzureAI #EnterpriseIntegration**
