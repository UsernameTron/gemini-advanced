"""
Unified Web Interface for Meld and RAG System
Integrates Agent Framework with Vector Database and provides shared session state
"""

import os
import uuid
import json
import time
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session, current_app
from flask_cors import CORS
from flask_session import Session
from werkzeug.utils import secure_filename
import redis

# Import existing components from VectorDBRAG
import sys
sys.path.append('/Users/cpconnor/projects/UnifiedAIPlatform/VectorDBRAG')

from search_system import SearchSystem
from config import Config
from unified_agent_system import UnifiedAgentManager, AgentType, TaskComplexity, AgentTask
from integrations.analytics_integration import AnalyticsIntegration

import base64
from services.tts_service import TTSService

# Import voice configuration system
sys.path.append('/Users/cpconnor/projects/UnifiedAIPlatform')
from voice.voice_config import voice_loader, build_voice_prompt_prefix, get_current_param


class UnifiedSessionManager:
    """Manages shared session state across all components."""
    
    def __init__(self, use_redis=False):
        self.use_redis = use_redis
        self.sessions = {}  # In-memory fallback
        
        if use_redis:
            try:
                self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
                self.redis_client.ping()
                print("✅ Redis connected for session management")
            except Exception as e:
                print(f"⚠️ Redis not available, using in-memory sessions: {e}")
                self.use_redis = False
    
    def get_session_id(self) -> str:
        """Get or create session ID."""
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        return session['session_id']
    
    def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Get session data."""
        if self.use_redis:
            try:
                data = self.redis_client.get(f"session:{session_id}")
                return json.loads(str(data)) if data else {}
            except Exception:
                pass
        
        return self.sessions.get(session_id, {})
    
    def set_session_data(self, session_id: str, data: Dict[str, Any]):
        """Set session data."""
        if self.use_redis:
            try:
                self.redis_client.setex(
                    f"session:{session_id}", 
                    3600,  # 1 hour TTL
                    json.dumps(data)
                )
                return
            except Exception:
                pass
        
        self.sessions[session_id] = data
    
    def update_session_data(self, session_id: str, updates: Dict[str, Any]):
        """Update session data."""
        data = self.get_session_data(session_id)
        data.update(updates)
        self.set_session_data(session_id, data)
    
    def get_voice_config(self, session_id: str) -> Dict[str, Any]:
        """Get voice configuration for session."""
        session_data = self.get_session_data(session_id)
        return session_data.get('voice_config', {})
    
    def set_voice_config(self, session_id: str, voice_config: Dict[str, Any]):
        """Set voice configuration for session."""
        self.update_session_data(session_id, {'voice_config': voice_config})
    
    def get_voice_prompt_prefix(self, session_id: str) -> str:
        """Get voice-aware prompt prefix for session."""
        voice_config = self.get_voice_config(session_id)
        return build_voice_prompt_prefix(voice_config if voice_config else None)


class UnifiedWebInterface:
    """Main unified web interface class."""
    
    def __init__(self):
        self.app = None
        self.search_system = None
        self.agent_manager = None
        self.analytics_integration = None
        self.session_manager = None
    
    def create_app(self, config_name: Optional[str] = None) -> Flask:
        """Create and configure the unified Flask application."""
        self.app = Flask(__name__, 
                        template_folder='/Users/cpconnor/projects/UnifiedAIPlatform/VectorDBRAG/templates',
                        static_folder='/Users/cpconnor/projects/UnifiedAIPlatform/VectorDBRAG/static')
        
        # Load configuration
        if config_name is None:
            config_name = os.getenv('FLASK_ENV', 'development')
        
        try:
            config = Config(config_name)
            config.validate()
            # Configure Flask
            self.app.config.update(config.to_dict())
        except Exception as e:
            # Fallback configuration
            logger.warning(f"Could not load config: {e}. Using fallback configuration.")
            self.app.config['DEBUG'] = True
        
        self.app.config['SECRET_KEY'] = os.urandom(24)
        self.app.config['SESSION_TYPE'] = 'filesystem'
        
        # Initialize session management
        Session(self.app)
        CORS(self.app)
        
        # Initialize session manager
        self.session_manager = UnifiedSessionManager()
        
        # Initialize core systems
        self._initialize_systems(config)
        
        # Register routes
        self._register_routes()
        
        # Register error handlers
        self._register_error_handlers()
        
        return self.app
    
    def _initialize_systems(self, config: Config):
        """Initialize all core systems."""
        try:
            # Initialize search system
            self.search_system = SearchSystem(config)
            self.app.search_system = self.search_system
            print("✅ Search system initialized")
            
            # Initialize analytics integration
            try:
                self.analytics_integration = AnalyticsIntegration(self.search_system, "Daily_Reporting")
                self.app.analytics_integration = self.analytics_integration
                print("✅ Analytics integration initialized")
            except Exception as e:
                print(f"⚠️ Analytics integration failed: {e}")
                self.analytics_integration = None
            
            # Initialize unified agent system
            try:
                self.agent_manager = UnifiedAgentManager(
                    rag_system=self.search_system,
                    analytics_integration=self.analytics_integration
                )
                self.app.agent_manager = self.agent_manager
                print("✅ Unified agent system initialized with 12 specialized agents")
            except Exception as e:
                print(f"⚠️ Agent system initialization failed: {e}")
                self.agent_manager = None
            
            # Initialize session manager
            self.app.session_manager = self.session_manager
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            raise
    
    def _register_routes(self):
        """Register all application routes."""
        
        @self.app.route('/')
        def index():
            """Main unified dashboard."""
            session_id = self.session_manager.get_session_id()
            session_data = self.session_manager.get_session_data(session_id)
            
            # Initialize session data if needed
            if not session_data:
                session_data = {
                    'created_at': datetime.now().isoformat(),
                    'agent_conversations': [],
                    'uploaded_documents': [],
                    'vector_stores': [],
                    'preferences': {
                        'default_agent': 'research',
                        'search_type': 'assisted',
                        'theme': 'light'
                    }
                }
                self.session_manager.set_session_data(session_id, session_data)
            
            return render_template('unified_dashboard.html', session_data=session_data)
        
        @self.app.route('/api/session/status')
        def session_status():
            """Get current session status."""
            session_id = self.session_manager.get_session_id()
            session_data = self.session_manager.get_session_data(session_id)
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'session_data': session_data,
                'systems_status': {
                    'search_system': self.search_system is not None,
                    'agent_manager': self.agent_manager is not None,
                    'analytics': self.analytics_integration is not None
                }
            })
        
        @self.app.route('/api/unified/chat', methods=['POST'])
        def unified_chat():
            """Unified chat interface that integrates agents and knowledge base."""
            try:
                data = request.get_json()
                message = data.get('message', '')
                agent_type = data.get('agent_type', 'research')
                use_knowledge_base = data.get('use_knowledge_base', True)
                vector_store_ids = data.get('vector_store_ids', [])
                
                session_id = self.session_manager.get_session_id()
                session_data = self.session_manager.get_session_data(session_id)
                
                if not message:
                    return jsonify({'error': 'Message is required'}), 400
                
                start_time = time.time()
                
                # Get knowledge base context if requested
                context = ""
                if use_knowledge_base and vector_store_ids and self.search_system:
                    try:
                        search_results = self.search_system.assisted_search(vector_store_ids, message)
                        if hasattr(search_results, 'content'):
                            context = f"\n\nKnowledge Base Context:\n{search_results.content}"
                        else:
                            context = f"\n\nKnowledge Base Context:\n{str(search_results)}"
                    except Exception as e:
                        print(f"Knowledge base search failed: {e}")
                
                # Create agent task
                if self.agent_manager:
                    enhanced_message = message + context
                    
                    # Map agent types
                    agent_mapping = {
                        'ceo': AgentType.CEO,
                        'research': AgentType.RESEARCH,
                        'performance': AgentType.PERFORMANCE,
                        'coaching': AgentType.COACHING,
                        'triage': AgentType.TRIAGE,
                        'code_analyzer': AgentType.CODE_ANALYZER,
                        'code_debugger': AgentType.CODE_DEBUGGER,
                        'code_repair': AgentType.CODE_REPAIR,
                        'test_generator': AgentType.TEST_GENERATOR,
                        'image': AgentType.IMAGE,
                        'audio': AgentType.AUDIO
                    }
                    
                    selected_agent_type = agent_mapping.get(agent_type, AgentType.RESEARCH)
                    
                    # Create and process task
                    task = AgentTask(
                        id=str(uuid.uuid4()),
                        content=enhanced_message,
                        agent_type=selected_agent_type,
                        complexity=TaskComplexity.MEDIUM,
                        context={'session_id': session_id, 'use_knowledge_base': use_knowledge_base}
                    )
                    
                    response = self.agent_manager.process_task(task)
                    
                    # Update session with conversation
                    conversation = {
                        'id': task.id,
                        'timestamp': datetime.now().isoformat(),
                        'user_message': message,
                        'agent_type': agent_type,
                        'agent_response': response.result,
                        'execution_time': response.execution_time,
                        'used_knowledge_base': bool(context),
                        'success': response.success
                    }
                    
                    if 'agent_conversations' not in session_data:
                        session_data['agent_conversations'] = []
                    session_data['agent_conversations'].append(conversation)
                    
                    # Keep only last 50 conversations
                    if len(session_data['agent_conversations']) > 50:
                        session_data['agent_conversations'] = session_data['agent_conversations'][-50:]
                    
                    self.session_manager.set_session_data(session_id, session_data)
                    
                    return jsonify({
                        'success': True,
                        'conversation_id': task.id,
                        'agent_type': agent_type,
                        'agent_name': response.agent_name,
                        'response': response.result,
                        'execution_time': response.execution_time,
                        'used_knowledge_base': bool(context),
                        'timestamp': conversation['timestamp']
                    })
                else:
                    return jsonify({
                        'error': 'Agent system not available',
                        'message': 'The agent system is not initialized.'
                    }), 503
                    
            except Exception as e:
                current_app.logger.error(f"Unified chat error: {str(e)}")
                return jsonify({
                    'error': 'Chat processing failed',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/unified/upload', methods=['POST'])
        def unified_upload():
            """Unified document upload with session tracking."""
            try:
                session_id = self.session_manager.get_session_id()
                session_data = self.session_manager.get_session_data(session_id)
                
                if 'file' not in request.files:
                    return jsonify({'error': 'No file provided'}), 400
                
                file = request.files['file']
                vector_store_id = request.form.get('vector_store_id')
                
                if not file.filename:
                    return jsonify({'error': 'No file selected'}), 400
                
                if not vector_store_id:
                    return jsonify({'error': 'Vector store ID required'}), 400
                
                # Upload to search system
                filename = secure_filename(file.filename)
                result = self.search_system.upload_file(file, vector_store_id)
                
                # Track in session
                upload_record = {
                    'id': str(uuid.uuid4()),
                    'filename': filename,
                    'vector_store_id': vector_store_id,
                    'timestamp': datetime.now().isoformat(),
                    'size': file.content_length or 0,
                    'status': 'uploaded'
                }
                
                if 'uploaded_documents' not in session_data:
                    session_data['uploaded_documents'] = []
                session_data['uploaded_documents'].append(upload_record)
                
                self.session_manager.set_session_data(session_id, session_data)
                
                return jsonify({
                    'success': True,
                    'message': 'File uploaded successfully',
                    'upload_id': upload_record['id'],
                    'filename': filename,
                    'result': result
                })
                
            except Exception as e:
                current_app.logger.error(f"Upload error: {str(e)}")
                return jsonify({
                    'error': 'Upload failed',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/unified/vector-stores', methods=['GET'])
        def get_vector_stores():
            """Get vector stores with session context."""
            try:
                stores = self.search_system.list_vector_stores()
                
                session_id = self.session_manager.get_session_id()
                session_data = self.session_manager.get_session_data(session_id)
                
                # Update session with current vector stores
                session_data['vector_stores'] = stores
                self.session_manager.set_session_data(session_id, session_data)
                
                return jsonify({
                    'success': True,
                    'vector_stores': stores
                })
                
            except Exception as e:
                current_app.logger.error(f"Vector stores error: {str(e)}")
                return jsonify({
                    'error': 'Failed to get vector stores',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/unified/preferences', methods=['POST'])
        def update_preferences():
            """Update user preferences in session."""
            try:
                data = request.get_json()
                session_id = self.session_manager.get_session_id()
                session_data = self.session_manager.get_session_data(session_id)
                
                if 'preferences' not in session_data:
                    session_data['preferences'] = {}
                
                session_data['preferences'].update(data)
                self.session_manager.set_session_data(session_id, session_data)
                
                return jsonify({
                    'success': True,
                    'preferences': session_data['preferences']
                })
                
            except Exception as e:
                return jsonify({
                    'error': 'Failed to update preferences',
                    'message': str(e)
                }), 500
        
        # TTS routes are handled by agent_flask_integration.py via _register_agent_routes()
        
        # Include existing routes from VectorDBRAG app
        self._register_legacy_routes()
        
        # Register comprehensive agent routes including TTS
        self._register_agent_routes()
    
    def _register_legacy_routes(self):
        """Register routes from the existing VectorDBRAG app for backward compatibility."""
        
        @self.app.route('/dashboard')
        def legacy_dashboard():
            """Legacy agent dashboard."""
            return render_template('agent_dashboard.html')
        
        @self.app.route('/analytics')
        def legacy_analytics():
            """Legacy analytics dashboard."""
            return render_template('analytics.html')
        
        @self.app.route('/health')
        def health_check():
            """System health check."""
            try:
                api_status = 'connected'
                if self.search_system:
                    self.search_system.client.models.list()
            except Exception as e:
                api_status = f'error: {str(e)}'
            
            return jsonify({
                'status': 'healthy' if api_status == 'connected' else 'degraded',
                'service': 'Unified Meld and RAG System',
                'version': '2.0.0',
                'components': {
                    'search_system': self.search_system is not None,
                    'agent_manager': self.agent_manager is not None,
                    'analytics': self.analytics_integration is not None,
                    'session_manager': self.session_manager is not None
                },
                'openai_api': api_status
            })
    
    def _register_error_handlers(self):
        """Register error handlers."""
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'error': 'Not found',
                'message': 'The requested resource was not found.'
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred.'
            }), 500
    
    def _register_agent_routes(self):
        """Register comprehensive agent routes including TTS from agent_flask_integration.py."""
        try:
            # Import and register agent routes from VectorDBRAG
            sys.path.append('/Users/cpconnor/projects/Meld and RAG/VectorDBRAG')
            from agent_flask_integration import register_agent_routes
            
            # Pass required systems to the app for agent routes
            self.app.search_system = self.search_system
            self.app.agent_manager = self.agent_manager
            self.app.analytics_integration = self.analytics_integration
            
            register_agent_routes(self.app)
            print("✅ Comprehensive agent routes registered (including TTS)")
            
            # Register voice configuration routes
            from voice.voice_routes import register_voice_routes
            register_voice_routes(self.app)
            print("✅ Voice configuration routes registered")
            
        except Exception as e:
            print(f"⚠️ Failed to register agent routes: {e}")
            # Continue without agent routes


def create_unified_app(config_name: Optional[str] = None) -> Flask:
    """Factory function to create the unified application."""
    interface = UnifiedWebInterface()
    return interface.create_app(config_name)


# Create app instance for imports and testing
app = create_unified_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)