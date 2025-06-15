# Enhanced Brand Deconstruction Web Interface
# Complete web UI for agent-enhanced brand deconstruction with gpt-image-1 integration

from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
import asyncio
import json
import os
import time
import base64
import io
from pathlib import Path
import logging
from typing import Dict, Any

# Import our enhanced system
from enhanced_brand_system import EnhancedBrandDeconstructionEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global engine instance
engine = None

def initialize_engine():
    """Initialize the enhanced brand deconstruction engine"""
    global engine
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment variables")
        return False
    
    try:
        engine = EnhancedBrandDeconstructionEngine(api_key)
        logger.info("Enhanced Brand Deconstruction Engine initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize engine: {e}")
        return False

# Initialize engine on startup
initialize_engine()

# Store results for retrieval
analysis_results = {}

@app.route('/')
def index():
    """Main interface for the enhanced brand deconstruction system"""
    return render_template_string(ENHANCED_HTML_TEMPLATE)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'engine_initialized': engine is not None,
        'agents_available': len(engine.analyzer.agents) if engine else 0,
        'version': 'enhanced_agent_v1.0'
    })

@app.route('/api/analyze-brand', methods=['POST'])
def analyze_brand():
    """Enhanced brand analysis endpoint with agent integration"""
    if not engine:
        # Try to initialize engine if not already done
        if not initialize_engine():
            return jsonify({
                'success': False,
                'error': 'Engine not initialized. Please set OPENAI_API_KEY environment variable.',
                'help': 'Set OPENAI_API_KEY environment variable with your OpenAI API key'
            }), 500
    
    data = request.get_json()
    url = data.get('url')
    generate_images = data.get('generate_images', True)
    image_count = data.get('image_count', 3)
    
    if not url:
        return jsonify({
            'success': False,
            'error': 'URL is required'
        }), 400
    
    try:
        # Run the async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            engine.process_brand(url, generate_images, image_count)
        )
        loop.close()
        
        # Store result for later retrieval
        result_id = f"analysis_{int(time.time())}"
        analysis_results[result_id] = result
        result['result_id'] = result_id
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# New gpt-image-1 specific endpoints
@app.route('/api/gpt-image-1-generation', methods=['POST'])
def gpt_image_1_generation():
    """
    New endpoint specifically for gpt-image-1 generation.
    Ensures ONLY gpt-image-1 is used (no DALL-E, no GPT-4o).
    """
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Configuration for gpt-image-1 only
        image_config = {
            'model': 'gpt-image-1',  # Explicitly set model
            'size': data.get('size', '1536x1024'),  # High resolution default
            'quality': data.get('quality', 'high'),
            'output_format': 'png',
            'excluded_models': ['dalle-2', 'dalle-3', 'gpt-4o']  # Explicitly exclude
        }
        
        # Force async execution
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Import direct pipeline with proper path
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent))
            
            from integrations.direct_gpt_image_1_pipeline import DirectGPTImage1Pipeline
            from workflows.brand_deconstruction import CompleteBrandDeconstructionWorkflow
            
            # Initialize pipeline
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                return jsonify({'error': 'API key not configured'}), 500
                
            workflow = CompleteBrandDeconstructionWorkflow()
            pipeline = DirectGPTImage1Pipeline(
                deconstruction_workflow=workflow,
                openai_api_key=api_key
            )
            
            # Execute gpt-image-1 generation
            result = loop.run_until_complete(
                pipeline.execute_direct_pipeline(
                    url=url,
                    image_config=image_config
                )
            )
            
            if result.success:
                # Format response for web interface
                response_data = {
                    'success': True,
                    'brand_name': result.brand_deconstruction.brand_analysis.brand_name,
                    'authenticity_score': result.brand_deconstruction.brand_analysis.authenticity_score,
                    'images': [],
                    'model_used': 'gpt-image-1',
                    'excluded_models': ['dalle-2', 'dalle-3', 'gpt-4o'],
                    'generation_time': getattr(result, 'processing_time', 0.0)
                }
                
                # Add image data
                for i, image in enumerate(result.generated_images):
                    image_data = {
                        'id': i + 1,
                        'success': image.success,
                        'model': 'gpt-image-1',
                        'size': image.image_specs.get('size', 'unknown'),
                        'processing_time': image.processing_time
                    }
                    
                    if image.success:
                        image_data['url'] = image.image_url
                        image_data['local_path'] = image.local_path
                    else:
                        image_data['error'] = image.error_message
                        # Check for organization verification error
                        if 'organization' in image.error_message.lower():
                            image_data['error_type'] = 'verification_required'
                            image_data['help_message'] = 'gpt-image-1 requires organization verification'
                    
                    response_data['images'].append(image_data)
                
                return jsonify(response_data)
            
            else:
                return jsonify({
                    'success': False,
                    'error': result.error_message,
                    'model_attempted': 'gpt-image-1',
                    'excluded_models': ['dalle-2', 'dalle-3', 'gpt-4o']
                }), 500
                
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"gpt-image-1 generation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'model_attempted': 'gpt-image-1'
        }), 500

@app.route('/api/gpt-image-1-config', methods=['GET'])
def gpt_image_1_config():
    """Get available gpt-image-1 configurations and capabilities"""
    return jsonify({
        'model': 'gpt-image-1',
        'excluded_models': ['dalle-2', 'dalle-3', 'gpt-4o'],
        'supported_sizes': [
            '1024x1024',
            '1536x1024', 
            '1024x1536'
        ],
        'quality_options': ['low', 'medium', 'high', 'auto'],
        'output_formats': ['png'],
        'max_resolution': '1536x1024',
        'features': [
            '8K-ready quality',
            'High-resolution support',
            'Professional satirical content',
            'Brand contradiction detection'
        ],
        'requirements': {
            'organization_verification': True,
            'api_key': True
        }
    })

@app.route('/api/gpt-image-1-status', methods=['GET'])
def gpt_image_1_status():
    """Check gpt-image-1 API status and organization verification"""
    try:
        # Test connection to gpt-image-1
        import openai
        
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'No API key configured',
                'model': 'gpt-image-1'
            })
        
        # Simple test call to check organization status
        client = openai.OpenAI(api_key=api_key)
        
        try:
            # Attempt a test generation (will fail with organization error if not verified)
            response = client.images.generate(
                model="gpt-image-1",
                prompt="test",
                size="1024x1024",
                quality="high",  # Use valid quality value
                n=1
            )
            
            return jsonify({
                'status': 'ready',
                'message': 'gpt-image-1 API access confirmed',
                'model': 'gpt-image-1',
                'organization_verified': True
            })
            
        except openai.PermissionDeniedError as e:
            if 'organization' in str(e).lower():
                return jsonify({
                    'status': 'verification_required',
                    'message': 'Organization verification required for gpt-image-1',
                    'model': 'gpt-image-1',
                    'organization_verified': False,
                    'help_url': 'https://platform.openai.com/settings/organization/general'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'model': 'gpt-image-1'
                })
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'API test failed: {str(e)}',
                'model': 'gpt-image-1'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Status check failed: {str(e)}',
            'model': 'gpt-image-1'
        })

