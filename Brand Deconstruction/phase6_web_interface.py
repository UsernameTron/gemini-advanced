# Phase 6: Web Interface and API Integration
# File: web/app.py

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any
import logging
import os
from dataclasses import asdict

# Import our complete system
from core.base_agents import AgentManager
from workflows.brand_deconstruction import (
    CompleteBrandDeconstructionWorkflow, 
    BrandDeconstructionRequest,
    BrandDeconstructionResult
)
# Import enhanced visual pipeline
from integrations.enhanced_visual_pipeline import EnhancedVisualPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Enable CORS for API access

# Global system components
agent_manager = AgentManager()
deconstruction_workflow = CompleteBrandDeconstructionWorkflow(agent_manager)

# In-memory storage for results (replace with database in production)
results_cache = {}
execution_queue = {}

class BrandDeconstructionAPI:
    """
    RESTful API for the Brand Deconstruction Engine.
    
    This class provides clean API endpoints that expose our sophisticated
    analytical pipeline through simple HTTP requests. Users can submit URLs
    and receive complete satirical analysis without understanding the
    complex multi-agent orchestration happening underneath.
    """
    
    def __init__(self, app: Flask, workflow: CompleteBrandDeconstructionWorkflow):
        self.app = app
        self.workflow = workflow
        self.setup_routes()
    
    def setup_routes(self):
        """Configure all API endpoints"""
        
        # Core functionality endpoints
        self.app.route('/api/deconstruct', methods=['POST'])(self.deconstruct_brand)
        self.app.route('/api/batch-deconstruct', methods=['POST'])(self.batch_deconstruct)
        self.app.route('/api/results/<result_id>', methods=['GET'])(self.get_result)
        self.app.route('/api/status/<execution_id>', methods=['GET'])(self.get_execution_status)
        
        # System monitoring endpoints
        self.app.route('/api/health', methods=['GET'])(self.health_check)
        self.app.route('/api/performance', methods=['GET'])(self.get_performance_metrics)
        self.app.route('/api/history', methods=['GET'])(self.get_execution_history)
        
        # Utility endpoints
        self.app.route('/api/validate-url', methods=['POST'])(self.validate_url)
        self.app.route('/api/preview', methods=['POST'])(self.preview_analysis)
        
    async def deconstruct_brand(self):
        """
        Main endpoint for brand deconstruction.
        
        Accepts a URL and optional parameters, returns complete satirical analysis.
        This is the primary interface most users will interact with.
        """
        
        try:
            data = request.get_json()
            
            # Validate required parameters
            if not data or 'url' not in data:
                return jsonify({
                    'success': False,
                    'error': 'URL is required',
                    'error_code': 'MISSING_URL'
                }), 400
            
            # Create deconstruction request with validated parameters
            deconstruction_request = BrandDeconstructionRequest(
                url=data['url'],
                satirical_intensity=data.get('satirical_intensity', 'medium'),
                style_preference=data.get('style_preference', 'contradiction_expose'),
                output_variations=data.get('output_variations', 3),
                metadata={
                    'user_agent': request.headers.get('User-Agent', 'Unknown'),
                    'timestamp': datetime.now().isoformat(),
                    'request_id': str(uuid.uuid4())
                }
            )
            
            # Generate unique execution ID for tracking
            execution_id = str(uuid.uuid4())
            execution_queue[execution_id] = {
                'status': 'processing',
                'started_at': datetime.now().isoformat(),
                'request': asdict(deconstruction_request)
            }
            
            logger.info(f"Starting brand deconstruction: {deconstruction_request.url} (ID: {execution_id})")
            
            # Execute the complete workflow
            result = await self.workflow.execute_complete_deconstruction(deconstruction_request)
            
            # Store results for later retrieval
            result_id = str(uuid.uuid4())
            results_cache[result_id] = result
            
            # Update execution queue
            execution_queue[execution_id] = {
                'status': 'completed',
                'started_at': execution_queue[execution_id]['started_at'],
                'completed_at': datetime.now().isoformat(),
                'result_id': result_id
            }
            
            # Prepare response
            if result.execution_summary.get('success', True):
                response_data = {
                    'success': True,
                    'execution_id': execution_id,
                    'result_id': result_id,
                    'analysis_summary': {
                        'company_name': result.scraped_content.metadata.get('company_name') if result.scraped_content else 'Unknown',
                        'authenticity_score': result.brand_analysis.authenticity_score if result.brand_analysis else 0,
                        'vulnerabilities_found': len(result.brand_analysis.satirical_vulnerabilities) if result.brand_analysis else 0,
                        'prompts_generated': result.execution_summary.get('prompts_generated', 0)
                    },
                    'primary_prompt': result.primary_satirical_prompt.compile_full_prompt() if result.primary_satirical_prompt else None,
                    'execution_time': result.execution_summary.get('total_execution_time', 0)
                }
                
                logger.info(f"Brand deconstruction completed successfully: {execution_id}")
                return jsonify(response_data), 200
            else:
                error_response = {
                    'success': False,
                    'execution_id': execution_id,
                    'error': result.execution_summary.get('error_message', 'Unknown error'),
                    'failed_phase': result.execution_summary.get('failed_phase', 'unknown'),
                    'error_code': 'PROCESSING_FAILED'
                }
                
                logger.error(f"Brand deconstruction failed: {execution_id} - {error_response['error']}")
                return jsonify(error_response), 500
                
        except Exception as e:
            logger.error(f"API error in deconstruct_brand: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'error_code': 'INTERNAL_ERROR'
            }), 500
    
    async def batch_deconstruct(self):
        """
        Endpoint for batch processing multiple URLs.
        
        Useful for competitive analysis or systematic industry surveys.
        """
        
        try:
            data = request.get_json()
            
            if not data or 'urls' not in data or not isinstance(data['urls'], list):
                return jsonify({
                    'success': False,
                    'error': 'URLs array is required',
                    'error_code': 'MISSING_URLS'
                }), 400
            
            urls = data['urls']
            if len(urls) > 10:  # Reasonable limit
                return jsonify({
                    'success': False,
                    'error': 'Maximum 10 URLs allowed per batch',
                    'error_code': 'TOO_MANY_URLS'
                }), 400
            
            # Extract common parameters
            common_params = {
                'satirical_intensity': data.get('satirical_intensity', 'medium'),
                'style_preference': data.get('style_preference', 'contradiction_expose')
            }
            
            batch_id = str(uuid.uuid4())
            logger.info(f"Starting batch deconstruction: {len(urls)} URLs (Batch ID: {batch_id})")
            
            # Execute batch processing
            batch_results = await self.workflow.batch_process_urls(urls, common_params)
            
            # Process and store results
            processed_results = []
            for i, result in enumerate(batch_results):
                result_id = str(uuid.uuid4())
                results_cache[result_id] = result
                
                processed_results.append({
                    'url': urls[i],
                    'result_id': result_id,
                    'success': result.execution_summary.get('success', True),
                    'company_name': result.scraped_content.metadata.get('company_name') if result.scraped_content else 'Unknown',
                    'authenticity_score': result.brand_analysis.authenticity_score if result.brand_analysis else 0,
                    'execution_time': result.execution_summary.get('total_execution_time', 0)
                })
            
            response_data = {
                'success': True,
                'batch_id': batch_id,
                'results': processed_results,
                'summary': {
                    'total_processed': len(batch_results),
                    'successful': sum(1 for r in processed_results if r['success']),
                    'failed': sum(1 for r in processed_results if not r['success'])
                }
            }
            
            logger.info(f"Batch deconstruction completed: {batch_id}")
            return jsonify(response_data), 200
            
        except Exception as e:
            logger.error(f"API error in batch_deconstruct: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'error_code': 'INTERNAL_ERROR'
            }), 500
    
    def get_result(self, result_id: str):
        """
        Retrieve complete results for a specific analysis.
        
        Returns the full BrandDeconstructionResult with all analysis details.
        """
        
        if result_id not in results_cache:
            return jsonify({
                'success': False,
                'error': 'Result not found',
                'error_code': 'RESULT_NOT_FOUND'
            }), 404
        
        result = results_cache[result_id]
        
        # Convert result to dictionary for JSON response
        response_data = {
            'success': True,
            'result_id': result_id,
            'result': result.to_dict()
        }
        
        return jsonify(response_data), 200
    
    def get_execution_status(self, execution_id: str):
        """Check the status of a running or completed execution"""
        
        if execution_id not in execution_queue:
            return jsonify({
                'success': False,
                'error': 'Execution not found',
                'error_code': 'EXECUTION_NOT_FOUND'
            }), 404
        
        status_info = execution_queue[execution_id]
        return jsonify({
            'success': True,
            'execution_id': execution_id,
            'status': status_info
        }), 200
    
    def health_check(self):
        """System health check endpoint"""
        
        try:
            # Test basic system functionality
            performance = self.workflow.get_performance_summary()
            
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'system_info': {
                    'total_executions': performance['total_executions'],
                    'success_rate': performance['success_rate'],
                    'average_execution_time': performance['average_execution_time']
                },
                'cache_info': {
                    'results_cached': len(results_cache),
                    'executions_tracked': len(execution_queue)
                }
            }
            
            return jsonify(health_status), 200
            
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    def get_performance_metrics(self):
        """Get detailed system performance metrics"""
        
        performance = self.workflow.get_performance_summary()
        
        return jsonify({
            'success': True,
            'performance_metrics': performance,
            'cache_status': {
                'results_stored': len(results_cache),
                'executions_tracked': len(execution_queue)
            }
        }), 200
    
    def get_execution_history(self):
        """Get recent execution history"""
        
        # Get recent executions from workflow history
        recent_history = self.workflow.execution_history[-20:]  # Last 20 executions
        
        history_summary = []
        for result in recent_history:
            if hasattr(result, 'execution_summary'):
                history_summary.append({
                    'timestamp': result.processing_timestamp,
                    'url': result.request_params.url if result.request_params else 'Unknown',
                    'success': result.execution_summary.get('success', True),
                    'execution_time': result.execution_summary.get('total_execution_time', 0),
                    'company_name': result.scraped_content.metadata.get('company_name') if result.scraped_content else 'Unknown'
                })
        
        return jsonify({
            'success': True,
            'execution_history': history_summary,
            'total_executions': len(self.workflow.execution_history)
        }), 200
    
    def validate_url(self):
        """Validate a URL before processing"""
        
        try:
            data = request.get_json()
            url = data.get('url', '')
            
            # Basic URL validation
            if not url:
                return jsonify({
                    'valid': False,
                    'error': 'URL is required'
                }), 400
            
            # Check URL format
            if not (url.startswith('http://') or url.startswith('https://')):
                return jsonify({
                    'valid': False,
                    'error': 'URL must start with http:// or https://'
                }), 400
            
            # Additional validation could include checking if site is accessible
            return jsonify({
                'valid': True,
                'url': url
            }), 200
            
        except Exception as e:
            return jsonify({
                'valid': False,
                'error': str(e)
            }), 500
    
    def preview_analysis(self):
        """Quick preview of what content would be analyzed"""
        
        # This would implement a lightweight version of scraping
        # just to show what content sections are available
        return jsonify({
            'success': True,
            'message': 'Preview functionality would be implemented here'
        }), 200

