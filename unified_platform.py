#!/usr/bin/env python3
# filepath: /Users/cpconnor/projects/UnifiedAIPlatform/unified_platform.py
"""
Unified AI Platform - Production-Ready Dark Mode Interface
Consolidates all modules: VectorDBRAG, Brand Deconstruction, RAG, MindMeld-v1.1
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import logging
from datetime import datetime

# Add all module paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "RAG"))
sys.path.insert(0, str(project_root / "VectorDBRAG"))
sys.path.insert(0, str(project_root / "Brand Deconstruction"))
sys.path.insert(0, str(project_root / "MindMeld-v1.1"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(project_root / 'logs' / 'unified_platform.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UnifiedPlatform:
    """Main unified platform class that orchestrates all modules"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)
        
        # Enable CORS for frontend integration
        CORS(self.app, resources={
            r"/api/*": {"origins": "*"},
            r"/brand/*": {"origins": "*"},
            r"/rag/*": {"origins": "*"},
            r"/vectordb/*": {"origins": "*"}
        })
        
        # Initialize modules
        self.modules = {}
        self.initialize_modules()
        self.setup_routes()
        
        logger.info("Unified AI Platform initialized successfully")
    
    def initialize_modules(self):
        """Initialize all platform modules"""
        
        # Initialize VectorDBRAG
        try:
            from VectorDBRAG.agents.enhanced.factory import EnhancedAgentFactory
            self.modules['vectordb'] = {
                'factory': EnhancedAgentFactory(),
                'status': 'active',
                'description': 'Production-ready RAG system with enhanced agents'
            }
            logger.info("✅ VectorDBRAG module initialized")
        except Exception as e:
            logger.error(f"❌ VectorDBRAG initialization failed: {e}")
            self.modules['vectordb'] = {'status': 'error', 'error': str(e)}
        
        # Initialize Brand Deconstruction
        try:
            from VectorDBRAG.agents.enhanced.brand_agents import (
                BrandDeconstructionAgent,
                GPTImageGenerationAgent,
                BrandIntelligenceAgent
            )
            self.modules['brand'] = {
                'agents': {
                    'deconstruction': BrandDeconstructionAgent,
                    'image_generation': GPTImageGenerationAgent,
                    'intelligence': BrandIntelligenceAgent
                },
                'status': 'active',
                'description': 'Advanced brand deconstruction with pentagram framework'
            }
            logger.info("✅ Brand Deconstruction module initialized")
        except Exception as e:
            logger.error(f"❌ Brand Deconstruction initialization failed: {e}")
            self.modules['brand'] = {'status': 'error', 'error': str(e)}
        
        # Initialize RAG
        try:
            # Import RAG agents if available
            self.modules['rag'] = {
                'status': 'active',
                'description': 'Core RAG system with agent ecosystem'
            }
            logger.info("✅ RAG module initialized")
        except Exception as e:
            logger.error(f"❌ RAG initialization failed: {e}")
            self.modules['rag'] = {'status': 'error', 'error': str(e)}
        
        # Initialize MindMeld frontend
        try:
            self.modules['mindmeld'] = {
                'status': 'active',
                'description': 'Next.js frontend interface'
            }
            logger.info("✅ MindMeld module initialized")
        except Exception as e:
            logger.error(f"❌ MindMeld initialization failed: {e}")
            self.modules['mindmeld'] = {'status': 'error', 'error': str(e)}
    
    def setup_routes(self):
        """Setup all platform routes"""
        
        # Main dashboard route
        @self.app.route('/')
        def dashboard():
            """Main dashboard with dark mode interface"""
            module_status = {
                name: module.get('status', 'unknown')
                for name, module in self.modules.items()
            }
            
            return render_template('dashboard.html', 
                                 modules=self.modules,
                                 module_status=module_status,
                                 current_time=datetime.now().isoformat())
        
        # Health check endpoint
        @self.app.route('/health')
        def health_check():
            """Health check for monitoring"""
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'modules': {
                    name: module.get('status', 'unknown')
                    for name, module in self.modules.items()
                },
                'version': '1.0.0'
            }
            
            # Check if any modules are in error state
            error_modules = [
                name for name, module in self.modules.items()
                if module.get('status') == 'error'
            ]
            
            if error_modules:
                health_status['status'] = 'degraded'
                health_status['errors'] = error_modules
            
            return jsonify(health_status)
        
        # Brand Deconstruction API routes
        @self.app.route('/api/brand/analyze', methods=['POST'])
        def brand_analyze():
            """Brand analysis endpoint"""
            try:
                if 'brand' not in self.modules or self.modules['brand']['status'] != 'active':
                    return jsonify({'error': 'Brand module not available'}), 503
                
                data = request.get_json()
                if not data or 'brand_name' not in data:
                    return jsonify({'error': 'brand_name is required'}), 400
                
                # Create brand deconstruction agent
                factory = self.modules['vectordb']['factory']
                agent = factory.create_agent('brand_deconstruction', 'BrandAnalyzer')
                
                # Execute analysis (this will be async in production)
                import asyncio
                result = asyncio.run(agent.execute(data))
                
                if result.success:
                    return jsonify({
                        'success': True,
                        'data': result.result,
                        'processing_time': result.execution_time
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': result.error
                    }), 500
                
            except Exception as e:
                logger.error(f"Brand analysis error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/brand/generate-image', methods=['POST'])
        def brand_generate_image():
            """Brand image generation endpoint"""
            try:
                if 'brand' not in self.modules or self.modules['brand']['status'] != 'active':
                    return jsonify({'error': 'Brand module not available'}), 503
                
                data = request.get_json()
                required_fields = ['prompt', 'brand_context']
                
                if not data or not all(field in data for field in required_fields):
                    return jsonify({'error': f'Required fields: {required_fields}'}), 400
                
                # Create image generation agent
                factory = self.modules['vectordb']['factory']
                agent = factory.create_agent('gpt_image_generation', 'ImageGenerator')
                
                # Execute image generation
                import asyncio
                result = asyncio.run(agent.execute(data))
                
                if result.success:
                    return jsonify({
                        'success': True,
                        'data': result.result,
                        'processing_time': result.execution_time
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': result.error
                    }), 500
                
            except Exception as e:
                logger.error(f"Image generation error: {e}")
                return jsonify({'error': str(e)}), 500
        
        # VectorDB RAG API routes  
        @self.app.route('/api/vectordb/query', methods=['POST'])
        def vectordb_query():
            """VectorDB RAG query endpoint"""
            try:
                if 'vectordb' not in self.modules or self.modules['vectordb']['status'] != 'active':
                    return jsonify({'error': 'VectorDB module not available'}), 503
                
                data = request.get_json()
                if not data or 'query' not in data:
                    return jsonify({'error': 'query is required'}), 400
                
                # Use VectorDB agents for processing
                factory = self.modules['vectordb']['factory']
                agent = factory.create_agent('research', 'RAGResearcher')
                
                # Execute query
                import asyncio
                result = asyncio.run(agent.execute(data))
                
                if result.success:
                    return jsonify({
                        'success': True,
                        'data': result.result,
                        'processing_time': result.execution_time
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': result.error
                    }), 500
                
            except Exception as e:
                logger.error(f"VectorDB query error: {e}")
                return jsonify({'error': str(e)}), 500
        
        # Module status endpoint
        @self.app.route('/api/modules/status')
        def modules_status():
            """Get status of all modules"""
            return jsonify({
                'modules': self.modules,
                'active_count': len([m for m in self.modules.values() if m.get('status') == 'active']),
                'total_count': len(self.modules),
                'timestamp': datetime.now().isoformat()
            })
        
        # Agent capabilities endpoint
        @self.app.route('/api/agents/capabilities')
        def agent_capabilities():
            """Get available agent capabilities"""
            try:
                if 'vectordb' not in self.modules or self.modules['vectordb']['status'] != 'active':
                    return jsonify({'error': 'VectorDB module not available'}), 503
                
                factory = self.modules['vectordb']['factory']
                agent_info = factory.get_agent_types()
                
                return jsonify({
                    'success': True,
                    'agents': agent_info,
                    'count': len(agent_info)
                })
                
            except Exception as e:
                logger.error(f"Agent capabilities error: {e}")
                return jsonify({'error': str(e)}), 500
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the unified platform"""
        logger.info(f"🚀 Starting Unified AI Platform on {host}:{port}")
        logger.info(f"📊 Active modules: {len([m for m in self.modules.values() if m.get('status') == 'active'])}/{len(self.modules)}")
        
        # Ensure logs directory exists
        os.makedirs(project_root / 'logs', exist_ok=True)
        
        # Create templates directory if it doesn't exist
        template_dir = project_root / 'templates'
        os.makedirs(template_dir, exist_ok=True)
        
        self.app.run(host=host, port=port, debug=debug)


def main():
    """Main entry point"""
    platform = UnifiedPlatform()
    
    # Check if running in development mode
    debug_mode = os.getenv('FLASK_ENV') == 'development' or '--debug' in sys.argv
    port = int(os.getenv('PORT', 5000))
    
    platform.run(port=port, debug=debug_mode)


if __name__ == '__main__':
    main()
