# 🎬 Pattern 2: Pipes and Filters with Cognitive Capabilities

## 📺 YouTube Presentation Style

What's up, cloud architects! 🚀 Today we're exploring one of the COOLEST enterprise integration patterns - **Pipes and Filters with AI superpowers**!

## 🎯 What's This Pattern About?

Think of it like an **assembly line for data**, but instead of robots, we have **AI agents** at each station! Each agent:
- 🔍 **Analyzes** the data
- 🎨 **Transforms** it intelligently  
- 🎯 **Passes** it to the next agent
- 🧠 **Learns** from context

## 🏗️ Architecture Overview

```
Input Data
    │
    ▼
┌─────────────────┐
│  Filter 1       │
│  (AI Agent)     │──► Sentiment Analysis
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Filter 2       │
│  (AI Agent)     │──► Entity Extraction
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Filter 3       │
│  (AI Agent)     │──► Summarization
└────────┬────────┘
         │
         ▼
    Output Data
```

### 🌟 Parallel Pipeline Option

```
                     ┌─► Filter A (Sentiment) ──┐
                     │                           │
Input Data ──────────┼─► Filter B (Topics) ─────┼──► All Results
                     │                           │
                     └─► Filter C (Language) ────┘
```

## 🔥 The Enterprise Integration Pattern

**Pipes and Filters** is a classic pattern where:

1. **Filters** - Independent processing units (our AI agents!)
2. **Pipes** - Data flow channels between filters
3. **Sequential** - Process one after another
4. **Parallel** - Process simultaneously for speed

### Why AI-Powered Filters Rock! 🎸

- ✅ **Context-Aware** - Agents understand what they're processing
- ✅ **Flexible** - Easy to add/remove/reorder filters
- ✅ **Scalable** - Each filter can scale independently
- ✅ **Reusable** - Filters can be used in multiple pipelines
- ✅ **Maintainable** - Change one filter without affecting others

## 🛠️ Technologies Used

- **Azure AI Foundry Agents** - Each filter is an AI agent 🤖
- **FastAPI** - REST API for pipeline execution 🚀
- **Async Python** - Non-blocking, concurrent processing ⚡
- **MCP Layer** - Standardized communication protocol 🔗
- **Pydantic** - Data validation and serialization ✅

## 🚀 Quick Start

### Prerequisites

1. Azure AI Foundry project configured
2. Python 3.11+
3. Environment variables set

### Setup

1. **Navigate to pattern:**
```bash
cd pattern-2-pipes-filters
```

2. **Configure environment:**
```bash
cp ../.env.example .env
# Edit with your credentials
```

3. **Install dependencies:**
```bash
pip install -r ../requirements.txt
```

### 🏃 Running the Application

**Option 1: Demo Script**
```bash
python main.py
```

**Option 2: REST API**
```bash
python api.py
# OR
uvicorn api:app --port 8001 --reload
```

### 🐳 Docker Deployment

**Build:**
```bash
# Production
docker build -t pipes-filters-agent --target production .

# Development
docker build -t pipes-filters-agent-dev --target development .
```

**Run:**
```bash
# Production
docker run --env-file .env pipes-filters-agent

# Development with hot reload
docker run -p 8001:8001 -v $(pwd):/app/pattern-2-pipes-filters --env-file .env pipes-filters-agent-dev
```

## 📡 API Endpoints

### Execute Custom Pipeline
```bash
POST /pipeline/execute
{
  "input_data": "Your text here...",
  "filters": [
    {
      "name": "Sentiment Analyzer",
      "instructions": "Analyze sentiment..."
    },
    {
      "name": "Entity Extractor",
      "instructions": "Extract entities..."
    }
  ],
  "parallel": false
}
```

### Preset: Text Analysis Pipeline
```bash
POST /pipeline/preset/text-analysis
{
  "input_text": "Microsoft announced Azure AI Foundry today..."
}
```

### Preset: Parallel Analysis
```bash
POST /pipeline/preset/parallel-analysis
{
  "input_text": "Your text for parallel processing..."
}
```

### Health Check
```bash
GET /health
```

## 💡 How It Works

### Sequential Pipeline

1. **Input** enters the pipeline
2. **Filter 1** processes and transforms
3. **Filter 2** receives Filter 1's output
4. **Filter 3** receives Filter 2's output
5. **Final output** is returned

Each filter adds value and context!

### Parallel Pipeline

1. **Input** is copied to all filters
2. **All filters** process simultaneously
3. **Results** are collected together
4. **All outputs** returned as array

Perfect for independent analyses!

## 🎓 Key Concepts

### CognitiveFilter Class
Each filter is an AI agent that:
- Has specific instructions
- Maintains conversation context
- Processes data intelligently
- Records transformations

```python
filter = CognitiveFilter(
    name="Sentiment Analyzer",
    project_client=client,
    agent_id=agent_id,
    instructions="Analyze sentiment..."
)
```

### Pipeline Composition
Build pipelines fluently:
```python
pipeline = Pipeline("My Pipeline")
    .add_filter(filter1)
    .add_filter(filter2)
    .add_filter(filter3)

result = await pipeline.execute(data)
```

### PipelineData
Carries information through the pipeline:
- **content** - The actual data
- **metadata** - Processing information
- **transformations** - Audit trail

## 📊 Real-World Use Cases

Perfect for:

1. 📄 **Document Processing**
   - Extract → Classify → Summarize → Store

2. 📧 **Email Processing**
   - Parse → Sentiment → Priority → Route

3. 🎥 **Content Moderation**
   - Detect → Analyze → Score → Action

4. 📊 **Data Enrichment**
   - Clean → Validate → Enhance → Format

5. 🔍 **Log Analysis**
   - Parse → Detect Patterns → Alert → Archive

## 🎯 Advanced Features

### Custom Filter Instructions
Tailor each filter's behavior:
```python
FilterConfig(
    name="Custom Analyzer",
    instructions="""
    You are an expert analyzer.
    Focus on: X, Y, Z
    Output format: JSON
    """
)
```

### Error Handling
Pipelines continue even if a filter fails:
- Failed filters are logged
- Metadata tracks status
- Downstream filters get last good output

### Performance Optimization
- Use parallel pipelines for independent tasks
- Reuse agent threads for multiple runs
- Async execution throughout

## 🔐 Best Practices

1. ✅ **Single Responsibility** - Each filter does ONE thing well
2. ✅ **Stateless Filters** - Don't depend on previous runs
3. ✅ **Clear Instructions** - Be specific with agent instructions
4. ✅ **Error Handling** - Always check filter status
5. ✅ **Logging** - Track transformations for debugging

## 📈 Monitoring

Track pipeline health:
- Execution time per filter
- Success/failure rates
- Transformation audit trail
- Agent performance metrics

```python
print(f"Transformations: {result.transformations}")
print(f"Metadata: {result.metadata}")
```

## 🎬 Coming Up Next!

In the next patterns:
- **Pattern 3**: Pub/Sub with agent subscribers
- **Pattern 4**: Command Messages with async pipelines

## 🙏 Don't Forget!

- 👍 Like this video
- 💬 Comment your use cases
- 📢 Share with your team
- 🔔 Subscribe for Pattern 3!

---

**🔗 Resources:**
- [Pipes and Filters Pattern](https://www.enterpriseintegrationpatterns.com/patterns/messaging/PipesAndFilters.html)
- [Azure AI Foundry](https://learn.microsoft.com/azure/ai-studio/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

**#EnterpriseIntegration #PipesAndFilters #AIAgents #AzureAI #CloudArchitecture**