# Initialize API
api = BrandDeconstructionAPI(app, deconstruction_workflow)

# Enhanced Visual Generation Endpoints using GPT-4o and Sora

@app.route('/api/enhanced-visuals', methods=['POST'])
async def enhanced_visual_generation():
    """
    API endpoint for GPT-4o enhanced visual concept generation.
    Creates sophisticated visual concepts and Sora-ready storyboards.
    """
    
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL is required',
                'error_code': 'MISSING_URL'
            }), 400
        
        url = data['url']
        visual_approaches = data.get('visual_approaches', ['satirical_visual_analysis', 'composite_design'])
        include_video = data.get('include_video', True)
        
        # Get OpenAI API key
        openai_api_key = data.get('openai_api_key') or os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            return jsonify({
                'success': False,
                'error': 'OpenAI API key is required',
                'error_code': 'MISSING_OPENAI_KEY'
            }), 400
        
        # Create enhanced pipeline
        enhanced_pipeline = EnhancedVisualPipeline(
            deconstruction_workflow=deconstruction_workflow,
            openai_api_key=openai_api_key,
            enable_sora=data.get('enable_sora', True)
        )
        
        # Execute enhanced pipeline
        result = await enhanced_pipeline.execute_enhanced_pipeline(
            url=url,
            visual_approaches=visual_approaches,
            include_video=include_video
        )
        
        if not result.success:
            return jsonify({
                'success': False,
                'error': result.error_message,
                'error_code': 'ENHANCED_PIPELINE_FAILED'
            }), 500
        
        # Format response
        response_data = {
            'success': True,
            'brand_analysis': {
                'brand_name': result.brand_deconstruction['brand_analysis']['brand_name'],
                'authenticity_score': result.brand_deconstruction['brand_analysis']['authenticity_score'],
                'satirical_vulnerabilities': result.brand_deconstruction['brand_analysis']['satirical_vulnerabilities']
            },
            'gpt4o_concepts': [
                {
                    'concept_id': i,
                    'success': concept.success,
                    'visual_concept': concept.visual_concept,
                    'detailed_instructions': concept.detailed_instructions,
                    'visual_elements': concept.visual_elements,
                    'satirical_approach': concept.satirical_approach,
                    'technical_specs': concept.technical_specs,
                    'sora_storyboard': concept.sora_storyboard,
                    'processing_time': concept.processing_time,
                    'error_message': concept.error_message
                }
                for i, concept in enumerate(result.gpt4o_concepts)
            ],
            'sora_videos': [
                {
                    'video_id': i,
                    'success': video.success,
                    'video_url': video.video_url,
                    'generation_metadata': video.generation_metadata,
                    'error_message': video.error_message
                }
                for i, video in enumerate(result.sora_videos)
            ],
            'pipeline_metadata': result.pipeline_metadata
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Enhanced visual generation API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Enhanced visual generation failed',
            'error_code': 'GPT4O_GENERATION_ERROR'
        }), 500

