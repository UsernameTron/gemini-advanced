# Hybrid Architecture Migration Guide

## Overview
This guide explains how to migrate from the original VectorDBRAG agent system to the enhanced hybrid architecture that leverages MindMeld's agent framework while keeping both projects separate.

## Architecture

The new hybrid architecture follows these principles:

1. **Clear Project Boundaries**: VectorDBRAG and MindMeld-v1.1 remain separate projects.
2. **Shared Framework**: Core agent functionality extracted from MindMeld lives in `shared_agents` package.
3. **Enhanced Agent Implementation**: VectorDBRAG agents are reimplemented using the shared framework.
4. **Parallel Route Systems**: Both original and enhanced agents are accessible via separate routes.

## Shared Framework Components

The shared framework in `/shared_agents/core/` includes:

- `AgentBase`: Abstract base class for all agents
- `AgentFactory`: Factory for creating and registering agents
- `AgentCapability`: Enum defining agent capabilities
- `AgentResponse`: Standardized response format
- Validation and error handling utilities

## Enhanced Agent Implementation

Enhanced agents in VectorDBRAG are located at:

- `/VectorDBRAG/agents/enhanced/enhanced_agents.py`: Agent implementations
- `/VectorDBRAG/agents/enhanced/factory.py`: Factory for creating enhanced agents

## API Routes

Two sets of routes are available:

1. **Original VectorDBRAG Routes**:
   - `/api/agents/query`
   - `/api/agents/workflow` 

2. **Enhanced Agent Routes**:
   - `/api/enhanced/agents/query`
   - `/api/enhanced/agents/capability`
   - `/api/enhanced/agents/types`

## Migration Steps

1. **Install Dependencies**:
   ```bash
   # From project root
   pip install -r requirements.txt
   ```

2. **Test the Integration**:
   ```bash
   python test_enhanced_integration.py
   ```

3. **Update Configuration** (if needed):
   - Set OpenAI API key in `.env` file
   - Configure model preferences in `enhanced_agent_integration.py`

4. **Start the Server**:
   ```bash
   python VectorDBRAG/app.py
   ```

5. **Verify Installation**:
   - Visit `http://localhost:5001/` in your browser
   - Use the API tester to try both original and enhanced agents

## Feature Comparison

| Feature | Original Agents | Enhanced Agents |
|---------|----------------|----------------|
| Code Analysis | ✅ | ✅ |
| Code Debugging | ✅ | ✅ |
| Code Repair | ✅ | ✅ |
| Performance Analysis | ✅ | ✅ |
| Test Generation | ✅ | ✅ |
| Image Processing | ✅ | ✅ |
| Audio Processing | ✅ | ✅ |
| Strategic Planning | ✅ | ✅ |
| Research | ✅ | ✅ |
| Type Safety | ❌ | ✅ |
| Input Validation | ❌ | ✅ |
| Statistics Tracking | ❌ | ✅ |
| Capability System | ❌ | ✅ |

## Next Steps

- [ ] Integrate MindMeld's testing patterns into VectorDBRAG
- [ ] Set up shared configuration management
- [ ] Create comprehensive API documentation
- [ ] Implement end-to-end validation testing
