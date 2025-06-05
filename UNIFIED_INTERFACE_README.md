# Unified Meld & RAG Web Interface

A comprehensive web application that integrates the 12-agent AI system with vector database functionality, providing a unified command and control interface with shared session management.

## 🌟 Features

### 🤖 AI Agent System
- **12 Specialized Agents**: CEO, Executor, Triage, Research, Performance, Coaching, Code Analyzer, Code Debugger, Code Repair, Test Generator, Image, and Audio agents
- **Intelligent Routing**: Automatic task classification and agent selection
- **Unified Interface**: Single chat interface for all agents
- **Session Persistence**: Conversation history maintained across sessions

### 📚 Knowledge Base Integration
- **Vector Database**: ChromaDB-powered document storage and retrieval
- **Document Upload**: Support for PDF, TXT, DOCX files
- **Semantic Search**: AI-powered document search and retrieval
- **Context Enhancement**: Automatic knowledge base integration in agent responses

### 🔄 Session Management
- **Shared State**: Persistent session data across all components
- **Conversation History**: Chat history preservation
- **Document Tracking**: Upload history and file management
- **User Preferences**: Customizable settings and themes

### 🎨 Modern Web Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Themes**: User-selectable interface themes
- **Real-time Chat**: Instant messaging with AI agents
- **Drag & Drop Upload**: Easy document uploading
- **Status Monitoring**: System health and performance indicators

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- Required Python packages (auto-installed)

### Installation & Setup

1. **Clone or navigate to the project directory**:
   ```bash
   cd "/Users/cpconnor/projects/Meld and RAG"
   ```

2. **Set up your OpenAI API key**:
   ```bash
   # Create .env file in VectorDBRAG directory
   echo "OPENAI_API_KEY=your_api_key_here" > VectorDBRAG/.env
   ```

3. **Start the unified interface**:
   ```bash
   python start_unified_interface.py
   ```

4. **Access the web interface**:
   - Main Dashboard: http://localhost:5000
   - Legacy Dashboard: http://localhost:5000/dashboard
   - Analytics: http://localhost:5000/analytics

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────┐
│                Unified Web Interface            │
├─────────────────────────────────────────────────┤
│  • Flask Application with Session Management    │
│  • Responsive Web UI with Bootstrap             │
│  • Real-time Chat Interface                     │
│  • Document Upload & Management                 │
└─────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────┐
│              Agent Management Layer             │
├─────────────────────────────────────────────────┤
│  • UnifiedAgentManager                          │
│  • 12 Specialized AI Agents                     │
│  • Task Routing & Processing                    │
│  • Response Aggregation                         │
└─────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────┐
│            Knowledge Base & Analytics           │
├─────────────────────────────────────────────────┤
│  • ChromaDB Vector Storage                      │
│  • Document Processing Pipeline                 │
│  • Semantic Search Engine                       │
│  • Analytics Integration                        │
└─────────────────────────────────────────────────┘
```

### Key Files

- **`agent_system/web_interface.py`**: Main unified Flask application
- **`VectorDBRAG/templates/unified_dashboard.html`**: Primary web interface
- **`VectorDBRAG/unified_agent_system.py`**: Agent management system
- **`start_unified_interface.py`**: Startup script

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the `VectorDBRAG` directory:

```env
OPENAI_API_KEY=your_openai_api_key
FLASK_ENV=development
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

### Session Management
The system supports both in-memory and Redis-based session storage:

- **In-Memory** (default): Simple, no additional setup required
- **Redis**: Scalable, persistent sessions (requires Redis server)

## 🎯 Usage Guide

### Chat Interface

1. **Select an Agent**: Choose from 12 specialized agents in the sidebar
2. **Enable Knowledge Base**: Toggle to include document context in responses
3. **Send Messages**: Type your query and press Enter or click Send
4. **View Responses**: Agent responses include execution time and knowledge base usage indicators

### Document Management

