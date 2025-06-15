# Phase 7: Vex Agent Integration for Visual Generation
# File: integrations/vex_client.py

import asyncio
import aiohttp
import json
import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class VexGenerationRequest:
    """Structure for requests to the Vex visual generation agent"""
    concept_prompt: str
    tone_guidance: str
    satirical_intensity: str
    brand_context: Dict[str, Any]
    generation_params: Dict[str, Any] = None

@dataclass
class VexGenerationResult:
    """Structure for results from Vex visual generation"""
    success: bool
    image_data: Optional[str]  # Base64 encoded image
    image_url: Optional[str]   # URL if hosted
    generation_metadata: Dict[str, Any]
    processing_time: float
    error_message: Optional[str] = None

class VexAgentClient:
    """
    Client for integrating with the Vex Visual Provocateur agent.
    
    This client transforms our satirical prompts into actual visual content
    through the external Vex agent. It handles the translation between our
    Pentagram Framework prompts and Vex's input requirements, ensuring that
    our brand analysis insights translate into impactful visual satirical content.
    """
    
    def __init__(self, vex_endpoint: str, api_key: str = None, timeout: int = 120):
        self.vex_endpoint = vex_endpoint.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = None
        
        # Vex-specific configuration parameters
        self.vex_config = {
            'default_style': 'mirror_universe_pete',
            'quality_preset': 'high_satirical_impact',
            'safety_level': 'corporate_critique_safe',
            'output_format': 'png',
            'resolution': '1024x1024'
        }
        
        # Translation templates for converting our prompts to Vex format
        self.prompt_translation_templates = {
            'contradiction_expose': 'Visual juxtaposition revealing corporate contradiction: {concept}',
            'buzzword_deflation': 'Surreal literal interpretation of corporate buzzword: {concept}',
            'aspiration_mockery': 'Satirical comparison of customer aspiration vs corporate reality: {concept}',
            'authority_undermining': 'Authority figure in ridiculous context: {concept}',
            'scale_absurdity': 'Mass production of supposedly unique experiences: {concept}'
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def generate_satirical_visual(self, generation_request: VexGenerationRequest) -> VexGenerationResult:
        """
        Generate visual satirical content using the Vex agent.
        
        This method handles the complete pipeline from our analytical insights
        to finished visual content. It translates our Pentagram Framework prompts
        into Vex's input format and manages the generation process.
        """
        
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting Vex visual generation for concept: {generation_request.concept_prompt[:100]}...")
            
            # Step 1: Prepare Vex-compatible request
            vex_request = await self._prepare_vex_request(generation_request)
            
            # Step 2: Submit generation request to Vex
            generation_response = await self._submit_to_vex(vex_request)
            
            # Step 3: Handle the generation result
            if generation_response['success']:
                result = await self._process_successful_generation(generation_response)
            else:
                result = VexGenerationResult(
                    success=False,
                    image_data=None,
                    image_url=None,
                    generation_metadata={},
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    error_message=generation_response.get('error', 'Vex generation failed')
                )
            
            logger.info(f"Vex generation completed in {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Vex integration error: {str(e)}")
            
            return VexGenerationResult(
                success=False,
                image_data=None,
                image_url=None,
                generation_metadata={},
                processing_time=processing_time,
                error_message=f"Vex integration error: {str(e)}"
            )
    
    async def _prepare_vex_request(self, request: VexGenerationRequest) -> Dict[str, Any]:
        """
        Transform our brand analysis and satirical concept into Vex-compatible format.
        
        This method acts as the translation layer between our analytical insights
        and Vex's creative generation requirements. It ensures that the rich
        contextual information from our brand analysis enhances the visual generation.
        """
        
        # Extract brand context for enriching the prompt
        brand_context = request.brand_context
        company_name = brand_context.get('company_name', 'Unknown Company')
        positioning = brand_context.get('primary_positioning', 'Generic Brand')
        authenticity_score = brand_context.get('authenticity_score', 0.5)
        
        # Determine the appropriate prompt template based on satirical style
        satirical_style = request.generation_params.get('satirical_style', 'contradiction_expose')
        template = self.prompt_translation_templates.get(satirical_style, 
                                                        self.prompt_translation_templates['contradiction_expose'])
        
        # Create enriched concept prompt for Vex
        enriched_concept = template.format(concept=request.concept_prompt)
        
        # Add brand-specific context
        brand_enrichment = f"""
        Brand Context: {company_name} positions itself as {positioning}
        Authenticity Level: {authenticity_score:.2f} (lower = more vulnerable to satirical critique)
        Satirical Intent: Expose the gap between brand claims and reality
        """
        
        # Combine concept with contextual enrichment
        full_vex_prompt = f"{enriched_concept}\n\nContext for satirical targeting:\n{brand_enrichment}"
        
        # Map our satirical intensity to Vex parameters
        intensity_mapping = {
            'low': {'creativity': 0.6, 'satirical_edge': 'subtle'},
            'medium': {'creativity': 0.7, 'satirical_edge': 'balanced'},
            'high': {'creativity': 0.8, 'satirical_edge': 'sharp'},
            'extreme': {'creativity': 0.9, 'satirical_edge': 'ruthless'}
        }
        
        intensity_params = intensity_mapping.get(request.satirical_intensity, intensity_mapping['medium'])
        
        # Construct complete Vex request
        vex_request = {
            'prompt': full_vex_prompt,
            'style': self.vex_config['default_style'],
            'tone_guidance': request.tone_guidance,
            'generation_parameters': {
                'creativity_level': intensity_params['creativity'],
                'satirical_edge': intensity_params['satirical_edge'],
                'quality_preset': self.vex_config['quality_preset'],
                'safety_level': self.vex_config['safety_level'],
                'output_format': self.vex_config['output_format'],
                'resolution': self.vex_config['resolution']
            },
            'metadata': {
                'source_system': 'brand_deconstruction_engine',
                'brand_analysis_version': '1.0',
                'generation_timestamp': datetime.now().isoformat(),
                'target_company': company_name
            }
        }
        
        return vex_request
    
    async def _submit_to_vex(self, vex_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit the generation request to the Vex agent endpoint.
        
        This method handles the actual HTTP communication with the Vex agent,
        including authentication, request formatting, and response parsing.
        """
        
        if not self.session:
            raise Exception("VexAgentClient not properly initialized. Use async context manager.")
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'BrandDeconstructionEngine/1.0'
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        # Submit request to Vex endpoint
        try:
            async with self.session.post(
                f'{self.vex_endpoint}/generate',
                json=vex_request,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        'success': True,
                        'data': result,
                        'status_code': response.status
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'Vex API error {response.status}: {error_text}',
                        'status_code': response.status
                    }
                    
        except asyncio.TimeoutError:
            return {
                'success': False,
                'error': 'Vex generation timeout',
                'status_code': 408
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'status_code': 0
            }
    
    async def _process_successful_generation(self, response: Dict[str, Any]) -> VexGenerationResult:
        """
        Process a successful generation response from Vex.
        
        This method extracts the generated visual content and metadata,
        handling different response formats that Vex might return.
        """
        
        response_data = response['data']
        
        # Extract image data (could be base64 or URL)
        image_data = None
        image_url = None
        
        if 'image_base64' in response_data:
            image_data = response_data['image_base64']
        elif 'image_url' in response_data:
            image_url = response_data['image_url']
        elif 'image' in response_data:
            # Handle different image response formats
            if response_data['image'].startswith('http'):
                image_url = response_data['image']
            else:
                image_data = response_data['image']
        
        # Extract generation metadata
        generation_metadata = {
            'vex_version': response_data.get('version', 'unknown'),
            'generation_id': response_data.get('generation_id'),
            'processing_time': response_data.get('processing_time', 0),
            'style_applied': response_data.get('style_applied'),
            'quality_metrics': response_data.get('quality_metrics', {}),
            'satirical_effectiveness': response_data.get('satirical_effectiveness', 'unknown')
        }
        
        processing_time = response_data.get('processing_time', 0)
        
        return VexGenerationResult(
            success=True,
            image_data=image_data,
            image_url=image_url,
            generation_metadata=generation_metadata,
            processing_time=processing_time
        )
    
    async def batch_generate_visuals(self, requests: List[VexGenerationRequest]) -> List[VexGenerationResult]:
        """
        Generate multiple visual satirical pieces simultaneously.
        
        This method enables batch processing of multiple satirical concepts,
        useful when creating comprehensive visual campaigns targeting multiple
        brand vulnerabilities or creating variations of the same concept.
        """
        
        logger.info(f"Starting batch visual generation for {len(requests)} concepts")
        
        # Limit concurrent requests to avoid overwhelming Vex
        semaphore = asyncio.Semaphore(3)
        
        async def generate_with_semaphore(request):
            async with semaphore:
                return await self.generate_satirical_visual(request)
        
        # Execute all requests concurrently
        results = await asyncio.gather(
            *[generate_with_semaphore(req) for req in requests],
            return_exceptions=True
        )
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch generation failed for request {i}: {str(result)}")
                processed_results.append(VexGenerationResult(
                    success=False,
                    image_data=None,
                    image_url=None,
                    generation_metadata={},
                    processing_time=0,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        successful_generations = sum(1 for r in processed_results if r.success)
        logger.info(f"Batch generation completed: {successful_generations}/{len(requests)} successful")
        
        return processed_results

# File: integrations/complete_visual_pipeline.py

from typing import Dict, Any, List
from dataclasses import dataclass
import asyncio
import logging

from workflows.brand_deconstruction import (
    CompleteBrandDeconstructionWorkflow, 
    BrandDeconstructionRequest
)
from integrations.vex_client import VexAgentClient, VexGenerationRequest
from agents.satirical_generator import PentagramPrompt

logger = logging.getLogger(__name__)

@dataclass
class CompleteVisualResult:
    """Complete result including both brand analysis and generated visuals"""
    brand_deconstruction: Any  # BrandDeconstructionResult
    visual_generations: List[Any]  # List of VexGenerationResult
    pipeline_metadata: Dict[str, Any]

class CompleteBrandToVisualPipeline:
    """
    Complete pipeline from brand URL to finished visual satirical content.
    
    This class represents the full realization of the Brand Deconstruction Engine
    concept from the original documents. It seamlessly integrates sophisticated
    brand analysis with visual generation to create finished satirical content
    that exposes corporate contradictions through impactful imagery.
    """
    
    def __init__(self, 
                 deconstruction_workflow: CompleteBrandDeconstructionWorkflow,
                 vex_endpoint: str,
                 vex_api_key: str = None):
        self.deconstruction_workflow = deconstruction_workflow
        self.vex_endpoint = vex_endpoint
        self.vex_api_key = vex_api_key
        
        # Pipeline configuration
        self.pipeline_config = {
            'generate_alternatives': True,
            'max_visual_variations': 5,
            'quality_threshold': 0.7,
            'timeout_per_generation': 120
        }
    
    async def execute_complete_pipeline(self, 
                                      url: str,
                                      satirical_intensity: str = 'medium',
                                      style_preference: str = 'contradiction_expose') -> CompleteVisualResult:
        """
        Execute the complete pipeline from URL to finished visual satirical content.
        
        This represents the full "Brand Deconstruction Engine" workflow:
        1. Analyze brand psychology and identify vulnerabilities
        2. Generate targeted satirical prompts using Pentagram Framework  
        3. Transform prompts into finished visual content via Vex
        4. Return complete package of analysis and visuals
        """
        
        pipeline_start = datetime.now()
        
        try:
            logger.info(f"Starting complete brand-to-visual pipeline for: {url}")
            
            # Phase 1: Execute brand deconstruction analysis
            logger.info("Phase 1: Brand deconstruction analysis")
            deconstruction_request = BrandDeconstructionRequest(
                url=url,
                satirical_intensity=satirical_intensity,
                style_preference=style_preference,
                output_variations=3
            )
            
            brand_result = await self.deconstruction_workflow.execute_complete_deconstruction(
                deconstruction_request
            )
            
            if not brand_result.execution_summary.get('success', True):
                raise Exception(f"Brand analysis failed: {brand_result.execution_summary.get('error_message')}")
            
            logger.info(f"Brand analysis completed: {brand_result.brand_analysis.authenticity_score:.2f} authenticity")
            
            # Phase 2: Generate visual content using Vex
            logger.info("Phase 2: Visual content generation")
            visual_results = await self._generate_visuals_from_analysis(brand_result)
            
            # Phase 3: Compile complete results
            pipeline_duration = (datetime.now() - pipeline_start).total_seconds()
            
            complete_result = CompleteVisualResult(
                brand_deconstruction=brand_result,
                visual_generations=visual_results,
                pipeline_metadata={
                    'total_pipeline_time': pipeline_duration,
                    'brand_analysis_time': brand_result.execution_summary.get('total_execution_time', 0),
                    'visual_generation_time': sum(r.processing_time for r in visual_results if r.success),
                    'visuals_generated': len([r for r in visual_results if r.success]),
                    'pipeline_version': '1.0'
                }
            )
            
            logger.info(f"Complete pipeline finished in {pipeline_duration:.2f}s")
            return complete_result
            
        except Exception as e:
            logger.error(f"Complete pipeline failed: {str(e)}")
            raise
    
    async def _generate_visuals_from_analysis(self, brand_result) -> List:
        """
        Transform brand analysis results into visual content using Vex.
        
        This method creates the bridge between our analytical insights and
        visual generation, ensuring that the visual content accurately reflects
        the specific contradictions and vulnerabilities identified in the analysis.
        """
        
        # Prepare brand context for Vex
        brand_context = {
            'company_name': brand_result.scraped_content.metadata.get('company_name') if brand_result.scraped_content else 'Unknown',
            'primary_positioning': brand_result.brand_analysis.primary_positioning if brand_result.brand_analysis else 'Unknown',
            'authenticity_score': brand_result.brand_analysis.authenticity_score if brand_result.brand_analysis else 0.5,
            'target_aspiration': brand_result.brand_analysis.target_audience_aspiration if brand_result.brand_analysis else 'Unknown'
        }
        
        # Create generation requests for primary and alternative prompts
        generation_requests = []
        
        # Primary prompt
        if brand_result.primary_satirical_prompt:
            primary_request = VexGenerationRequest(
                concept_prompt=brand_result.primary_satirical_prompt.compile_full_prompt(),
                tone_guidance=brand_result.primary_satirical_prompt.symbolic_anchoring,
                satirical_intensity=brand_result.request_params.satirical_intensity,
                brand_context=brand_context,
                generation_params={
                    'satirical_style': brand_result.request_params.style_preference,
                    'is_primary': True
                }
            )
            generation_requests.append(primary_request)
        
        # Alternative prompts
        for i, alt_prompt in enumerate(brand_result.alternative_prompts):
            alt_request = VexGenerationRequest(
                concept_prompt=alt_prompt.compile_full_prompt(),
                tone_guidance=alt_prompt.symbolic_anchoring,
                satirical_intensity=brand_result.request_params.satirical_intensity,
                brand_context=brand_context,
                generation_params={
                    'satirical_style': 'alternative_variation',
                    'variation_index': i,
                    'is_primary': False
                }
            )
            generation_requests.append(alt_request)
        
        # Generate visuals using Vex
        async with VexAgentClient(self.vex_endpoint, self.vex_api_key) as vex_client:
            visual_results = await vex_client.batch_generate_visuals(generation_requests)
        
        return visual_results
    
    async def generate_competitive_analysis_visuals(self, 
                                                  competitor_urls: List[str],
                                                  analysis_theme: str = 'industry_contradictions') -> Dict[str, CompleteVisualResult]:
        """
        Generate comparative visual analysis across multiple competitors.
        
        This method enables systematic visual critique of entire industries,
        identifying common patterns of corporate contradiction across competitors
        and creating visual content that exposes industry-wide pretensions.
        """
        
        logger.info(f"Starting competitive visual analysis for {len(competitor_urls)} companies")
        
        # Process all competitors in parallel
        competitor_results = {}
        
        # Limit concurrent processing
        semaphore = asyncio.Semaphore(2)
        
        async def process_competitor(url):
            async with semaphore:
                try:
                    result = await self.execute_complete_pipeline(
                        url, 
                        satirical_intensity='medium',
                        style_preference='contradiction_expose'
                    )
                    return url, result
                except Exception as e:
                    logger.error(f"Competitive analysis failed for {url}: {str(e)}")
                    return url, None
        
        # Execute competitive analysis
        results = await asyncio.gather(
            *[process_competitor(url) for url in competitor_urls],
            return_exceptions=True
        )
        
        # Compile results
        for result in results:
            if not isinstance(result, Exception) and result[1] is not None:
                url, analysis_result = result
                competitor_results[url] = analysis_result
        
        logger.info(f"Competitive analysis completed: {len(competitor_results)}/{len(competitor_urls)} successful")
        return competitor_results

# File: web/visual_api_integration.py

from flask import jsonify, request
import asyncio
from datetime import datetime

# Add these routes to the existing Flask app from Phase 6

@app.route('/api/generate-visuals', methods=['POST'])
async def generate_visuals():
    """
    API endpoint for complete brand-to-visual pipeline.
    
    This endpoint represents the full realization of the Brand Deconstruction Engine,
    taking a URL and returning both analytical insights and finished visual content.
    """
    
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL is required',
                'error_code': 'MISSING_URL'
            }), 400
        
        # Get Vex configuration from request or environment
        vex_endpoint = data.get('vex_endpoint') or os.environ.get('VEX_ENDPOINT')
        vex_api_key = data.get('vex_api_key') or os.environ.get('VEX_API_KEY')
        
        if not vex_endpoint:
            return jsonify({
                'success': False,
                'error': 'Vex endpoint configuration required',
                'error_code': 'MISSING_VEX_CONFIG'
            }), 400
        
        # Create complete pipeline
        from integrations.complete_visual_pipeline import CompleteBrandToVisualPipeline
        
        visual_pipeline = CompleteBrandToVisualPipeline(
            deconstruction_workflow,
            vex_endpoint,
            vex_api_key
        )
        
        # Execute complete pipeline
        result = await visual_pipeline.execute_complete_pipeline(
            url=data['url'],
            satirical_intensity=data.get('satirical_intensity', 'medium'),
            style_preference=data.get('style_preference', 'contradiction_expose')
        )
        
        # Prepare response with both analysis and visuals
        response_data = {
            'success': True,
            'pipeline_metadata': result.pipeline_metadata,
            'brand_analysis': {
                'company_name': result.brand_deconstruction.scraped_content.metadata.get('company_name'),
                'authenticity_score': result.brand_deconstruction.brand_analysis.authenticity_score,
                'vulnerabilities_found': len(result.brand_deconstruction.brand_analysis.satirical_vulnerabilities),
                'primary_positioning': result.brand_deconstruction.brand_analysis.primary_positioning
            },
            'visual_content': [
                {
                    'generation_id': i,
                    'success': visual.success,
                    'image_url': visual.image_url,
                    'image_data': visual.image_data,
                    'generation_metadata': visual.generation_metadata
                }
                for i, visual in enumerate(result.visual_generations)
            ]
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Visual generation API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Visual generation failed',
            'error_code': 'VISUAL_GENERATION_ERROR'
        }), 500

@app.route('/api/competitive-visuals', methods=['POST'])
async def competitive_visual_analysis():
    """
    API endpoint for competitive visual analysis across multiple brands.
    
    This enables systematic visual critique of entire industries or competitive sets.
    """
    
    try:
        data = request.get_json()
        
        if not data or 'urls' not in data:
            return jsonify({
                'success': False,
                'error': 'URLs array is required',
                'error_code': 'MISSING_URLS'
            }), 400
        
        urls = data['urls']
        if len(urls) > 5:  # Reasonable limit for visual generation
            return jsonify({
                'success': False,
                'error': 'Maximum 5 URLs allowed for competitive visual analysis',
                'error_code': 'TOO_MANY_URLS'
            }), 400
        
        # Get Vex configuration
        vex_endpoint = data.get('vex_endpoint') or os.environ.get('VEX_ENDPOINT')
        vex_api_key = data.get('vex_api_key') or os.environ.get('VEX_API_KEY')
        
        if not vex_endpoint:
            return jsonify({
                'success': False,
                'error': 'Vex endpoint configuration required',
                'error_code': 'MISSING_VEX_CONFIG'
            }), 400
        
        # Create visual pipeline
        from integrations.complete_visual_pipeline import CompleteBrandToVisualPipeline
        
        visual_pipeline = CompleteBrandToVisualPipeline(
            deconstruction_workflow,
            vex_endpoint,
            vex_api_key
        )
        
        # Execute competitive analysis
        competitive_results = await visual_pipeline.generate_competitive_analysis_visuals(
            urls,
            analysis_theme=data.get('analysis_theme', 'industry_contradictions')
        )
        
        # Format response
        response_data = {
            'success': True,
            'competitive_analysis': {
                'total_companies': len(urls),
                'successful_analyses': len(competitive_results),
                'results': {
                    url: {
                        'company_name': result.brand_deconstruction.scraped_content.metadata.get('company_name'),
                        'authenticity_score': result.brand_deconstruction.brand_analysis.authenticity_score,
                        'visual_count': len([v for v in result.visual_generations if v.success])
                    }
                    for url, result in competitive_results.items()
                }
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Competitive visual analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Competitive analysis failed',
            'error_code': 'COMPETITIVE_ANALYSIS_ERROR'
        }), 500

# File: examples/test_complete_system.py

import asyncio
import os
from integrations.complete_visual_pipeline import CompleteBrandToVisualPipeline
from core.base_agents import AgentManager
from workflows.brand_deconstruction import CompleteBrandDeconstructionWorkflow

async def test_complete_brand_to_visual_system():
    """
    Test the complete Brand Deconstruction Engine with visual generation.
    
    This represents the full system working together - from corporate URL
    to finished visual satirical content that exposes brand contradictions.
    """
    
    print("🎯 Testing Complete Brand Deconstruction Engine with Visual Generation")
    print("=" * 70)
    
    # Initialize complete system
    agent_manager = AgentManager()
    deconstruction_workflow = CompleteBrandDeconstructionWorkflow(agent_manager)
    
    # Configure Vex integration (replace with actual endpoint)
    vex_endpoint = os.environ.get('VEX_ENDPOINT', 'https://your-vex-agent-endpoint.com')
    vex_api_key = os.environ.get('VEX_API_KEY', 'your-vex-api-key')
    
    visual_pipeline = CompleteBrandToVisualPipeline(
        deconstruction_workflow,
        vex_endpoint,
        vex_api_key
    )
    
    # Test with a corporate website known for contradictions
    test_url = 'https://www.salesforce.com'
    
    try:
        print(f"🚀 Processing: {test_url}")
        print("📊 Stage 1: Brand analysis...")
        
        # Execute complete pipeline
        result = await visual_pipeline.execute_complete_pipeline(
            url=test_url,
            satirical_intensity='high',
            style_preference='contradiction_expose'
        )
        
        print("✅ Complete pipeline executed successfully!")
        print(f"⏱️  Total time: {result.pipeline_metadata['total_pipeline_time']:.2f}s")
        print(f"🏢 Company: {result.brand_deconstruction.scraped_content.metadata.get('company_name')}")
        print(f"📈 Authenticity Score: {result.brand_deconstruction.brand_analysis.authenticity_score:.2f}")
        print(f"🎨 Visuals Generated: {result.pipeline_metadata['visuals_generated']}")
        
        # Display visual generation results
        print(f"\n🖼️  Visual Generation Results:")
        for i, visual in enumerate(result.visual_generations):
            if visual.success:
                print(f"   ✅ Visual {i+1}: Generated in {visual.processing_time:.2f}s")
                if visual.image_url:
                    print(f"      URL: {visual.image_url}")
                if visual.generation_metadata.get('satirical_effectiveness'):
                    print(f"      Satirical Effectiveness: {visual.generation_metadata['satirical_effectiveness']}")
            else:
                print(f"   ❌ Visual {i+1}: {visual.error_message}")
        
        # Show primary satirical target
        if result.brand_deconstruction.brand_analysis.satirical_vulnerabilities:
            print(f"\n🎯 Primary Satirical Target:")
            print(f"   {result.brand_deconstruction.brand_analysis.satirical_vulnerabilities[0]}")
        
        print(f"\n🎨 Primary Visual Prompt Applied:")
        if result.brand_deconstruction.primary_satirical_prompt:
            print(f"   {result.brand_deconstruction.primary_satirical_prompt.compile_full_prompt()}")
        
    except Exception as e:
        print(f"❌ Complete system test failed: {str(e)}")
        print("💡 Make sure Vex endpoint is configured correctly")

async def test_competitive_visual_analysis():
    """Test competitive analysis with visual generation"""
    
    print(f"\n🏆 Testing Competitive Visual Analysis")
    print("=" * 40)
    
    # Test URLs (replace with actual competitors)
    competitor_urls = [
        'https://www.salesforce.com',
        'https://www.hubspot.com',
        'https://www.zendesk.com'
    ]
    
    # This would run if properly configured
    print(f"📊 Would analyze {len(competitor_urls)} competitors")
    print("💡 Configure VEX_ENDPOINT and VEX_API_KEY environment variables to run")

if __name__ == "__main__":
    # Check for Vex configuration
    if not os.environ.get('VEX_ENDPOINT'):
        print("⚠️  VEX_ENDPOINT environment variable not set")
        print("💡 Set VEX_ENDPOINT=https://your-vex-agent-endpoint.com")
        print("💡 Set VEX_API_KEY=your-vex-api-key")
        print("🧪 Running analysis-only test instead...\n")
        
        # Run analysis-only version
        asyncio.run(test_complete_brand_to_visual_system())
    else:
        # Run complete system test
        asyncio.run(test_complete_brand_to_visual_system())
        asyncio.run(test_competitive_visual_analysis())