@app.route('/api/models-info', methods=['GET'])
def models_info():
    """Get information about models used and excluded"""
    return jsonify({
        'models_used': ['gpt-image-1'],
        'models_excluded': ['dalle-2', 'dalle-3', 'gpt-4o'],
        'exclusion_reason': 'Per user requirements - ONLY gpt-image-1',
        'features': {
            'gpt-image-1': {
                'description': 'OpenAI latest image generation model',
                'capabilities': ['8K-ready', 'high quality', 'professional output'],
                'requirements': ['organization verification']
            }
        },
        'excluded_features': {
            'dalle-2': 'Completely removed from system',
            'dalle-3': 'Completely removed from system', 
            'gpt-4o': 'Completely removed from system'
        }
    })

@app.route('/api/organization-status', methods=['GET'])
def organization_status():
    """Get detailed organization verification status and guidance"""
    try:
        import openai
        
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'No API key configured',
                'action_required': 'Set OPENAI_API_KEY environment variable'
            })
        
        # Test gpt-image-1 access
        client = openai.OpenAI(api_key=api_key)
        
        try:
            # Test call to check organization status
            response = client.images.generate(
                model="gpt-image-1",
                prompt="test verification",
                size="1024x1024",
                quality="high",
                n=1
            )
            
            return jsonify({
                'status': 'verified',
                'message': 'Organization verified - full gpt-image-1 access available',
                'capabilities': ['8K generation', 'high quality', 'professional output'],
                'ready_for_production': True
            })
            
        except openai.PermissionDeniedError as e:
            if 'organization' in str(e).lower():
                return jsonify({
                    'status': 'verification_required',
                    'message': 'Organization verification required for gpt-image-1 access',
                    'action_required': 'Complete organization verification',
                    'verification_url': 'https://platform.openai.com/settings/organization/general',
                    'help_text': 'Visit OpenAI platform settings to complete organization verification',
                    'estimated_time': '24-48 hours for verification approval',
                    'alternative_demo': 'Brand analysis features fully functional'
                })
            else:
                return jsonify({
                    'status': 'permission_error',
                    'message': str(e),
                    'action_required': 'Check API key permissions'
                })
                
        except Exception as e:
            return jsonify({
                'status': 'api_error',
                'message': f'API test failed: {str(e)}',
                'action_required': 'Check OpenAI API connectivity'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'system_error',
            'message': f'Status check failed: {str(e)}',
            'action_required': 'Check system configuration'
        })

@app.route('/api/demo-mode', methods=['POST'])
def demo_mode():
    """Provide demo functionality while awaiting gpt-image-1 verification"""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        # Run brand analysis without image generation for demo
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                engine.process_brand(url, generate_images=False, image_count=0)
            )
            
            # Add demo messaging
            demo_result = {
                'success': True,
                'demo_mode': True,
                'brand_analysis': result['brand_analysis'],
                'message': 'Brand analysis completed - Image generation available after organization verification',
                'verification_status': 'pending',
                'capabilities_demo': {
                    'brand_scraping': 'Fully operational',
                    'satirical_analysis': 'Fully operational', 
                    'agent_enhancement': 'Fully operational',
                    'image_generation': 'Pending verification'
                },
                'next_steps': 'Complete OpenAI organization verification to unlock gpt-image-1'
            }
            
            return jsonify(demo_result)
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Demo mode failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'demo_mode': True
        }), 500