@app.route('/api/gpt4o-concepts', methods=['POST'])
async def gpt4o_concept_generation():
    """
    Dedicated endpoint for GPT-4o visual concept generation only.
    """
    
    try:
        data = request.get_json()
        
        if not data or 'brand_context' not in data:
            return jsonify({
                'success': False,
                'error': 'Brand context is required',
                'error_code': 'MISSING_BRAND_CONTEXT'
            }), 400
        
        # Get OpenAI API key
        openai_api_key = data.get('openai_api_key') or os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            return jsonify({
                'success': False,
                'error': 'OpenAI API key is required',
                'error_code': 'MISSING_OPENAI_KEY'
            }), 400
        
        # Import here to avoid circular imports
        from integrations.gpt4o_visual_client import GPT4oVisualClient, GPT4oVisualRequest
        
        # Create GPT-4o client
        gpt4o_client = GPT4oVisualClient(api_key=openai_api_key)
        
        # Create request
        concept_request = GPT4oVisualRequest(
            pentagram_prompt=data.get('pentagram_prompt', ''),
            brand_context=data['brand_context'],
            analysis_mode=data.get('analysis_mode', 'satirical_visual_analysis'),
            visual_style=data.get('visual_style', 'professional_satirical')
        )
        
        # Generate concept
        concept_result = await gpt4o_client.analyze_and_conceptualize(concept_request)
        
        # Format response
        response_data = {
            'success': concept_result.success,
            'visual_concept': concept_result.visual_concept,
            'detailed_instructions': concept_result.detailed_instructions,
            'visual_elements': concept_result.visual_elements,
            'satirical_approach': concept_result.satirical_approach,
            'technical_specs': concept_result.technical_specs,
            'sora_storyboard': concept_result.sora_storyboard,
            'processing_time': concept_result.processing_time,
            'error_message': concept_result.error_message
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"GPT-4o concept generation API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'GPT-4o concept generation failed',
            'error_code': 'GPT4O_CONCEPT_ERROR'
        }), 500