1. **Upload Documents**: Drag & drop files or click the upload area
2. **Select Vector Store**: Choose which knowledge base to store documents
3. **Monitor Progress**: Real-time upload progress and status updates
4. **Search Documents**: Use the knowledge base toggle in chat for document-enhanced responses

### Agent Selection Guide

| Agent | Best For | Use Cases |
|-------|----------|-----------|
| **Research** | Information gathering, analysis | Market research, data analysis |
| **CEO** | Strategic decisions, planning | Business strategy, high-level planning |
| **Performance** | Optimization, metrics | Performance analysis, KPI review |
| **Coaching** | Learning, improvement | Skill development, feedback |
| **Triage** | Task classification | Request routing, priority assessment |
| **Code Analyzer** | Code review, analysis | Code quality, architecture review |
| **Code Debugger** | Bug finding, fixing | Error diagnosis, debugging |
| **Code Repair** | Code improvement | Refactoring, optimization |
| **Test Generator** | Test creation | Unit tests, integration tests |
| **Image** | Image processing | Image analysis, generation |
| **Audio** | Audio processing | Audio analysis, generation |

## 🔌 API Endpoints

### Unified Interface Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | Main unified dashboard |
| `/api/session/status` | GET | Session information |
| `/api/unified/chat` | POST | Chat with agents |
| `/api/unified/upload` | POST | Upload documents |
| `/api/unified/vector-stores` | GET | List vector stores |
| `/api/unified/preferences` | POST | Update user preferences |

### Legacy Endpoints
All existing VectorDBRAG endpoints remain available for backward compatibility.

## 🔍 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**:
   ```
   Error: OpenAI API key not found
   Solution: Set OPENAI_API_KEY in VectorDBRAG/.env file
   ```

2. **Agent Not Responding**:
   ```
   Check: System status in the top status bar
   Solution: Refresh page or restart application
   ```

3. **File Upload Fails**:
   ```
   Check: Vector store selected and file type supported
   Solution: Select a vector store before uploading
   ```

### Debug Mode
Run with debug enabled for detailed logging:
```bash
FLASK_ENV=development python start_unified_interface.py
```

## 🚀 Advanced Features

### Session Persistence
- Conversations are automatically saved
- Document upload history is maintained
- User preferences persist across sessions
- Session data includes timestamps and metadata

### Theme Customization
The interface supports custom themes via CSS variables:
```css
:root {
  --primary-color: #2563eb;
  --secondary-color: #10b981;
  --background-color: #ffffff;
}
```

### Multi-Agent Workflows
Chain multiple agents for complex tasks:
1. Use Triage agent to classify the request
2. Route to appropriate specialist agent
3. Use Research agent for additional context
4. Apply results through Code Repair or other action agents

## 📊 Monitoring & Analytics

### System Health
- Real-time system status indicator
- Agent availability monitoring
- Session timer and activity tracking
- Vector store status and file counts

### Usage Analytics
- Conversation history and patterns
- Agent usage statistics
- Document access patterns
- Response time metrics

## 🔄 Migration from Gradio

This unified interface replaces the previous Gradio-based interfaces:

| Old Interface | New Location | Migration Notes |
|---------------|--------------|-----------------|
| Gradio Agent Chat | Unified Dashboard Chat | Full feature parity + enhancements |
| Gradio File Upload | Unified Dashboard Upload | Improved UI + session tracking |
| Separate Agent UIs | Single Agent Selector | All agents in one interface |

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Run tests: `python -m pytest`
5. Submit a pull request

### Code Structure
- **Frontend**: HTML/CSS/JavaScript (no build process required)
- **Backend**: Flask with modular design
- **Agents**: Existing agent framework (no changes needed)
- **Storage**: ChromaDB for vectors, filesystem for sessions

## 📝 License

This project is part of the Meld and RAG system. See the main project license for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the system health indicators
3. Check logs for detailed error messages
4. Ensure all dependencies are installed

---

**Status**: ✅ Production Ready  
**Version**: 2.0.0  
**Last Updated**: June 2025