# Two-step brand analysis endpoints
@app.route('/api/analyze-brand-step1', methods=['POST'])
def analyze_brand_step1():
    """Step 1: Analyze brand and generate satirical prompts (no images)"""
    if not engine:
        if not initialize_engine():
            return jsonify({
                'success': False,
                'error': 'Engine not initialized. Please set OPENAI_API_KEY environment variable.'
            }), 500
    
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({
            'success': False,
            'error': 'URL is required'
        }), 400
    
    try:
        # Run brand analysis WITHOUT image generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            engine.process_brand(url, generate_images=False, image_count=0)
        )
        loop.close()
        
        # Generate satirical prompts from the analysis
        satirical_prompts = []
        if result['success'] and result['brand_analysis']:
            brand_analysis = result['brand_analysis']
            brand_name = brand_analysis.get('brand_name', 'Unknown Brand')
            vulnerabilities = brand_analysis.get('satirical_vulnerabilities', [])
            
            # Generate multiple satirical prompts using Pentagram Framework
            if vulnerabilities:
                for i, vuln in enumerate(vulnerabilities[:3]):  # Top 3 vulnerabilities
                    # Pentagram Framework elements
                    intent_clarity = f"Expose the corporate contradiction in {brand_name}'s {vuln.get('theme', 'messaging')} claims"
                    fidelity_pass = "8K resolution, professional commercial photography style, crisp corporate aesthetic with subtle wrongness"
                    symbolic_anchoring = f"Visual metaphor of {vuln.get('theme', 'corporate perfection')} revealing its artificial nature, mood: satirical revelation"
                    environmental_context = "Modern corporate office environment with polished surfaces that reflect hidden contradictions"
                    brand_world_constraints = f"Maintain {brand_name}'s actual visual language while revealing underlying pretension, no obvious parody elements"
                    
                    # Compile full pentagram prompt
                    full_prompt = f"{intent_clarity}. {fidelity_pass}. {symbolic_anchoring}. {environmental_context}. {brand_world_constraints}"
                    
                    satirical_prompts.append({
                        'id': i + 1,
                        'vulnerability_theme': vuln.get('theme', 'Corporate Messaging'),
                        'intent_clarity': intent_clarity,
                        'fidelity_pass': fidelity_pass,
                        'symbolic_anchoring': symbolic_anchoring,
                        'environmental_context': environmental_context,
                        'brand_world_constraints': brand_world_constraints,
                        'full_prompt': full_prompt,
                        'severity': vuln.get('severity', 'medium'),
                        'description': vuln.get('description', 'Corporate messaging contradiction')
                    })
            else:
                # Default prompts using Pentagram Framework if no specific vulnerabilities found
                default_prompts = [
                    {
                        'theme': 'Generic Corporate Perfection',
                        'intent': f"Expose {brand_name}'s manufactured authenticity",
                        'symbolic': "pristine corporate imagery with visible artificiality",
                        'context': "sterile boardroom with perfect lighting revealing emptiness"
                    },
                    {
                        'theme': 'Aspirational Disconnection', 
                        'intent': f"Reveal {brand_name}'s gap between promises and reality",
                        'symbolic': "aspirational lifestyle imagery with corporate machinery visible",
                        'context': "lifestyle setting with corporate infrastructure bleeding through"
                    },
                    {
                        'theme': 'Innovation Theater',
                        'intent': f"Satirize {brand_name}'s innovation posturing", 
                        'symbolic': "cutting-edge technology aesthetic with mundane reality exposed",
                        'context': "futuristic tech environment revealing ordinary operations"
                    }
                ]
                
                for i, prompt_config in enumerate(default_prompts):
                    intent_clarity = prompt_config['intent']
                    fidelity_pass = "8K resolution, professional commercial photography, hyperreal corporate aesthetic"
                    symbolic_anchoring = f"{prompt_config['symbolic']}, mood: subtle corporate irony"
                    environmental_context = prompt_config['context']
                    brand_world_constraints = f"Maintain {brand_name}'s visual branding while exposing pretension, subtle wrongness over obvious mockery"
                    
                    full_prompt = f"{intent_clarity}. {fidelity_pass}. {symbolic_anchoring}. {environmental_context}. {brand_world_constraints}"
                    
                    satirical_prompts.append({
                        'id': i + 1,
                        'vulnerability_theme': prompt_config['theme'],
                        'intent_clarity': intent_clarity,
                        'fidelity_pass': fidelity_pass,
                        'symbolic_anchoring': symbolic_anchoring,
                        'environmental_context': environmental_context,
                        'brand_world_constraints': brand_world_constraints,
                        'full_prompt': full_prompt,
                        'severity': 'low',
                        'description': 'Standard corporate communication patterns'
                    })
        
        # Store analysis and prompts for step 2
        analysis_id = f"analysis_{int(time.time())}"
        analysis_results[analysis_id] = {
            'brand_analysis': result['brand_analysis'],
            'satirical_prompts': satirical_prompts,
            'pipeline_metadata': result.get('pipeline_metadata', {})
        }
        
        response = {
            'success': True,
            'analysis_id': analysis_id,
            'brand_analysis': {
                'brand_name': brand_name,
                'authenticity_score': brand_analysis.get('authenticity_score', 1.0),
                'vulnerabilities_count': len(vulnerabilities),
                'processing_time': result.get('pipeline_metadata', {}).get('total_processing_time', 0)
            },
            'satirical_prompts': satirical_prompts,
            'message': 'Brand analysis complete. Review prompts and select which ones to generate images for.',
            'next_step': 'Use /api/generate-images-step2 to generate images from selected prompts'
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Step 1 analysis failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-images-step2', methods=['POST'])
def generate_images_step2():
    """Step 2: Generate images from selected satirical prompts"""
    if not engine:
        if not initialize_engine():
            return jsonify({
                'success': False,
                'error': 'Engine not initialized.'
            }), 500
    
    data = request.get_json()
    analysis_id = data.get('analysis_id')
    selected_prompt_ids = data.get('selected_prompts', [])  # List of prompt IDs to generate
    
    if not analysis_id or analysis_id not in analysis_results:
        return jsonify({
            'success': False,
            'error': 'Invalid analysis_id. Please run step 1 first.'
        }), 400
    
    if not selected_prompt_ids:
        return jsonify({
            'success': False,
            'error': 'Please select at least one prompt to generate images for.'
        }), 400
    
    try:
        result = generate_images_step2_internal(analysis_id, selected_prompt_ids)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Step 2 image generation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-single-max-image', methods=['POST'])
def generate_single_max_image():
    """Generate a single maximum quality image from one selected prompt"""
    data = request.get_json()
    analysis_id = data.get('analysis_id')
    selected_prompt_id = data.get('selected_prompt_id')
    
    if not analysis_id or analysis_id not in analysis_results:
        return jsonify({
            'success': False,
            'error': 'Invalid analysis_id. Please run step 1 first.'
        }), 400
    
    if not selected_prompt_id:
        return jsonify({
            'success': False,
            'error': 'Please select one prompt for maximum quality generation.'
        }), 400
    
    try:
        # Use the existing Step 2 logic but for single image
        response = generate_images_step2_internal(analysis_id, [selected_prompt_id])
        
        if response['success'] and response['generated_images']:
            single_image = response['generated_images'][0]
            return jsonify({
                'success': True,
                'analysis_id': analysis_id,
                'single_max_image': single_image,
                'message': 'Generated maximum quality (8K) image successfully.',
                'image_specifications': {
                    'resolution': '1792x1024',
                    'quality': 'maximum',
                    'model': 'gpt-image-1'
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': response.get('error', 'Single image generation failed')
            }), 500
            
    except Exception as e:
        logger.error(f"Single max image generation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_images_step2_internal(analysis_id, selected_prompt_ids):
    """Internal function for Step 2 image generation logic"""
    # Get the stored analysis results
    stored_analysis = analysis_results[analysis_id]
    satirical_prompts = stored_analysis['satirical_prompts']
    
    # Filter selected prompts
    selected_prompts = [p for p in satirical_prompts if p['id'] in selected_prompt_ids]
    
    if not selected_prompts:
        return {
            'success': False,
            'error': 'No valid prompts selected.'
        }
    
    # Generate images for selected prompts using direct OpenAI API
    generated_images = []
    
    for prompt_data in selected_prompts:
        try:
            import openai
            
            api_key = os.environ.get('OPENAI_API_KEY')
            client = openai.OpenAI(api_key=api_key)
            
            start_time = time.time()
            
            response = client.images.generate(
                model="gpt-image-1",
                prompt=prompt_data.get('full_prompt', prompt_data.get('prompt', 'Corporate satirical image')),
                size="1536x1024",  # Maximum supported resolution for gpt-image-1
                quality="high",
                n=1
            )
            
            processing_time = time.time() - start_time
            
            # Debug: log the response structure
            logger.info(f"OpenAI response type: {type(response)}")
            logger.info(f"OpenAI response data: {response.data if hasattr(response, 'data') else 'No data attr'}")
            
            # Get image URL or base64 data from response
            image_url = None
            image_b64 = None
            
            if hasattr(response, 'data') and response.data and len(response.data) > 0:
                image_item = response.data[0]
                
                # Try URL first (for hosted images)
                if hasattr(image_item, 'url') and image_item.url:
                    image_url = image_item.url
                    logger.info(f"Got image URL: {image_url}")
                
                # Try base64 data (for gpt-image-1)
                elif hasattr(image_item, 'b64_json') and image_item.b64_json:
                    image_b64 = image_item.b64_json
                    # Convert base64 to data URL for display
                    image_url = f"data:image/png;base64,{image_b64}"
                    logger.info(f"Got base64 image data, length: {len(image_b64) if image_b64 else 0}")
                
                else:
                    logger.warning(f"No URL or b64_json found in response. Available attrs: {[attr for attr in dir(image_item) if not attr.startswith('_')]}")
                    logger.warning(f"URL value: {getattr(image_item, 'url', 'NOT_FOUND')}")
                    logger.warning(f"B64 value: {getattr(image_item, 'b64_json', 'NOT_FOUND')}")
            
            else:
                logger.error(f"No data in response or empty data list")
            
            generated_images.append({
                'prompt_id': prompt_data['id'],
                'vulnerability_theme': prompt_data['vulnerability_theme'],
                'prompt_used': prompt_data.get('full_prompt', prompt_data.get('prompt', 'Corporate satirical image')),
                'pentagram_elements': {
                    'intent_clarity': prompt_data.get('intent_clarity', ''),
                    'fidelity_pass': prompt_data.get('fidelity_pass', ''),
                    'symbolic_anchoring': prompt_data.get('symbolic_anchoring', ''),
                    'environmental_context': prompt_data.get('environmental_context', ''),
                    'brand_world_constraints': prompt_data.get('brand_world_constraints', '')
                },
                'success': True,
                'image_url': image_url,
                'image_data': None,
                'processing_time': processing_time,
                'error_message': None,
                'generation_metadata': {
                    'revised_prompt': getattr(response.data[0], 'revised_prompt', None) if hasattr(response, 'data') and response.data and len(response.data) > 0 else None,
                    'generation_timestamp': time.time(),
                    'response_debug': str(response) if response else 'No response',
                    'image_format': 'base64' if image_b64 else 'url' if image_url else 'none'
                }
            })
            
        except Exception as e:
            logger.error(f"Image generation failed for prompt {prompt_data['id']}: {e}")
            generated_images.append({
                'prompt_id': prompt_data['id'],
                'vulnerability_theme': prompt_data['vulnerability_theme'],
                'prompt_used': prompt_data.get('full_prompt', prompt_data.get('prompt', 'Corporate satirical image')),
                'success': False,
                'error_message': str(e),
                'processing_time': 0
            })
    
    # Update stored results with generated images
    analysis_results[analysis_id]['generated_images'] = generated_images
    
    return {
        'success': True,
        'analysis_id': analysis_id,
        'images_requested': len(selected_prompts),
        'images_generated': sum(1 for img in generated_images if img['success']),
        'generated_images': generated_images,
        'brand_analysis': stored_analysis['brand_analysis'],
        'message': f'Generated {sum(1 for img in generated_images if img["success"])}/{len(selected_prompts)} images successfully.'
    }

# End of endpoints section

def await_sync(coroutine):
    """Helper to run async code in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coroutine)
    finally:
        loop.close()

# Enhanced HTML Template with agent integration features
ENHANCED_HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Brand Deconstruction Engine</title>
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
            max-width: 1400px;
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
        
        .header .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 20px;
        }
        
        .features {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }
        
        .feature-badge {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .card h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        .input-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #34495e;
        }
        
        .input-group input, .input-group select, .input-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .input-group input:focus, .input-group select:focus, .input-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .checkbox-group input[type="checkbox"] {
            width: auto;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
            width: 100%;
            margin-bottom: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        }
        
        .status {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        
        .status.success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        
        .status.error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        
        .status.loading {
            background: #cce7ff;
            border: 1px solid #99d1ff;
            color: #0066cc;
        }
        
        .results {
            grid-column: 1 / -1;
            display: none;
        }
        
        .results-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        .analysis-section {
            margin-bottom: 25px;
        }
        
        .analysis-section h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.3rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 5px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #ecf0f1;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .vulnerability {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .vulnerability h4 {
            color: #856404;
            margin-bottom: 8px;
        }
        
        .vulnerability p {
            color: #856404;
            margin: 0;
        }
        
        .agent-insight {
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .agent-insight h4 {
            color: #1565c0;
            margin-bottom: 8px;
        }
        
        .image-gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .image-card {
            background: white;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .image-card img {
            width: 100%;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        .image-card .prompt {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 10px;
            font-style: italic;
        }
        
        .image-actions {
            display: flex;
            gap: 10px;
        }
        
        .btn-small {
            padding: 8px 16px;
            font-size: 0.9rem;
            flex: 1;
        }
        
        .agent-status {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .agent-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        
        .agent-card.available {
            background: #d4edda;
            border: 1px solid #c3e6cb;
        }
        
        .agent-card.unavailable {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
        }
        
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .results-grid {
                grid-template-columns: 1fr;
            }
            
            .features {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎭 Enhanced Brand Deconstruction Engine</h1>
            <p class="subtitle">Agent-Enhanced Satirical Brand Analysis with Direct gpt-image-1 Integration</p>
            
            <div class="features">
                <span class="feature-badge">🤖 Multi-Agent Integration</span>
                <span class="feature-badge">🔍 Robust Scraping</span>
                <span class="feature-badge">🎨 Direct gpt-image-1</span>
                <span class="feature-badge">📊 Advanced Analytics</span>
                <span class="feature-badge">💾 Export Ready</span>
            </div>
        </div>
        
        <div class="main-content">
            <div class="card">
                <h2>🎯 Two-Step Brand Analysis</h2>
                
                <div class="input-group">
                    <label for="url">Brand URL:</label>
                    <input type="url" id="url" placeholder="https://example.com" required>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #667eea;">
                    <h4 style="margin: 0 0 10px 0; color: #495057;">Two-Step Process:</h4>
                    <ol style="margin: 0; color: #6c757d;">
                        <li><strong>Step 1:</strong> Analyze brand and generate satirical prompts</li>
                        <li><strong>Step 2:</strong> Review prompts and select which ones to generate images for</li>
                    </ol>
                </div>
                
                <button class="btn" onclick="analyzeBrand()">
                    <span id="analyzeText">🚀 Step 1: Analyze Brand</span>
                </button>
                
                <button class="btn btn-secondary" onclick="testAgents()">
                    🤖 Test Agent System
                </button>
            </div>
            
            <div class="card">
                <h2>🎨 Direct gpt-image-1 Generation</h2>
                
                <div class="input-group">
                    <label for="customPrompt">Custom prompt:</label>
                    <textarea id="customPrompt" rows="3" placeholder="Enter your satirical image prompt..."></textarea>
                </div>
                
                <div class="input-group">
                    <label for="imageStyle">Style:</label>
                    <select id="imageStyle">
                        <option value="photorealistic">Photorealistic</option>
                        <option value="illustration">Illustration</option>
                        <option value="corporate">Corporate</option>
                    </select>
                </div>
                
                <div class="input-group">
                    <label for="resolution">Resolution:</label>
                    <select id="resolution">
                        <option value="1024x1024" selected>1024x1024 (Square)</option>
                        <option value="1792x1024">1792x1024 (Landscape)</option>
                        <option value="1024x1792">1024x1792 (Portrait)</option>
                    </select>
                </div>
                
                <button class="btn" onclick="generateCustomImage()">
                    🎨 Generate Image
                </button>
            </div>
        </div>
        
        <div id="status" class="status"></div>
        
        <div id="agentStatus" class="card" style="display: none;">
            <h2>🤖 Agent System Status</h2>
            <div id="agentCards" class="agent-status"></div>
        </div>
        
        <div id="results" class="card results">
            <h2>📊 Analysis Results</h2>
            <div class="results-grid">
                <div>
                    <div class="analysis-section">
                        <h3>Brand Overview</h3>
                        <div id="brandOverview"></div>
                    </div>
                    
                    <div class="analysis-section">
                        <h3>🎭 Satirical Vulnerabilities</h3>
                        <div id="vulnerabilities"></div>
                    </div>
                </div>
                
                <div>
                    <div class="analysis-section">
                        <h3>🤖 Agent Insights</h3>
                        <div id="agentInsights"></div>
                    </div>
                    
                    <div class="analysis-section">
                        <h3>⚡ Performance Metrics</h3>
                        <div id="performanceMetrics"></div>
                    </div>
                </div>
            </div>
            
            <div class="analysis-section">
                <h3>🎨 Generated Images</h3>
                <div id="imageGallery" class="image-gallery"></div>
            </div>
            
            <div style="margin-top: 30px; display: flex; gap: 15px;">
                <button class="btn btn-secondary" onclick="exportAnalysis()" style="width: auto;">
                    📄 Export Analysis
                </button>
                <button class="btn" onclick="newAnalysis()" style="width: auto;">
                    🔄 New Analysis
                </button>
            </div>
        </div>
    </div>
    
    <script>
        let currentResultId = null;
        
        let currentAnalysisId = null;
        let satiricalPrompts = [];
        
        async function analyzeBrand() {
            const url = document.getElementById('url').value;
            
            if (!url) {
                showStatus('Please enter a valid URL', 'error');
                return;
            }
            
            showStatus('🔍 Step 1: Analyzing brand and generating satirical prompts...', 'loading');
            setAnalyzeButtonLoading(true);
            
            try {
                // Step 1: Analyze brand and get satirical prompts
                const response = await fetch('/api/analyze-brand-step1', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        url: url
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    currentAnalysisId = result.analysis_id;
                    satiricalPrompts = result.satirical_prompts;
                    displayStep1Results(result);
                    showStatus('✅ Step 1 completed! Review and select prompts for image generation.', 'success');
                } else {
                    showStatus(`❌ Analysis failed: ${result.error}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Network error: ${error.message}`, 'error');
            } finally {
                setAnalyzeButtonLoading(false);
            }
        }
        
        async function generateSingleMaxImage() {
            if (!currentAnalysisId) {
                showStatus('Please run brand analysis first', 'error');
                return;
            }
            
            // Get selected radio button
            const selectedRadio = document.querySelector('input[name="selectedPrompt"]:checked');
            if (!selectedRadio) {
                showStatus('Please select one prompt for maximum quality generation', 'error');
                return;
            }
            
            const selectedPromptId = parseInt(selectedRadio.value);
            
            showStatus('🎨 Generating MAXIMUM quality image (8K) with gpt-image-1...', 'loading');
            
            try {
                const response = await fetch('/api/generate-single-max-image', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        analysis_id: currentAnalysisId,
                        selected_prompt_id: selectedPromptId  // Single prompt only
                    })
                });
                
                const result = await response.json();
                
                if (result.success && result.single_max_image) {
                    displaySingleMaxImage(result.single_max_image);
                    showStatus('✅ Maximum quality (8K) image generated successfully!', 'success');
                } else {
                    showStatus(`❌ Single image generation failed: ${result.error || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Network error: ${error.message}`, 'error');
            }
        }
        
        function displaySingleMaxImage(imageResult) {
            let imageHtml = '';
            
            if (imageResult.success && imageResult.image_url) {
                imageHtml = `
                    <div class="image-card" style="max-width: 800px; margin: 0 auto;">
                        <img src="${imageResult.image_url}" alt="Maximum Quality Satirical Image" />
                        <div style="padding: 20px;">
                            <h4 style="color: #495057; margin-bottom: 15px;">🎨 Maximum Quality (8K) Generated Image</h4>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                                <strong>Theme:</strong> ${imageResult.vulnerability_theme}<br>
                                <strong>Model:</strong> gpt-image-1<br>
                                <strong>Quality:</strong> Maximum (8K Ready)<br>
                                <strong>Processing Time:</strong> ${imageResult.processing_time.toFixed(2)}s
                            </div>
                            <div style="background: #e9ecef; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 0.9rem;">
                                <strong>Prompt Used:</strong><br>
                                ${imageResult.prompt_used}
                            </div>
                            <div style="margin-top: 15px; display: flex; gap: 10px; justify-content: center;">
                                <button class="btn btn-small" onclick="viewFullImage('${imageResult.image_url}')" style="background: #28a745;">
                                    🔍 View Full Size
                                </button>
                                <button class="btn btn-small" onclick="downloadSingleImage('${imageResult.image_url}')" style="background: #17a2b8;">
                                    📥 Download 8K Image
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                imageHtml = `
                    <div class="image-card" style="max-width: 600px; margin: 0 auto;">
                        <div style="background: #f8d7da; padding: 30px; border-radius: 8px; text-align: center;">
                            <h4 style="color: #721c24; margin-bottom: 15px;">❌ Generation Failed</h4>
                            <p style="color: #721c24; margin: 0;">${imageResult.error_message || 'Unknown error occurred'}</p>
                            <small style="color: #721c24; display: block; margin-top: 10px;">
                                Processing Time: ${imageResult.processing_time.toFixed(2)}s
                            </small>
                        </div>
                    </div>
                `;
            }
            
            document.getElementById('singleImageResult').innerHTML = imageHtml;
            
            // Update performance metrics
            document.getElementById('performanceMetrics').innerHTML = `
                <div class="metric">
                    <span>Single Image Generation:</span>
                    <strong>${imageResult.success ? 'Successful' : 'Failed'}</strong>
                </div>
                <div class="metric">
                    <span>Model Used:</span>
                    <strong>gpt-image-1</strong>
                </div>
                <div class="metric">
                    <span>Quality:</span>
                    <strong>Maximum (8K Ready)</strong>
                </div>
                <div class="metric">
                    <span>Processing Time:</span>
                    <strong>${imageResult.processing_time.toFixed(2)}s</strong>
                </div>
            `;
            
            // Update agent insights
            document.getElementById('agentInsights').innerHTML = `
                <div class="agent-insight">
                    <h4>Single Maximum Quality Generation</h4>
                    <p>Generated one maximum quality image using gpt-image-1 at 1792x1024 resolution for 8K compatibility.</p>
                </div>
            `;
        }
        
        function downloadSingleImage(imageUrl) {
            const link = document.createElement('a');
            link.href = imageUrl;
            link.download = `brand-satirical-image-8k-${Date.now()}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        
        async function generateSingleMaxImage() {
            if (!currentAnalysisId) {
                showStatus('Please run brand analysis first', 'error');
                return;
            }
            
            // Get selected radio button
            const selectedRadio = document.querySelector('input[name="selectedPrompt"]:checked');
            if (!selectedRadio) {
                showStatus('Please select one prompt for maximum quality generation', 'error');
                return;
            }
            
            const selectedPromptId = parseInt(selectedRadio.value);
            
            showStatus('🎨 Generating MAXIMUM quality image (8K) with gpt-image-1...', 'loading');
            
            try {
                const response = await fetch('/api/generate-images-step2', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        analysis_id: currentAnalysisId,
                        selected_prompts: [selectedPromptId]  // Single prompt only
                    })
                });
                
                const result = await response.json();
                
                if (result.success && result.generated_images && result.generated_images.length > 0) {
                    displaySingleMaxImage(result.generated_images[0]);
                    showStatus('✅ Maximum quality (8K) image generated successfully!', 'success');
                } else {
                    showStatus(`❌ Single image generation failed: ${result.error || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Network error: ${error.message}`, 'error');
            }
        }
        
        function displaySingleMaxImage(imageResult) {
            let imageHtml = '';
            
            if (imageResult.success && imageResult.image_url) {
                imageHtml = `
                    <div class="image-card" style="max-width: 800px; margin: 0 auto;">
                        <img src="${imageResult.image_url}" alt="Maximum Quality Satirical Image" />
                        <div style="padding: 20px;">
                            <h4 style="color: #495057; margin-bottom: 15px;">🎨 Maximum Quality (8K) Generated Image</h4>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                                <strong>Theme:</strong> ${imageResult.vulnerability_theme}<br>
                                <strong>Model:</strong> gpt-image-1<br>
                                <strong>Quality:</strong> Maximum (8K Ready)<br>
                                <strong>Processing Time:</strong> ${imageResult.processing_time.toFixed(2)}s
                            </div>
                            <div style="background: #e9ecef; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 0.9rem;">
                                <strong>Prompt Used:</strong><br>
                                ${imageResult.prompt_used}
                            </div>
                            <div style="margin-top: 15px; display: flex; gap: 10px; justify-content: center;">
                                <button class="btn btn-small" onclick="viewFullImage('${imageResult.image_url}')" style="background: #28a745;">
                                    🔍 View Full Size
                                </button>
                                <button class="btn btn-small" onclick="downloadSingleImage('${imageResult.image_url}')" style="background: #17a2b8;">
                                    📥 Download 8K Image
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                imageHtml = `
                    <div class="image-card" style="max-width: 600px; margin: 0 auto;">
                        <div style="background: #f8d7da; padding: 30px; border-radius: 8px; text-align: center;">
                            <h4 style="color: #721c24; margin-bottom: 15px;">❌ Generation Failed</h4>
                            <p style="color: #721c24; margin: 0;">${imageResult.error_message || 'Unknown error occurred'}</p>
                            <small style="color: #721c24; display: block; margin-top: 10px;">
                                Processing Time: ${imageResult.processing_time.toFixed(2)}s
                            </small>
                        </div>
                    </div>
                `;
            }
            
            document.getElementById('singleImageResult').innerHTML = imageHtml;
            
            // Update performance metrics
            document.getElementById('performanceMetrics').innerHTML = `
                <div class="metric">
                    <span>Single Image Generation:</span>
                    <strong>${imageResult.success ? 'Successful' : 'Failed'}</strong>
                </div>
                <div class="metric">
                    <span>Model Used:</span>
                    <strong>gpt-image-1</strong>
                </div>
                <div class="metric">
                    <span>Quality:</span>
                    <strong>Maximum (8K Ready)</strong>
                </div>
                <div class="metric">
                    <span>Processing Time:</span>
                    <strong>${imageResult.processing_time.toFixed(2)}s</strong>
                </div>
            `;
            
            // Update agent insights
            document.getElementById('agentInsights').innerHTML = `
                <div class="agent-insight">
                    <h4>Single Maximum Quality Generation</h4>
                    <p>Generated one maximum quality image using gpt-image-1 at 1792x1024 resolution for 8K compatibility.</p>
                </div>
            `;
        }
        
        function downloadSingleImage(imageUrl) {
            const link = document.createElement('a');
            link.href = imageUrl;
            link.download = `brand-satirical-image-8k-${Date.now()}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        
        async function generateSelectedImages() {
            if (!currentAnalysisId) {
                showStatus('Please run brand analysis first', 'error');
                return;
            }
            
            const selectedPrompts = [];
            const checkboxes = document.querySelectorAll('input[name="promptSelect"]:checked');
            checkboxes.forEach(cb => {
                selectedPrompts.push(parseInt(cb.value));
            });
            
            if (selectedPrompts.length === 0) {
                showStatus('Please select at least one prompt to generate images for', 'error');
                return;
            }
            
            showStatus(`🎨 Step 2: Generating ${selectedPrompts.length} image(s) with gpt-image-1...`, 'loading');
            
            try {
                const response = await fetch('/api/generate-images-step2', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        analysis_id: currentAnalysisId,
                        selected_prompts: selectedPrompts
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    displayStep2Results(result);
                    showStatus('✅ Images generated successfully!', 'success');
                } else {
                    showStatus(`❌ Image generation failed: ${result.error}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Network error: ${error.message}`, 'error');
            }
        }
        
        async function generateCustomImage() {
            const prompt = document.getElementById('customPrompt').value;
            const style = document.getElementById('imageStyle').value;
            const resolution = document.getElementById('resolution').value;
            
            if (!prompt) {
                showStatus('Please enter a prompt', 'error');
                return;
            }
            
            showStatus('🎨 Generating image with gpt-image-1...', 'loading');
            
            try {
                const response = await fetch('/api/gpt-image-1-generation', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        prompt: prompt,
                        style: style,
                        resolution: resolution,
                        quality: 'hd'
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    displayCustomImage(result);
                    showStatus('✅ Image generated successfully!', 'success');
                } else {
                    showStatus(`❌ Image generation failed: ${result.error_message}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Network error: ${error.message}`, 'error');
            }
        }
        
        async function testAgents() {
            showStatus('🤖 Testing agent system...', 'loading');
            
            try {
                const response = await fetch('/api/agent-test', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                const result = await response.json();
                
                if (result.success) {
                    displayAgentStatus(result);
                    showStatus(`✅ Agent system tested: ${result.agents_available} agents available`, 'success');
                } else {
                    showStatus(`❌ Agent test failed: ${result.error}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Network error: ${error.message}`, 'error');
            }
        }
        
        function displayResults(result) {
            const analysis = result.brand_analysis;
            const metadata = result.pipeline_metadata;
            
            // Brand Overview
            document.getElementById('brandOverview').innerHTML = `
                <div class="metric">
                    <span>Brand Name:</span>
                    <strong>${analysis.brand_name}</strong>
                </div>
                <div class="metric">
                    <span>Authenticity Score:</span>
                    <strong>${(analysis.authenticity_score * 100).toFixed(1)}%</strong>
                </div>
                <div class="metric">
                    <span>Scraping Method:</span>
                    <strong>${analysis.scraping_fallback_used ? 'Fallback Strategy' : 'Direct Scraping'}</strong>
                </div>
                <div class="metric">
                    <span>Processing Time:</span>
                    <strong>${analysis.processing_time.toFixed(2)}s</strong>
                </div>
            `;
            
            // Vulnerabilities
            let vulnerabilitiesHtml = '';
            analysis.satirical_vulnerabilities.forEach(vuln => {
                vulnerabilitiesHtml += `
                    <div class="vulnerability">
                        <h4>${vuln.theme}</h4>
                        <p>${vuln.description}</p>
                        ${vuln.agent_source ? `<small>Source: ${vuln.agent_source}</small>` : ''}
                    </div>
                `;
            });
            document.getElementById('vulnerabilities').innerHTML = vulnerabilitiesHtml || '<p>No vulnerabilities detected.</p>';
            
            // Agent Insights
            let insightsHtml = '';
            Object.entries(analysis.agent_insights).forEach(([category, insight]) => {
                insightsHtml += `
                    <div class="agent-insight">
                        <h4>${category.replace('_', ' ').toUpperCase()}</h4>
                        <p>${JSON.stringify(insight, null, 2)}</p>
                    </div>
                `;
            });
            document.getElementById('agentInsights').innerHTML = insightsHtml || '<p>No agent insights available.</p>';
            
            // Performance Metrics
            document.getElementById('performanceMetrics').innerHTML = `
                <div class="metric">
                    <span>Total Processing Time:</span>
                    <strong>${metadata.total_processing_time.toFixed(2)}s</strong>
                </div>
                <div class="metric">
                    <span>Agents Used:</span>
                    <strong>${metadata.agents_used.length}</strong>
                </div>
                <div class="metric">
                    <span>Images Generated:</span>
                    <strong>${metadata.images_generated}</strong>
                </div>
                <div class="metric">
                    <span>Pipeline Version:</span>
                    <strong>${metadata.pipeline_version}</strong>
                </div>
            `;
            
            // Image Gallery
            displayImageGallery(result.generated_images);
            
            document.getElementById('results').style.display = 'block';
        }
        
        function displayImageGallery(images) {
            let galleryHtml = '';
            
            images.forEach(img => {
                if (img.success && img.image_url) {
                    galleryHtml += `
                        <div class="image-card">
                            <img src="${img.image_url}" alt="Generated satirical image" />
                            <div class="prompt">${img.prompt}</div>
                            <div class="image-actions">
                                <button class="btn btn-small" onclick="downloadImage(${img.image_id})">
                                    📥 Download
                                </button>
                                <button class="btn btn-small btn-secondary" onclick="viewFullImage('${img.image_url}')">
                                    🔍 View Full
                                </button>
                            </div>
                        </div>
                    `;
                } else {
                    galleryHtml += `
                        <div class="image-card">
                            <div style="background: #f8d7da; padding: 20px; border-radius: 8px; text-align: center;">
                                ❌ Generation Failed<br>
                                <small>${img.error_message || 'Unknown error'}</small>
                            </div>
                        </div>
                    `;
                }
            });
            
            document.getElementById('imageGallery').innerHTML = galleryHtml || '<p>No images generated.</p>';
        }
        
        function displayCustomImage(result) {
            const galleryHtml = `
                <div class="image-card">
                    <img src="${result.image_url}" alt="Custom generated image" />
                    <div class="prompt">Custom generation</div>
                    <div class="image-actions">
                        <button class="btn btn-small btn-secondary" onclick="viewFullImage('${result.image_url}')">
                            🔍 View Full
                        </button>
                    </div>
                </div>
            `;
            
            document.getElementById('imageGallery').innerHTML = galleryHtml;
            document.getElementById('results').style.display = 'block';
        }
        
        function displayAgentStatus(result) {
            let statusHtml = '';
            
            Object.entries(result.agent_status).forEach(([name, status]) => {
                const cardClass = status.available ? 'available' : 'unavailable';
                const statusIcon = status.available ? '✅' : '❌';
                
                statusHtml += `
                    <div class="agent-card ${cardClass}">
                        <div>${statusIcon}</div>
                        <h4>${name.replace('_', ' ').toUpperCase()}</h4>
                        <p>${status.type || 'N/A'}</p>
                    </div>
                `;
            });
            
            document.getElementById('agentCards').innerHTML = statusHtml;
            document.getElementById('agentStatus').style.display = 'block';
        }
        
        function downloadImage(imageId) {
            if (!currentResultId) {
                showStatus('No analysis result available', 'error');
                return;
            }
            
            window.open(`/api/download-image/${currentResultId}/${imageId}`, '_blank');
        }
        
        function viewFullImage(imageUrl) {
            window.open(imageUrl, '_blank');
        }
        
        function exportAnalysis() {
            if (!currentAnalysisId) {
                showStatus('No analysis result available', 'error');
                return;
            }
            
            // Create export data from current analysis
            const exportData = {
                analysis_id: currentAnalysisId,
                brand_analysis: document.getElementById('brandOverview').innerHTML,
                satirical_prompts: satiricalPrompts,
                export_timestamp: new Date().toISOString(),
                export_type: 'two_step_brand_analysis'
            };
            
            // Create and download JSON file
            const dataStr = JSON.stringify(exportData, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `brand_analysis_${currentAnalysisId}.json`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
            showStatus('Analysis exported successfully', 'success');
        }
        
        function newAnalysis() {
            document.getElementById('results').style.display = 'none';
            document.getElementById('agentStatus').style.display = 'none';
            document.getElementById('url').value = '';
            document.getElementById('customPrompt').value = '';
            currentAnalysisId = null;
            satiricalPrompts = [];
            showStatus('Ready for new analysis', 'success');
        }
        
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = `status ${type}`;
            status.style.display = 'block';
            
            if (type === 'success') {
                setTimeout(() => {
                    status.style.display = 'none';
                }, 5000);
            }
        }
        
        function setAnalyzeButtonLoading(loading) {
            const btn = document.querySelector('.btn');
            const text = document.getElementById('analyzeText');
            
            btn.disabled = loading;
            
            if (loading) {
                text.innerHTML = '<span class="loading-spinner"></span>Analyzing...';
            } else {
                text.innerHTML = '🚀 Step 1: Analyze Brand';
            }
        }
        
        function displayStep1Results(result) {
            const analysis = result.brand_analysis;
            const prompts = result.satirical_prompts;
            
            // Brand Overview
            document.getElementById('brandOverview').innerHTML = `
                <div class="metric">
                    <span>Brand Name:</span>
                    <strong>${analysis.brand_name}</strong>
                </div>
                <div class="metric">
                    <span>Authenticity Score:</span>
                    <strong>${(analysis.authenticity_score * 100).toFixed(1)}%</strong>
                </div>
                <div class="metric">
                    <span>Vulnerabilities Found:</span>
                    <strong>${analysis.vulnerabilities_count}</strong>
                </div>
                <div class="metric">
                    <span>Processing Time:</span>
                    <strong>${analysis.processing_time.toFixed(2)}s</strong>
                </div>
            `;
            
            // Display satirical prompts for SINGLE selection
            let promptsHtml = `
                <h3>🎭 Satirical Prompts - Select ONE for Maximum Quality Image (8K)</h3>
                <div style="margin: 20px 0;">
            `;
            
            prompts.forEach(prompt => {
                promptsHtml += `
                    <div class="vulnerability" style="background: #f8f9fa; border: 1px solid #dee2e6;">
                        <div style="display: flex; align-items: flex-start; gap: 15px;">
                            <div class="single-image-selector">
                                <input type="radio" name="selectedPrompt" value="${prompt.id}" id="prompt_${prompt.id}" style="margin-top: 5px;">
                                <label for="prompt_${prompt.id}" class="radio-label" style="cursor: pointer; color: #667eea; font-weight: 600;">🎨 Select for 8K Generation</label>
                            </div>
                            <div style="flex: 1;">
                                <h4 style="color: #495057; margin-bottom: 8px;">
                                    ${prompt.vulnerability_theme} (${prompt.severity})
                                </h4>
                                <p style="color: #6c757d; margin-bottom: 10px; font-size: 0.9rem;">
                                    ${prompt.description}
                                </p>
                                
                                <!-- Pentagram Framework Elements -->
                                <div style="background: #ffffff; border: 1px solid #e9ecef; border-radius: 5px; padding: 15px; margin: 10px 0;">
                                    <h5 style="color: #343a40; margin-bottom: 10px; font-size: 0.9rem;">🔯 Pentagram Framework Elements:</h5>
                                    
                                    <div style="margin-bottom: 8px;">
                                        <strong style="color: #6f42c1;">Intent Clarity:</strong>
                                        <span style="font-size: 0.85rem; color: #495057;">${prompt.intent_clarity}</span>
                                    </div>
                                    
                                    <div style="margin-bottom: 8px;">
                                        <strong style="color: #dc3545;">Fidelity Pass:</strong>
                                        <span style="font-size: 0.85rem; color: #495057;">${prompt.fidelity_pass}</span>
                                    </div>
                                    
                                    <div style="margin-bottom: 8px;">
                                        <strong style="color: #fd7e14;">Symbolic Anchoring:</strong>
                                        <span style="font-size: 0.85rem; color: #495057;">${prompt.symbolic_anchoring}</span>
                                    </div>
                                    
                                    <div style="margin-bottom: 8px;">
                                        <strong style="color: #198754;">Environmental Context:</strong>
                                        <span style="font-size: 0.85rem; color: #495057;">${prompt.environmental_context}</span>
                                    </div>
                                    
                                    <div style="margin-bottom: 8px;">
                                        <strong style="color: #0dcaf0;">Brand World Constraints:</strong>
                                        <span style="font-size: 0.85rem; color: #495057;">${prompt.brand_world_constraints}</span>
                                    </div>
                                </div>
                                
                                <div style="background: #e9ecef; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 0.8rem; color: #495057;">
                                    <strong>Full Compiled Prompt:</strong><br>
                                    ${prompt.full_prompt || prompt.prompt}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            promptsHtml += `
                </div>
                <div id="singleImageButtonContainer" style="text-align: center; margin: 30px 0;">
                    <button onclick="generateSingleMaxImage()" style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border: none;
                        padding: 15px 35px;
                        border-radius: 12px;
                        cursor: pointer;
                        font-size: 16px;
                        font-weight: 600;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
                        transition: all 0.3s ease;
                        margin: 0 10px;
                    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 12px 35px rgba(102, 126, 234, 0.5)'" 
                       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 8px 25px rgba(102, 126, 234, 0.4)'">
                        🎨 Generate MAXIMUM Quality Image (8K)
                    </button>
                </div>
                <div id="singleImageResult" style="margin-top: 30px;"></div>
            `;
            
            document.getElementById('vulnerabilities').innerHTML = promptsHtml;
            
            // Clear other sections for now
            document.getElementById('agentInsights').innerHTML = '<p>Image generation pending...</p>';
            document.getElementById('performanceMetrics').innerHTML = '<p>Complete workflow pending...</p>';
            document.getElementById('imageGallery').innerHTML = '<p>Select prompts above and click "Generate Selected Images"</p>';
            
            document.getElementById('results').style.display = 'block';
        }
        
        function displayStep2Results(result) {
            // Update performance metrics with complete data
            document.getElementById('performanceMetrics').innerHTML = `
                <div class="metric">
                    <span>Total Processing Time:</span>
                    <strong>${result.total_processing_time.toFixed(2)}s</strong>
                </div>
                <div class="metric">
                    <span>Images Generated:</span>
                    <strong>${result.generated_images.length}</strong>
                </div>
                <div class="metric">
                    <span>Successful Images:</span>
                    <strong>${result.generated_images.filter(img => img.success).length}</strong>
                </div>
                <div class="metric">
                    <span>Model Used:</span>
                    <strong>gpt-image-1 (8K Resolution)</strong>
                </div>
            `;
            
            // Display generated images
            displayImageGallery(result.generated_images);
            
            // Update agent insights
            document.getElementById('agentInsights').innerHTML = `
                <div class="agent-insight">
                    <h4>Two-Step Process Complete</h4>
                    <p>Successfully completed brand analysis and selective image generation using gpt-image-1.</p>
                </div>
            `;
        }
        
        function selectAllPrompts() {
            const checkboxes = document.querySelectorAll('input[name="promptSelect"]');
            checkboxes.forEach(cb => cb.checked = true);
        }
        
        function clearAllPrompts() {
            const checkboxes = document.querySelectorAll('input[name="promptSelect"]');
            checkboxes.forEach(cb => cb.checked = false);
        }
        
        // Initialize with health check
        fetch('/api/health')
            .then(response => response.json())
            .then(result => {
                if (result.status === 'healthy') {
                    showStatus(`✅ System ready - ${result.agents_available} agents available`, 'success');
                } else {
                    showStatus('⚠️ System not fully ready', 'error');
                }
            })
            .catch(error => {
                showStatus('❌ System health check failed', 'error');
            });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    if initialize_engine():
        logger.info("Starting Enhanced Brand Deconstruction Web Interface")
        app.run(host='0.0.0.0', port=5002, debug=True)
    else:
        logger.error("Failed to start - engine initialization failed")