@app.route('/api/sora-storyboard', methods=['POST'])
async def sora_storyboard_generation():
    """
    Dedicated endpoint for Sora storyboard preparation.
    """
    
    try:
        data = request.get_json()
        
        if not data or 'brand_context' not in data:
            return jsonify({
                'success': False,
                'error': 'Brand context is required',
                'error_code': 'MISSING_BRAND_CONTEXT'
            }), 400
        
        # Get OpenAI API key
        openai_api_key = data.get('openai_api_key') or os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            return jsonify({
                'success': False,
                'error': 'OpenAI API key is required',
                'error_code': 'MISSING_OPENAI_KEY'
            }), 400
        
        # Import clients
        from integrations.gpt4o_visual_client import GPT4oVisualClient, GPT4oVisualRequest
        from integrations.sora_client import SoraClient, SoraGenerationRequest
        
        # Create clients
        gpt4o_client = GPT4oVisualClient(api_key=openai_api_key)
        sora_client = SoraClient(api_key=openai_api_key)
        
        # Create storyboard request
        storyboard_request = GPT4oVisualRequest(
            pentagram_prompt=data.get('pentagram_prompt', ''),
            brand_context=data['brand_context'],
            analysis_mode='sora_storyboard',
            visual_style=data.get('visual_style', 'professional_satirical')
        )
        
        # Generate storyboard with GPT-4o
        storyboard_result = await gpt4o_client.analyze_and_conceptualize(storyboard_request)
        
        # If storyboard was successful and Sora is available, attempt video generation
        sora_result = None
        if storyboard_result.success and storyboard_result.sora_storyboard:
            sora_request = SoraGenerationRequest(
                storyboard=storyboard_result.sora_storyboard,
                video_concept=storyboard_result.visual_concept or "Satirical brand critique video",
                duration=data.get('duration', 15),
                style=data.get('style', 'professional_satirical')
            )
            
            sora_result = await sora_client.generate_satirical_video(sora_request)
        
        # Format response
        response_data = {
            'success': storyboard_result.success,
            'storyboard': {
                'visual_concept': storyboard_result.visual_concept,
                'detailed_instructions': storyboard_result.detailed_instructions,
                'scenes': storyboard_result.sora_storyboard,
                'processing_time': storyboard_result.processing_time,
                'error_message': storyboard_result.error_message
            },
            'sora_generation': {
                'attempted': sora_result is not None,
                'success': sora_result.success if sora_result else False,
                'video_url': sora_result.video_url if sora_result else None,
                'metadata': sora_result.generation_metadata if sora_result else {},
                'error_message': sora_result.error_message if sora_result else None
            } if sora_result else None
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Sora storyboard generation API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Sora storyboard generation failed',
            'error_code': 'SORA_STORYBOARD_ERROR'
        }), 500

