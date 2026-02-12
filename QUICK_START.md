# 🚀 Quick Reference Guide

## Getting Started in 5 Minutes

### Step 1: Clone & Configure (2 min)
```bash
git clone https://github.com/Cataldir/reactor-enterprise-integration-agents.git
cd reactor-enterprise-integration-agents
cp .env.example .env
# Edit .env with your Azure credentials
```

### Step 2: Start All Patterns (2 min)
```bash
./start.sh up
```

### Step 3: Try the APIs (1 min)
Visit these URLs in your browser:
- Pattern 1: http://localhost:8000/docs
- Pattern 2: http://localhost:8001/docs
- Pattern 3: http://localhost:8002/docs
- Pattern 4: http://localhost:8003/docs

---

## 📡 API Quick Reference

### Pattern 1: Message Queue (Port 8000)

**Submit Task to Queue:**
```bash
curl -X POST "http://localhost:8000/queue/send" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Process customer order",
    "data": {"order_id": "12345"},
    "priority": 1
  }'
```

**Start Agent Monitor:**
```bash
curl -X POST "http://localhost:8000/agent/start"
```

### Pattern 2: Pipes & Filters (Port 8001)

**Execute Text Analysis Pipeline:**
```bash
curl -X POST "http://localhost:8001/pipeline/preset/text-analysis" \
  -H "Content-Type: application/json" \
  -d '"Your text to analyze here"'
```

**Custom Pipeline:**
```bash
curl -X POST "http://localhost:8001/pipeline/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": "Your data",
    "filters": [
      {
        "name": "Filter 1",
        "instructions": "Process this..."
      }
    ],
    "parallel": false
  }'
```

### Pattern 3: Pub/Sub (Port 8002)

**Publish Message:**
```bash
curl -X POST "http://localhost:8002/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "customer_events",
    "payload": {
      "event_type": "feedback",
      "customer_id": "C123",
      "rating": 5
    }
  }'
```

**Create Subscriber:**
```bash
curl -X POST "http://localhost:8002/subscribers/preset/customer-service"
```

**Start Consumers:**
```bash
curl -X POST "http://localhost:8002/consumers/start"
```

### Pattern 4: Command Messages (Port 8003)

**Submit Command:**
```bash
curl -X POST "http://localhost:8003/commands/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "command_type": "process_data",
    "parameters": {
      "data": [1, 2, 3, 4, 5],
      "operation": "calculate_statistics"
    }
  }'
```

**Check Status:**
```bash
curl "http://localhost:8003/commands/{command_id}"
```

**Create Processor:**
```bash
curl -X POST "http://localhost:8003/processors/preset/data-processor"
```

**Start Pipeline:**
```bash
curl -X POST "http://localhost:8003/pipeline/start"
```

---

## 🐳 Docker Commands

### All Patterns
```bash
./start.sh up       # Start all
./start.sh down     # Stop all
./start.sh logs     # View logs
./start.sh status   # Check status
./start.sh restart  # Restart all
./start.sh clean    # Clean up everything
```

### Individual Pattern
```bash
# Build
cd pattern-1-message-queue
docker build -t pattern-1 --target production .

# Run
docker run --env-file ../.env -p 8000:8000 pattern-1

# Development mode
docker build -t pattern-1-dev --target development .
docker run --env-file ../.env -p 8000:8000 -v $(pwd):/app/pattern-1-message-queue pattern-1-dev
```

---

## 🔧 Environment Variables

Required in `.env`:
```bash
# Azure AI Foundry
PROJECT_CONNECTION_STRING=your_connection_string

# Azure Event Hub
EVENTHUB_CONNECTION_STRING=your_eventhub_connection
EVENTHUB_NAME=your_hub_name

# Optional
MODEL_DEPLOYMENT_NAME=gpt-4
LOG_LEVEL=INFO
```

---

## 📂 Project Structure

```
reactor-enterprise-integration-agents/
├── shared/                    # Shared utilities
│   ├── mcp/                  # MCP integration layer
│   └── utils/                # Common utilities
├── pattern-1-message-queue/   # Queue pattern
├── pattern-2-pipes-filters/   # Pipeline pattern
├── pattern-3-pubsub/         # Pub/Sub pattern
├── pattern-4-command-messages/ # Command pattern
├── docker-compose.yml        # All patterns orchestration
├── start.sh                  # Startup script
└── requirements.txt          # Dependencies
```

---

## 🎯 Use Case Selection

**Choose Pattern 1 (Queue)** when:
- Background job processing
- Task distribution
- Work queue management

**Choose Pattern 2 (Pipes & Filters)** when:
- Data transformation pipelines
- Multi-stage processing
- ETL operations

**Choose Pattern 3 (Pub/Sub)** when:
- Event-driven architecture
- Multiple consumers per event
- Real-time notifications

**Choose Pattern 4 (Commands)** when:
- Long-running operations
- Status tracking needed
- Request/reply pattern

---

## 🐛 Troubleshooting

### Connection Issues
```bash
# Check Azure credentials
echo $PROJECT_CONNECTION_STRING
echo $EVENTHUB_CONNECTION_STRING

# Test Event Hub connectivity
# (Use Azure Portal to verify hub exists)
```

### Docker Issues
```bash
# Clean Docker environment
./start.sh clean

# Rebuild from scratch
docker-compose build --no-cache
./start.sh up
```

### Port Conflicts
```bash
# Check what's using the ports
lsof -i :8000
lsof -i :8001
lsof -i :8002
lsof -i :8003

# Change ports in docker-compose.yml if needed
```

### Agent Issues
```bash
# Check agent creation
# Look for "Created agent" in logs
./start.sh logs | grep "Created agent"

# Verify Azure AI Foundry quota
# Check Azure Portal for deployment limits
```

---

## 📚 Learn More

- [Main README](README.md) - Project overview
- [Architecture](ARCHITECTURE.md) - Detailed architecture
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Complete details
- [Pattern 1 Guide](pattern-1-message-queue/README.md)
- [Pattern 2 Guide](pattern-2-pipes-filters/README.md)
- [Pattern 3 Guide](pattern-3-pubsub/README.md)
- [Pattern 4 Guide](pattern-4-command-messages/README.md)

---

## 💡 Quick Tips

1. **Start Simple:** Try Pattern 1 first
2. **Check Logs:** Use `./start.sh logs` frequently
3. **Use Swagger:** Visit `/docs` on each port
4. **Monitor Azure:** Watch Event Hub metrics in portal
5. **Scale:** Add replicas in docker-compose.yml

---

## 🆘 Getting Help

1. Check the documentation in each pattern's README
2. Review logs: `./start.sh logs`
3. Validate environment: `cat .env`
4. Check Azure portal for service health
5. Open an issue on GitHub

---

**Happy Integrating! 🚀**
