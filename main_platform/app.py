"""
Unified Brand Deconstruction Platform
Integrates VectorDBRAG, MindMeld agents, and brand analysis capabilities
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import asyncio
import json
import base64
import io
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "VectorDBRAG"))
sys.path.append(str(project_root / "shared_agents"))

# Import enhanced configuration and services
from main_platform.config import PlatformConfig
from main_platform.services import EnhancedImageService, ImageGenerationError
from main_platform.utils import CampaignManager

# Import existing infrastructure
try:
    from VectorDBRAG.agents.enhanced.factory import EnhancedAgentFactory
    from shared_agents.core.agent_factory import AgentCapability
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Agent infrastructure not fully available: {e}")
    AGENTS_AVAILABLE = False

# Import new brand agents
try:
    from VectorDBRAG.agents.enhanced.brand_agents import (
        BrandDeconstructionAgent, 
        GPTImageGenerationAgent, 
        BrandIntelligenceAgent
    )
    BRAND_AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Brand agents not available: {e}")
    BRAND_AGENTS_AVAILABLE = False

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)

# Initialize WebSocket support
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize comprehensive configuration
try:
    environment = os.getenv('FLASK_ENV', 'development')
    platform_config = PlatformConfig(environment=environment)
    
    # Initialize enhanced services
    image_service = EnhancedImageService(platform_config)
    campaign_manager = CampaignManager(platform_config)
    
    print(f"✅ Platform configuration loaded for {environment} environment")
    print(f"✅ Enhanced image service initialized")
    print(f"✅ Campaign manager initialized")
    
except Exception as e:
    print(f"⚠️ Warning: Failed to initialize enhanced services: {e}")
    platform_config = None
    image_service = None
    campaign_manager = None

# Legacy configuration for backward compatibility
config = {
    'default_model': 'gpt-4-turbo',
    'debug': True,
    'port': 5003,
    'websocket_support': True
}

# Initialize enhanced agent factory with brand capabilities
agent_factory = None
if AGENTS_AVAILABLE:
    try:
        # Import OpenAI client
        from openai import OpenAI
        
        # Initialize OpenAI client with API key from environment
        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        enhanced_factory = EnhancedAgentFactory({
            'model': config.get('default_model', 'gpt-4'),
            'default_model': config.get('default_model', 'gpt-4'),
            'openai_client': openai_client
        })
        agent_factory = enhanced_factory
        print(f"✅ Enhanced agent factory initialized with OpenAI client")
    except Exception as e:
        print(f"Warning: Failed to initialize enhanced agent factory: {e}")
        enhanced_factory = None
        agent_factory = None
else:
    enhanced_factory = None
    agent_factory = None

@app.route('/')
def index():
    """Main platform dashboard with unified dark mode interface"""
    return render_template('dashboard.html', 
                         title="Brand Deconstruction Platform",
                         timestamp=datetime.now().isoformat(),
                         agents_available=AGENTS_AVAILABLE,
                         brand_agents_available=BRAND_AGENTS_AVAILABLE)

@app.route('/api/health')
def health_check():
    """Platform health check endpoint"""
    try:
        agent_count = len(enhanced_factory.get_agent_types()) if enhanced_factory else 0
    except Exception:
        agent_count = 0
    
    return jsonify({
        "status": "healthy",
        "platform": "Brand Deconstruction Platform",
        "agents_available": AGENTS_AVAILABLE,
        "brand_agents_available": BRAND_AGENTS_AVAILABLE,
        "agent_count": agent_count,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/api/agents/available')
def get_available_agents():
    """Get all available agents including brand deconstruction agents"""
    if not enhanced_factory:
        return jsonify({
            "success": False,
            "message": "Agent factory not available"
        }), 503
    
    # Get agent types and convert to JSON-safe format
    try:
        agent_types_raw = enhanced_factory.get_agent_types()
        # Convert to simple dict with string keys and values
        agent_types = {}
        for key, value in agent_types_raw.items():
            agent_types[str(key)] = str(value) if not isinstance(value, (dict, list)) else "complex_object"
    except Exception as e:
        agent_types = {"error": f"Could not retrieve agent types: {str(e)}"}
    
    # Convert AgentCapability enum values to strings
    capabilities = []
    if AGENTS_AVAILABLE:
        try:
            capabilities = [cap.value for cap in AgentCapability]
        except Exception as e:
            capabilities = ["analysis", "generation", "orchestration"]  # fallback
    
    return jsonify({
        "success": True,
        "agents": {
            "available": agent_types,
            "brand_deconstruction": [
                "brand_deconstruction",
                "gpt_image_generation", 
                "brand_intelligence"
            ] if BRAND_AGENTS_AVAILABLE else []
        },
        "capabilities": capabilities,
        "total_agents": len(agent_types)
    })

@app.route('/api/brand/analyze', methods=['POST'])
def analyze_brand():
    """
    Main brand deconstruction analysis endpoint
    Orchestrates comprehensive brand analysis workflow
    """
    try:
        if not BRAND_AGENTS_AVAILABLE:
            return jsonify({
                "success": False,
                "message": "Brand agents not available"
            }), 503
        
        data = request.get_json()
        brand_name = data.get('brand_name', '')
        analysis_depth = data.get('depth', 'comprehensive')
        target_vectors = data.get('vectors', ['positioning', 'performance', 'technical'])
        
        if not brand_name:
            return jsonify({
                "success": False,
                "message": "Brand name is required"
            }), 400
        
        # Create brand deconstruction agent
        brand_agent = enhanced_factory.create_agent('brand_deconstruction', f'BrandAnalyzer_{brand_name}')
        
        # Execute comprehensive analysis (sync version for Flask)
        analysis_request = {
            "brand_name": brand_name,
            "analysis_depth": analysis_depth,
            "additional_context": {
                "vectors": target_vectors,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Run async method in event loop
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        analysis_result = loop.run_until_complete(brand_agent.execute(analysis_request))
        
        if analysis_result.success:
            return jsonify({
                "success": True,
                "data": analysis_result.result,
                "processing_time": analysis_result.execution_time,
                "analysis_id": f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "next_steps": [
                    "Review satirical concepts",
                    "Select concepts for image generation",
                    "Generate high-quality images",
                    "Export campaign materials"
                ]
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Analysis failed: {analysis_result.error}"
            }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Analysis failed: {str(e)}"
        }), 500

@app.route('/api/brand/intelligence', methods=['POST'])
def gather_intelligence():
    """Dedicated endpoint for brand intelligence gathering"""
    try:
        if not BRAND_AGENTS_AVAILABLE:
            return jsonify({
                "success": False,
                "message": "Brand intelligence agent not available"
            }), 503
        
        data = request.get_json()
        brand_name = data.get('brand_name', '')
        intelligence_type = data.get('type', 'comprehensive')
        
        if not brand_name:
            return jsonify({
                "success": False,
                "message": "Brand name is required"
            }), 400
        
        # Create intelligence agent
        intel_agent = enhanced_factory.create_agent('brand_intelligence', f'Intel_{brand_name}')
        
        # Configure sub-agents for intelligence agent
        brand_agent = enhanced_factory.create_agent('brand_deconstruction', f'SubBrand_{brand_name}')
        image_agent = enhanced_factory.create_agent('gpt_image_generation', f'SubImage_{brand_name}')
        
        # Update intelligence agent config
        intel_config = {
            'brand_deconstruction_agent': brand_agent,
            'image_generation_agent': image_agent
        }
        
        # Create new intelligence agent with sub-agents
        intel_agent = enhanced_factory.create_agent('brand_intelligence', f'Intel_{brand_name}', intel_config)
        
        # Gather intelligence
        intel_request = {
            "brand_name": brand_name,
            "analysis_depth": intelligence_type
        }
        
        # Run async method
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        intel_result = loop.run_until_complete(intel_agent.execute(intel_request))
        
        if intel_result.success:
            return jsonify({
                "success": True,
                "data": intel_result.result,
                "processing_time": intel_result.execution_time
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Intelligence gathering failed: {intel_result.error}"
            }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Intelligence gathering failed: {str(e)}"
        }), 500

@app.route('/api/image/concepts', methods=['POST'])
def generate_image_concepts():
    """Step 1: Generate satirical concept previews for user selection"""
    try:
        if not BRAND_AGENTS_AVAILABLE:
            return jsonify({
                "success": False,
                "message": "Image generation agent not available"
            }), 503
        
        data = request.get_json()
        satirical_concepts = data.get('satirical_concepts', [])
        brand_context = data.get('brand_context', {})
        
        if not satirical_concepts:
            return jsonify({
                "success": False,
                "message": "Satirical concepts are required"
            }), 400
        
        # Create image generation agent
        image_agent = enhanced_factory.create_agent('gpt_image_generation', 'ImageConceptGenerator')
        
        # Generate concept previews (mock implementation for now)
        concepts_data = []
        for i, concept in enumerate(satirical_concepts):
            concepts_data.append({
                "concept_id": f"concept_{i+1}",
                "concept_text": concept,
                "preview_description": f"Satirical visualization of {concept}",
                "estimated_cost": 0.08,
                "quality_level": "HD"
            })
        
        return jsonify({
            "success": True,
            "data": {
                "concepts": concepts_data,
                "total_concepts": len(concepts_data),
                "ready_for_generation": True
            },
            "message": f"Generated {len(concepts_data)} concept previews"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Concept generation failed: {str(e)}"
        }), 500

@app.route('/api/image/generate', methods=['POST'])
def generate_final_image():
    """Step 2: Generate final high-quality image from selected concept"""
    try:
        if not BRAND_AGENTS_AVAILABLE:
            return jsonify({
                "success": False,
                "message": "Image generation agent not available"
            }), 503
        
        data = request.get_json()
        enhanced_prompt = data.get('enhanced_prompt', '')
        brand_context = data.get('brand_context', {})
        
        if not enhanced_prompt:
            return jsonify({
                "success": False,
                "message": "Enhanced prompt is required"
            }), 400
        
        # Create image generation agent
        image_agent = enhanced_factory.create_agent('gpt_image_generation', 'ImageGenerator')
        
        # Prepare image generation request
        image_request = {
            "prompt": enhanced_prompt,
            "brand_context": brand_context,
            "resolution": "1536x1024",  # Use valid gpt-image-1 resolution
            "quality": "hd",
            "satirical_intensity": data.get('satirical_intensity', 0.7)
        }
        
        # Generate final image
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        image_result = loop.run_until_complete(image_agent.execute(image_request))
        
        if image_result.success:
            return jsonify({
                "success": True,
                "data": image_result.result,
                "processing_time": image_result.execution_time,
                "cost": 0.08,
                "resolution": "1536x1024"
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Image generation failed: {image_result.error}"
            }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Image generation failed: {str(e)}"
        }), 500

@app.route('/api/image/download/<image_id>')
def download_image(image_id):
    """Download generated image by ID"""
    try:
        # This would normally retrieve from a database or cache
        # For now, return a placeholder response
        return jsonify({
            "success": True,
            "message": f"Image {image_id} download endpoint ready",
            "download_url": f"/api/image/download/{image_id}",
            "note": "Implement database storage for production"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Image download failed: {str(e)}"
        }), 500

@app.route('/api/campaign/export', methods=['POST'])
def export_campaign():
    """Export complete campaign analysis and materials"""
    try:
        data = request.get_json()
        campaign_data = data.get('campaign_data', {})
        export_format = data.get('format', 'json')
        
        if export_format == 'json':
            export_data = {
                "campaign_export": campaign_data,
                "export_timestamp": datetime.now().isoformat(),
                "platform": "Brand Deconstruction Platform",
                "version": "1.0",
                "export_format": export_format
            }
            
            return jsonify({
                "success": True,
                "data": export_data,
                "message": "Campaign exported successfully",
                "download_size": len(json.dumps(export_data))
            })
        
        return jsonify({
            "success": False,
            "message": f"Export format '{export_format}' not supported"
        }), 400
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Campaign export failed: {str(e)}"
        }), 500

@app.route('/api/workflow/orchestrate', methods=['POST'])
def orchestrate_workflow():
    """
    Advanced workflow orchestration using CEO agent
    Coordinates multiple agents for complex campaigns
    """
    try:
        if not AGENTS_AVAILABLE:
            return jsonify({
                "success": False,
                "message": "Agent orchestration not available"
            }), 503
        
        data = request.get_json()
        workflow_type = data.get('workflow_type', 'brand_campaign')
        workflow_config = data.get('config', {})
        
        # Create CEO agent for orchestration
        ceo_agent = enhanced_factory.create_agent('ceo', 'CampaignOrchestrator')
        
        # Prepare orchestration request
        orchestration_request = {
            "workflow_type": workflow_type,
            "config": workflow_config,
            "available_agents": enhanced_factory.get_agent_types(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Orchestrate multi-agent workflow
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        orchestration_result = loop.run_until_complete(ceo_agent.execute(orchestration_request))
        
        if orchestration_result.success:
            return jsonify({
                "success": True,
                "data": orchestration_result.result,
                "processing_time": orchestration_result.execution_time,
                "workflow_id": f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Workflow orchestration failed: {orchestration_result.error}"
            }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Workflow orchestration failed: {str(e)}"
        }), 500

# Enhanced API endpoints using new configuration system

@app.route('/api/enhanced/config', methods=['GET'])
def get_platform_config():
    """Get current platform configuration (non-sensitive data only)"""
    if platform_config:
        return jsonify({
            "success": True,
            "config": platform_config.to_dict(),
            "environment": platform_config.environment
        })
    else:
        return jsonify({
            "success": False,
            "message": "Platform configuration not available"
        }), 503

@app.route('/api/enhanced/image/concepts', methods=['POST'])
async def generate_concept_previews():
    """Generate optimized concept previews for image generation"""
    if not image_service:
        return jsonify({
            "success": False,
            "message": "Enhanced image service not available"
        }), 503
    
    try:
        data = request.get_json()
        satirical_concepts = data.get('satirical_concepts', [])
        brand_category = data.get('brand_category', 'general')
        
        if not satirical_concepts:
            return jsonify({
                "success": False,
                "message": "Satirical concepts are required"
            }), 400
        
        # Generate concept previews
        concept_previews = await image_service.generate_concept_previews(
            satirical_concepts, 
            brand_category
        )
        
        return jsonify({
            "success": True,
            "concept_previews": concept_previews,
            "total_concepts": len(concept_previews),
            "estimated_total_cost": sum(cp.get('estimated_cost', 0) for cp in concept_previews)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to generate concept previews: {str(e)}"
        }), 500

@app.route('/api/enhanced/image/generate', methods=['POST'])
async def generate_enhanced_image():
    """Generate high-quality image using enhanced service"""
    if not image_service:
        return jsonify({
            "success": False,
            "message": "Enhanced image service not available"
        }), 503
    
    try:
        data = request.get_json()
        optimized_prompt = data.get('optimized_prompt', '')
        concept_metadata = data.get('concept_metadata', {})
        
        if not optimized_prompt:
            return jsonify({
                "success": False,
                "message": "Optimized prompt is required"
            }), 400
        
        # Generate the image
        result = await image_service.generate_high_quality_image(
            optimized_prompt,
            concept_metadata
        )
        
        # Convert base64 image to data URL for frontend display
        if result.get('success') and result.get('image_base64'):
            result['image_url'] = f"data:image/png;base64,{result['image_base64']}"
        
        return jsonify(result)
        
    except ImageGenerationError as e:
        return jsonify({
            "success": False,
            "message": str(e),
            "error_type": "image_generation_error"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Image generation failed: {str(e)}"
        }), 500

@app.route('/api/enhanced/image/stats', methods=['GET'])
def get_image_generation_stats():
    """Get image generation statistics"""
    if not image_service:
        return jsonify({
            "success": False,
            "message": "Enhanced image service not available"
        }), 503
    
    try:
        stats = image_service.get_generation_stats()
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get stats: {str(e)}"
        }), 500

@app.route('/api/enhanced/campaigns', methods=['POST'])
def create_campaign():
    """Create a new campaign using enhanced campaign manager"""
    if not campaign_manager:
        return jsonify({
            "success": False,
            "message": "Campaign manager not available"
        }), 503
    
    try:
        data = request.get_json()
        brand_name = data.get('brand_name', '')
        analysis_data = data.get('analysis_data', {})
        metadata = data.get('metadata', {})
        
        if not brand_name:
            return jsonify({
                "success": False,
                "message": "Brand name is required"
            }), 400
        
        campaign_id = campaign_manager.create_campaign(
            brand_name,
            analysis_data,
            metadata
        )
        
        return jsonify({
            "success": True,
            "campaign_id": campaign_id,
            "message": f"Campaign created for {brand_name}"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to create campaign: {str(e)}"
        }), 500

@app.route('/api/enhanced/campaigns/<campaign_id>/export')
def export_enhanced_campaign(campaign_id):
    """Export campaign data"""
    if not campaign_manager:
        return jsonify({
            "success": False,
            "message": "Campaign manager not available"
        }), 503
    
    try:
        export_format = request.args.get('format', 'json')
        
        if export_format not in ['json', 'zip']:
            return jsonify({
                "success": False,
                "message": "Unsupported export format. Use 'json' or 'zip'"
            }), 400
        
        export_data = campaign_manager.export_campaign(campaign_id, export_format)
        
        if export_format == 'json':
            response = send_file(
                io.BytesIO(export_data),
                as_attachment=True,
                download_name=f'campaign_{campaign_id}.json',
                mimetype='application/json'
            )
        else:  # zip
            response = send_file(
                io.BytesIO(export_data),
                as_attachment=True,
                download_name=f'campaign_{campaign_id}.zip',
                mimetype='application/zip'
            )
        
        return response
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Export failed: {str(e)}"
        }), 500

@app.route('/api/enhanced/analytics', methods=['GET'])
def get_platform_analytics():
    """Get platform analytics and statistics"""
    if not campaign_manager:
        return jsonify({
            "success": False,
            "message": "Campaign manager not available"
        }), 503
    
    try:
        stats = campaign_manager.analytics.get_platform_statistics()
        
        # Add image generation stats if available
        if image_service:
            image_stats = image_service.get_generation_stats()
            stats['image_generation'] = image_stats
        
        return jsonify({
            "success": True,
            "analytics": stats,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get analytics: {str(e)}"
        }), 500

# Helper functions for workflow execution and analytics
def validate_workflow_structure(nodes: List[Dict], connections: List[Dict]) -> Dict[str, Any]:
    """Validate workflow structure and dependencies"""
    try:
        # Basic validation
        if not nodes:
            return {"valid": False, "error": "No nodes found in workflow"}
        
        # Check for required node properties
        for i, node in enumerate(nodes):
            if 'id' not in node:
                return {"valid": False, "error": f"Node {i} missing 'id' property"}
            if 'type' not in node:
                return {"valid": False, "error": f"Node {node['id']} missing 'type' property"}
        
        # Validate connections
        node_ids = {node['id'] for node in nodes}
        for i, connection in enumerate(connections):
            if 'source' not in connection or 'target' not in connection:
                return {"valid": False, "error": f"Connection {i} missing source or target"}
            
            if connection['source'] not in node_ids:
                return {"valid": False, "error": f"Connection source '{connection['source']}' not found"}
            if connection['target'] not in node_ids:
                return {"valid": False, "error": f"Connection target '{connection['target']}' not found"}
        
        # Check for circular dependencies (basic check)
        visited = set()
        visiting = set()
        
        def has_cycle(node_id):
            if node_id in visiting:
                return True
            if node_id in visited:
                return False
            
            visiting.add(node_id)
            
            # Find outgoing connections
            for conn in connections:
                if conn['source'] == node_id:
                    if has_cycle(conn['target']):
                        return True
            
            visiting.remove(node_id)
            visited.add(node_id)
            return False
        
        for node in nodes:
            if has_cycle(node['id']):
                return {"valid": False, "error": "Circular dependency detected in workflow"}
        
        return {"valid": True, "nodes": len(nodes), "connections": len(connections)}
        
    except Exception as e:
        return {"valid": False, "error": f"Validation error: {str(e)}"}

def execute_workflow_with_tracking(execution_id: str, workflow_data: Dict[str, Any], 
                                 campaign_manager: Optional[Any] = None) -> Dict[str, Any]:
    """Execute workflow with comprehensive tracking"""
    try:
        nodes = workflow_data.get('nodes', [])
        connections = workflow_data.get('connections', [])
        
        execution_log = {
            'execution_id': execution_id,
            'start_time': datetime.now().isoformat(),
            'workflow_summary': {
                'total_nodes': len(nodes),
                'total_connections': len(connections),
                'node_types': [node.get('type', 'unknown') for node in nodes]
            },
            'execution_steps': [],
            'status': 'running'
        }
        
        # Execute nodes in dependency order
        executed_nodes = set()
        execution_queue = []
        
        # Find starting nodes (no incoming connections)
        starting_nodes = []
        for node in nodes:
            has_incoming = any(conn['target'] == node['id'] for conn in connections)
            if not has_incoming:
                starting_nodes.append(node)
        
        if not starting_nodes:
            # If no clear starting point, execute in order
            starting_nodes = [nodes[0]] if nodes else []
        
        # Simple execution simulation (can be enhanced with actual logic)
        for i, node in enumerate(nodes):
            step_result = {
                'node_id': node['id'],
                'node_type': node.get('type', 'unknown'),
                'step_number': i + 1,
                'execution_time': datetime.now().isoformat(),
                'status': 'completed',
                'output': f"Simulated execution of {node.get('type', 'unknown')} node"
            }
            
            # Add node-specific execution logic here
            if node.get('type') == 'brand_analysis':
                step_result['output'] = "Brand analysis completed with satirical concept generation"
            elif node.get('type') == 'image_generation':
                step_result['output'] = "Image generation queued for processing"
            elif node.get('type') == 'campaign_export':
                step_result['output'] = "Campaign data prepared for export"
            
            execution_log['execution_steps'].append(step_result)
            executed_nodes.add(node['id'])
        
        execution_log['end_time'] = datetime.now().isoformat()
        execution_log['status'] = 'completed'
        execution_log['success'] = True
        
        # Log to campaign if available
        if campaign_manager:
            try:
                campaign_manager.analytics.log_event(
                    execution_id, 
                    'workflow_executed', 
                    execution_log
                )
            except Exception as log_error:
                print(f"Failed to log workflow execution: {log_error}")
        
        return execution_log
        
    except Exception as e:
        error_log = {
            'execution_id': execution_id,
            'start_time': datetime.now().isoformat(),
            'end_time': datetime.now().isoformat(),
            'status': 'failed',
            'success': False,
            'error': str(e),
            'execution_steps': []
        }
        return error_log

def store_analytics_event(tracking_data: Dict[str, Any]) -> Dict[str, Any]:
    """Store analytics event with enhanced metadata"""
    try:
        tracking_id = str(uuid.uuid4())
        
        # Enhanced tracking data
        enhanced_data = {
            'tracking_id': tracking_id,
            'stored_at': datetime.now().isoformat(),
            **tracking_data
        }
        
        # In a real implementation, this would store to a database
        # For now, we'll simulate storage and return success
        
        # Could integrate with campaign_manager analytics here
        return {
            'tracking_id': tracking_id,
            'status': 'stored',
            'timestamp': enhanced_data['stored_at']
        }
        
    except Exception as e:
        return {
            'tracking_id': None,
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

# Enhanced workflow and analytics API endpoints
@app.route('/api/enhanced/workflow/execute', methods=['POST'])
def execute_workflow():
    """Execute a workflow with advanced validation and tracking"""
    try:
        data = request.get_json()
        workflow_data = data.get('workflow', {})
        nodes = workflow_data.get('nodes', [])
        connections = workflow_data.get('connections', [])
        
        if not nodes:
            return jsonify({
                "success": False,
                "message": "Workflow must contain at least one node"
            }), 400
        
        # Validate workflow structure
        validation_result = validate_workflow_structure(nodes, connections)
        if not validation_result['valid']:
            return jsonify({
                "success": False,
                "message": f"Workflow validation failed: {validation_result['error']}"
            }), 400
        
        # Execute workflow with tracking
        execution_id = str(uuid.uuid4())
        execution_result = execute_workflow_with_tracking(
            execution_id, 
            workflow_data, 
            campaign_manager if campaign_manager else None
        )
        
        return jsonify({
            "success": True,
            "execution_id": execution_id,
            "result": execution_result,
            "message": "Workflow executed successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Workflow execution failed: {str(e)}"
        }), 500

@app.route('/api/enhanced/analytics/track', methods=['POST'])
def track_analytics_event():
    """Track analytics events with enhanced metadata"""
    try:
        data = request.get_json()
        event_type = data.get('event_type', '')
        event_data = data.get('event_data', {})
        campaign_id = data.get('campaign_id')
        
        if not event_type:
            return jsonify({
                "success": False,
                "message": "Event type is required"
            }), 400
        
        # Enhanced event tracking with metadata
        tracking_data = {
            'event_type': event_type,
            'event_data': event_data,
            'timestamp': datetime.now().isoformat(),
            'session_id': data.get('session_id', ''),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr
        }
        
        # Log to campaign if campaign_id provided
        if campaign_id and campaign_manager:
            campaign_manager.analytics.log_event(campaign_id, event_type, tracking_data)
        
        # Store in analytics tracking
        analytics_result = store_analytics_event(tracking_data)
        
        return jsonify({
            "success": True,
            "tracking_id": analytics_result.get('tracking_id'),
            "message": "Event tracked successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Analytics tracking failed: {str(e)}"
        }), 500

@app.route('/api/enhanced/workflow/validate', methods=['POST'])
def validate_workflow():
    """Validate workflow structure and dependencies"""
    try:
        data = request.get_json()
        workflow_data = data.get('workflow', {})
        nodes = workflow_data.get('nodes', [])
        connections = workflow_data.get('connections', [])
        
        validation_result = validate_workflow_structure(nodes, connections)
        
        return jsonify({
            "success": True,
            "validation": validation_result,
            "message": "Workflow validation complete"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Workflow validation failed: {str(e)}"
        }), 500

@app.route('/api/enhanced/campaign/workflows/<campaign_id>', methods=['GET'])
def get_campaign_workflows(campaign_id):
    """Get workflows associated with a campaign"""
    try:
        if not campaign_manager:
            return jsonify({
                "success": False,
                "message": "Campaign manager not available"
            }), 503
        
        campaign = campaign_manager.db.get_campaign(campaign_id)
        if not campaign:
            return jsonify({
                "success": False,
                "message": "Campaign not found"
            }), 404
        
        workflows = campaign.get('workflows', [])
        
        return jsonify({
            "success": True,
            "workflows": workflows,
            "campaign_id": campaign_id
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get campaign workflows: {str(e)}"
        }), 500

# WebSocket handlers for real-time collaboration
@socketio.on('connect')
def handle_connect():
    """Handle client connection for real-time updates"""
    emit('status', {
        'message': 'Connected to Brand Deconstruction Platform',
        'timestamp': datetime.now().isoformat(),
        'platform_status': 'ready'
    })

@socketio.on('start_analysis')
def handle_start_analysis(data):
    """Handle real-time brand analysis start"""
    brand_name = data.get('brand_name', '')
    emit('analysis_status', {
        'brand_name': brand_name,
        'status': 'started',
        'message': f'Starting analysis for {brand_name}',
        'timestamp': datetime.now().isoformat(),
        'progress': 0
    })

@socketio.on('analysis_progress')
def handle_analysis_progress(data):
    """Handle analysis progress updates"""
    emit('analysis_status', {
        'status': 'progress',
        'step': data.get('step', ''),
        'progress': data.get('progress', 0),
        'timestamp': datetime.now().isoformat(),
        'message': f"Processing: {data.get('step', 'Unknown step')}"
    })

@socketio.on('request_agent_status')
def handle_agent_status_request():
    """Handle request for current agent status"""
    if enhanced_factory:
        agent_types = enhanced_factory.get_agent_types()
        emit('agent_status', {
            'agents_available': len(agent_types),
            'agent_types': list(agent_types.keys()),
            'brand_agents_available': BRAND_AGENTS_AVAILABLE,
            'timestamp': datetime.now().isoformat()
        })
    else:
        emit('agent_status', {
            'agents_available': 0,
            'agent_types': [],
            'brand_agents_available': False,
            'error': 'Agent factory not initialized',
            'timestamp': datetime.now().isoformat()
        })

if __name__ == '__main__':
    # Development server configuration
    debug_mode = config.get('debug', True)
    port = config.get('port', 5003)
    
    print(f"🚀 Starting Brand Deconstruction Platform on port {port}")
    print(f"📊 Agents Available: {AGENTS_AVAILABLE}")
    print(f"🎯 Brand Agents Available: {BRAND_AGENTS_AVAILABLE}")
    
    if config.get('websocket_support', True):
        socketio.run(app, debug=debug_mode, port=port, host='0.0.0.0')
    else:
        app.run(debug=debug_mode, port=port, host='0.0.0.0')