@app.route('/api/pure-8k-concepts', methods=['POST'])
async def pure_8k_concept_development():
    """
    API endpoint for pure GPT-4o 8K concept development.
    Creates comprehensive visual concepts, technical specs, and implementation guides.
    No image generation - pure conceptual development.
    """
    
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL is required',
                'error_code': 'MISSING_URL'
            }), 400
        
        url = data['url']
        analysis_modes = data.get('analysis_modes', [
            '8k_concept_development',
            'technical_specifications', 
            'creative_direction',
            'implementation_guide'
        ])
        include_alternatives = data.get('include_alternatives', True)
        
        # Get OpenAI API key
        openai_api_key = data.get('openai_api_key') or os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            return jsonify({
                'success': False,
                'error': 'OpenAI API key is required',
                'error_code': 'MISSING_OPENAI_KEY'
            }), 400
        
        # Create pure 8K concept pipeline
        from integrations.pure_8k_concept_pipeline import Pure8KConceptPipeline
        
        concept_pipeline = Pure8KConceptPipeline(
            deconstruction_workflow=deconstruction_workflow,
            openai_api_key=openai_api_key
        )
        
        # Execute pure concept pipeline
        result = await concept_pipeline.execute_concept_pipeline(
            url=url,
            analysis_modes=analysis_modes,
            include_alternatives=include_alternatives
        )
        
        if not result.success:
            return jsonify({
                'success': False,
                'error': result.error_message,
                'error_code': 'PURE_8K_PIPELINE_FAILED'
            }), 500
        
        # Export portfolio for comprehensive results
        portfolio_export = await concept_pipeline.export_concept_portfolio(result)
        
        # Format response
        response_data = {
            'success': True,
            'brand_analysis': {
                'brand_name': result.brand_deconstruction.brand_analysis.brand_name,
                'authenticity_score': result.brand_deconstruction.brand_analysis.authenticity_score,
                'satirical_vulnerabilities': result.brand_deconstruction.brand_analysis.satirical_vulnerabilities,
                'primary_positioning': result.brand_deconstruction.brand_analysis.primary_positioning
            },
            'concept_developments': [
                {
                    'concept_id': i,
                    'title': concept.concept_title,
                    'core_concept': concept.visual_concept,
                    'detailed_breakdown': concept.detailed_breakdown,
                    'satirical_strategy': concept.satirical_strategy,
                    'alternative_concepts': concept.alternative_concepts,
                    'quality_benchmarks': concept.quality_benchmarks,
                    'processing_time': concept.processing_time,
                    'success': concept.success,
                    'error_message': concept.error_message
                }
                for i, concept in enumerate(result.concept_developments)
            ],
            'technical_specifications': [
                {
                    'spec_id': i,
                    'overview': spec.visual_concept,
                    'detailed_specs': spec.technical_specifications,
                    'implementation_notes': spec.detailed_breakdown,
                    'processing_time': spec.processing_time,
                    'success': spec.success
                }
                for i, spec in enumerate(result.technical_specifications)
            ],
            'creative_directions': [
                {
                    'direction_id': i,
                    'creative_vision': direction.visual_concept,
                    'artistic_guidance': direction.creative_direction,
                    'satirical_approach': direction.satirical_strategy,
                    'processing_time': direction.processing_time,
                    'success': direction.success
                }
                for i, direction in enumerate(result.creative_directions)
            ],
            'implementation_guides': [
                {
                    'guide_id': i,
                    'overview': guide.visual_concept,
                    'step_by_step': guide.implementation_steps,
                    'technical_setup': guide.technical_specifications,
                    'quality_assurance': guide.quality_benchmarks,
                    'processing_time': guide.processing_time,
                    'success': guide.success
                }
                for i, guide in enumerate(result.implementation_guides)
            ],
            'portfolio': portfolio_export.get('portfolio') if portfolio_export['success'] else None,
            'pipeline_metadata': result.pipeline_metadata
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Pure 8K concept development API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Pure 8K concept development failed',
            'error_code': 'PURE_8K_CONCEPT_ERROR'
        }), 500

@app.route('/api/export-portfolio/<result_id>', methods=['GET'])
async def export_concept_portfolio(result_id: str):
    """
    Export a complete concept development portfolio as downloadable file.
    """
    
    try:
        # This endpoint would retrieve a stored result and export it
        # For now, return format information
        
        return jsonify({
            'success': True,
            'message': 'Portfolio export endpoint ready',
            'formats_available': [
                'json',
                'pdf_report', 
                'markdown',
                'creative_brief'
            ],
            'note': 'Implementation depends on stored result availability'
        }), 200
        
    except Exception as e:
        logger.error(f"Portfolio export error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Portfolio export failed',
            'error_code': 'PORTFOLIO_EXPORT_ERROR'
        }), 500

# File: web/templates/index.html

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brand Deconstruction Engine</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .main-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #555;
        }
        
        input[type="url"], select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input[type="url"]:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .controls-row {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
        }
        
        .analyze-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
            width: 100%;
            margin-top: 20px;
        }
        
        .analyze-btn:hover {
            transform: translateY(-2px);
        }
        
        .analyze-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        
        .loading.active {
            display: block;
        }
        
        .results {
            display: none;
            margin-top: 30px;
        }
        
        .results.active {
            display: block;
        }
        
        .result-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .result-section h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .prompt-box {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            font-family: monospace;
            white-space: pre-wrap;
            line-height: 1.4;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .metric-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .metric-label {
            color: #666;
            margin-top: 5px;
        }
        
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #c33;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Brand Deconstruction Engine</h1>
            <p>Precision satirical analysis of corporate messaging</p>
        </div>
        
        <div class="main-card">
            <form id="analysisForm">
                <div class="form-group">
                    <label for="url">Target URL</label>
                    <input type="url" id="url" name="url" placeholder="https://example-company.com" required>
                </div>
                
                <div class="controls-row">
                    <div class="form-group">
                        <label for="intensity">Satirical Intensity</label>
                        <select id="intensity" name="intensity">
                            <option value="low">Low - Subtle Critique</option>
                            <option value="medium" selected>Medium - Balanced Approach</option>
                            <option value="high">High - Sharp Satirical Edge</option>
                            <option value="extreme">Extreme - Ruthless Deconstruction</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="style">Analysis Style</label>
                        <select id="style" name="style">
                            <option value="contradiction_expose" selected>Contradiction Exposure</option>
                            <option value="buzzword_deflation">Buzzword Deflation</option>
                            <option value="aspiration_mockery">Aspiration Gap Analysis</option>
                            <option value="authority_undermining">Authority Undermining</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="variations">Prompt Variations</label>
                        <select id="variations" name="variations">
                            <option value="1">1 Variation</option>
                            <option value="3" selected>3 Variations</option>
                            <option value="5">5 Variations</option>
                        </select>
                    </div>
                </div>
                
                <button type="submit" class="analyze-btn" id="analyzeBtn">
                    🔍 Deconstruct Brand
                </button>
            </form>
            
            <div class="loading" id="loading">
                <p>🧠 Analyzing brand psychology...</p>
                <p><small>This may take 30-60 seconds</small></p>
            </div>
            
            <div class="error" id="error" style="display: none;"></div>
        </div>
        
        <div class="results" id="results">
            <div class="result-section">
                <h3>📊 Analysis Overview</h3>
                <div class="metrics-grid" id="metricsGrid">
                    <!-- Metrics will be populated by JavaScript -->
                </div>
            </div>
            
            <div class="result-section">
                <h3>🎯 Primary Satirical Prompt</h3>
                <div class="prompt-box" id="primaryPrompt">
                    <!-- Primary prompt will be populated by JavaScript -->
                </div>
            </div>
            
            <div class="result-section" id="alternativePrompts">
                <h3>🔄 Alternative Variations</h3>
                <!-- Alternative prompts will be populated by JavaScript -->
            </div>
        </div>
    </div>
    
    <script>
        // Brand Deconstruction Engine Frontend
        class BrandDeconstructionUI {
            constructor() {
                this.form = document.getElementById('analysisForm');
                this.loading = document.getElementById('loading');
                this.results = document.getElementById('results');
                this.error = document.getElementById('error');
                this.analyzeBtn = document.getElementById('analyzeBtn');
                
                this.setupEventListeners();
            }
            
            setupEventListeners() {
                this.form.addEventListener('submit', (e) => this.handleSubmit(e));
            }
            
            async handleSubmit(event) {
                event.preventDefault();
                
                const formData = new FormData(this.form);
                const requestData = {
                    url: formData.get('url'),
                    satirical_intensity: formData.get('intensity'),
                    style_preference: formData.get('style'),
                    output_variations: parseInt(formData.get('variations'))
                };
                
                this.showLoading();
                this.hideError();
                this.hideResults();
                
                try {
                    const response = await fetch('/api/deconstruct', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(requestData)
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        await this.displayResults(result);
                    } else {
                        this.showError(result.error || 'Analysis failed');
                    }
                    
                } catch (error) {
                    this.showError('Network error: ' + error.message);
                } finally {
                    this.hideLoading();
                }
            }
            
            async displayResults(result) {
                // Display metrics
                this.displayMetrics(result.analysis_summary);
                
                // Display primary prompt
                document.getElementById('primaryPrompt').textContent = result.primary_prompt;
                
                // Get full results for alternatives
                if (result.result_id) {
                    try {
                        const fullResultResponse = await fetch(`/api/results/${result.result_id}`);
                        const fullResult = await fullResultResponse.json();
                        
                        if (fullResult.success && fullResult.result.alternative_prompts) {
                            this.displayAlternativePrompts(fullResult.result.alternative_prompts);
                        }
                    } catch (error) {
                        console.error('Failed to load alternative prompts:', error);
                    }
                }
                
                this.showResults();
            }
            
            displayMetrics(summary) {
                const metricsGrid = document.getElementById('metricsGrid');
                metricsGrid.innerHTML = `
                    <div class="metric-card">
                        <div class="metric-value">${summary.company_name}</div>
                        <div class="metric-label">Company</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${summary.authenticity_score.toFixed(2)}</div>
                        <div class="metric-label">Authenticity Score</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${summary.vulnerabilities_found}</div>
                        <div class="metric-label">Vulnerabilities</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${summary.prompts_generated}</div>
                        <div class="metric-label">Prompts Generated</div>
                    </div>
                `;
            }
            
            displayAlternativePrompts(alternatives) {
                const container = document.getElementById('alternativePrompts');
                let html = '<h3>🔄 Alternative Variations</h3>';
                
                alternatives.forEach((prompt, index) => {
                    html += `
                        <div class="prompt-box" style="margin-bottom: 15px;">
                            <strong>Variation ${index + 1}:</strong><br>
                            ${prompt.intent_clarity}. ${prompt.fidelity_pass}. ${prompt.symbolic_anchoring}. ${prompt.environmental_context}. ${prompt.brand_world_constraints}
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            }
            
            showLoading() {
                this.loading.classList.add('active');
                this.analyzeBtn.disabled = true;
                this.analyzeBtn.textContent = '🧠 Analyzing...';
            }
            
            hideLoading() {
                this.loading.classList.remove('active');
                this.analyzeBtn.disabled = false;
                this.analyzeBtn.textContent = '🔍 Deconstruct Brand';
            }
            
            showResults() {
                this.results.classList.add('active');
            }
            
            hideResults() {
                this.results.classList.remove('active');
            }
            
            showError(message) {
                this.error.textContent = message;
                this.error.style.display = 'block';
            }
            
            hideError() {
                this.error.style.display = 'none';
            }
        }
        
        // Initialize the UI when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            new BrandDeconstructionUI();
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Serve the main web interface"""
    return HTML_TEMPLATE

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

# File: web/run_server.py

import asyncio
from threading import Thread
import uvloop

def run_flask_app():
    """Run the Flask application"""
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )

def setup_async_loop():
    """Setup the async event loop for background processing"""
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()

if __name__ == '__main__':
    # Start async loop in background thread
    async_thread = Thread(target=setup_async_loop, daemon=True)
    async_thread.start()
    
    print("🚀 Brand Deconstruction Engine Starting...")
    print("📡 API available at: http://localhost:5000/api/")
    print("🌐 Web interface at: http://localhost:5000/")
    print("📊 Health check at: http://localhost:5000/api/health")
    
    # Start Flask application
    run_flask_app()

# File: examples/test_api.py

import asyncio
import aiohttp
import json

async def test_api_endpoints():
    """
    Test all API endpoints to ensure they're working correctly.
    This demonstrates how to interact with the API programmatically.
    """
    
    base_url = 'http://localhost:5000/api'
    
    async with aiohttp.ClientSession() as session:
        # Test health check
        print("🏥 Testing health check...")
        async with session.get(f'{base_url}/health') as response:
            health_data = await response.json()
            print(f"   Status: {health_data['status']}")
        
        # Test URL validation
        print("🔍 Testing URL validation...")
        validation_data = {'url': 'https://www.salesforce.com'}
        async with session.post(f'{base_url}/validate-url', 
                              json=validation_data) as response:
            validation_result = await response.json()
            print(f"   Valid: {validation_result['valid']}")
        
        # Test brand deconstruction
        print("🎯 Testing brand deconstruction...")
        deconstruction_data = {
            'url': 'https://www.hubspot.com',
            'satirical_intensity': 'medium',
            'style_preference': 'contradiction_expose'
        }
        
        async with session.post(f'{base_url}/deconstruct', 
                              json=deconstruction_data) as response:
            if response.status == 200:
                result = await response.json()
                if result['success']:
                    print(f"   ✅ Analysis completed in {result['execution_time']:.2f}s")
                    print(f"   Company: {result['analysis_summary']['company_name']}")
                    print(f"   Authenticity: {result['analysis_summary']['authenticity_score']:.2f}")
                else:
                    print(f"   ❌ Analysis failed: {result['error']}")
            else:
                print(f"   ❌ HTTP {response.status}")
        
        # Test performance metrics
        print("📊 Testing performance metrics...")
        async with session.get(f'{base_url}/performance') as response:
            performance_data = await response.json();
            metrics = performance_data['performance_metrics'];
            print(f"   Total executions: {metrics['total_executions']}");
            print(f"   Success rate: {metrics['success_rate']}");

if __name__ == "__main__":
    print("🧪 Testing Brand Deconstruction API")
    print("📝 Make sure the server is running on localhost:5000")
    print("=" * 50)
    
    asyncio.run(test_api_endpoints())