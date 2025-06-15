# File: integrations/enhanced_visual_pipeline.py

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio
import logging
import time
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.gpt4o_visual_client import GPT4oVisualClient, GPT4oVisualRequest
from integrations.sora_client import SoraClient, SoraGenerationRequest

logger = logging.getLogger(__name__)

@dataclass
class BrandDeconstructionRequest:
    """Request structure for brand deconstruction"""
    url: str
    satirical_intensity: str = "medium"
    style_preference: str = "contradiction_expose"

@dataclass
class EnhancedVisualPipelineResult:
    """Complete result from brand analysis to advanced visual content"""
    success: bool
    brand_deconstruction: Any
    gpt4o_concepts: List[Any]
    sora_videos: List[Any]  # When available
    composite_instructions: List[Any]
    pipeline_metadata: Dict[str, Any]
    total_processing_time: float
    error_message: Optional[str] = None

class EnhancedVisualPipeline:
    """
    Next-generation visual pipeline using GPT-4o and Sora.
    
    This pipeline creates sophisticated visual concepts and instructions
    that go far beyond simple image generation, providing detailed
    creative direction for producing impactful satirical content.
    """
    
    def __init__(self, deconstruction_workflow=None,
                 openai_api_key: str = None, 
                 enable_sora: bool = True):
        self.deconstruction_workflow = deconstruction_workflow
        
        # Get API key from environment if not provided
        api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")
        
        self.gpt4o_client = GPT4oVisualClient(api_key=api_key)
        self.sora_client = SoraClient(api_key=api_key) if enable_sora else None
    
    async def execute_enhanced_pipeline(self, url: str, 
                                      visual_approaches: List[str] = None,
                                      include_video: bool = True) -> EnhancedVisualPipelineResult:
        """
        Execute the complete enhanced visual pipeline.
        
        Creates multiple sophisticated visual concepts using GPT-4o's advanced
        reasoning, including video storyboards for Sora generation.
        """
        
        start_time = time.time()
        visual_approaches = visual_approaches or ['satirical_visual_analysis', 'composite_design']
        
        if include_video and self.sora_client:
            visual_approaches.append('sora_storyboard')
        
        try:
            logger.info(f"Starting enhanced visual pipeline for: {url}")
            
            # Phase 1: Mock brand deconstruction for now (replace with actual workflow when available)
            brand_result = await self._mock_brand_deconstruction(url)
            
            if not brand_result.get('success', False):
                return EnhancedVisualPipelineResult(
                    success=False,
                    brand_deconstruction=brand_result,
                    gpt4o_concepts=[],
                    sora_videos=[],
                    composite_instructions=[],
                    pipeline_metadata={},
                    total_processing_time=time.time() - start_time,
                    error_message=f"Brand deconstruction failed: {brand_result.get('error_message', 'Unknown error')}"
                )
            
            # Phase 2: GPT-4o visual concept development
            gpt4o_concepts = []
            sora_videos = []
            composite_instructions = []
            
            for approach in visual_approaches:
                concept_request = GPT4oVisualRequest(
                    pentagram_prompt=brand_result['satirical_prompts']['primary_prompt'],
                    brand_context={
                        'brand_name': brand_result['brand_analysis']['brand_name'],
                        'authenticity_score': brand_result['brand_analysis']['authenticity_score'],
                        'satirical_vulnerabilities': brand_result['brand_analysis']['satirical_vulnerabilities'],
                        'primary_positioning': brand_result['brand_analysis']['primary_positioning']
                    },
                    analysis_mode=approach,
                    visual_style="professional_satirical"
                )
                
                concept_result = await self.gpt4o_client.analyze_and_conceptualize(concept_request)
                
                if concept_result.success:
                    gpt4o_concepts.append(concept_result)
                    
                    # If this was a storyboard, attempt Sora generation
                    if approach == 'sora_storyboard' and concept_result.sora_storyboard and self.sora_client:
                        sora_request = SoraGenerationRequest(
                            storyboard=concept_result.sora_storyboard,
                            video_concept=concept_result.visual_concept,
                            duration=15,
                            style="professional_satirical"
                        )
                        
                        sora_result = await self.sora_client.generate_satirical_video(sora_request)
                        sora_videos.append(sora_result)
                    
                    # If this was composite design, save instructions
                    if approach == 'composite_design':
                        composite_instructions.append(concept_result)
            
            total_processing_time = time.time() - start_time
            
            pipeline_metadata = {
                'pipeline_version': '2.0_gpt4o_enhanced',
                'brand_analysis_time': brand_result.get('total_processing_time', 0),
                'gpt4o_concepts_generated': len(gpt4o_concepts),
                'sora_videos_attempted': len(sora_videos),
                'composite_designs_created': len(composite_instructions),
                'total_processing_time': total_processing_time,
                'visual_approaches_used': visual_approaches
            }
            
            successful_concepts = sum(1 for c in gpt4o_concepts if c.success)
            logger.info(f"Enhanced pipeline completed: {successful_concepts}/{len(gpt4o_concepts)} concepts generated in {total_processing_time:.2f}s")
            
            return EnhancedVisualPipelineResult(
                success=True,
                brand_deconstruction=brand_result,
                gpt4o_concepts=gpt4o_concepts,
                sora_videos=sora_videos,
                composite_instructions=composite_instructions,
                pipeline_metadata=pipeline_metadata,
                total_processing_time=total_processing_time
            )
            
        except Exception as e:
            logger.error(f"Enhanced visual pipeline error: {str(e)}")
            return EnhancedVisualPipelineResult(
                success=False,
                brand_deconstruction=None,
                gpt4o_concepts=[],
                sora_videos=[],
                composite_instructions=[],
                pipeline_metadata={},
                total_processing_time=time.time() - start_time,
                error_message=f"Pipeline error: {str(e)}"
            )
    
    async def _mock_brand_deconstruction(self, url: str) -> Dict[str, Any]:
        """
        Mock brand deconstruction for testing purposes.
        Replace this with actual brand deconstruction workflow when available.
        """
        
        # Extract domain name for mock analysis
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace('www.', '')
        company_name = domain.split('.')[0].title()
        
        return {
            'success': True,
            'brand_analysis': {
                'brand_name': company_name,
                'authenticity_score': 0.3,  # Low authenticity for satirical purposes
                'satirical_vulnerabilities': [
                    'Corporate buzzword overuse',
                    'Authenticity vs scale contradiction',
                    'Innovation claims vs conventional practices'
                ],
                'primary_positioning': f'{company_name} positions itself as an innovative, customer-centric solution provider'
            },
            'satirical_prompts': {
                'primary_prompt': f'''
                Intent Clarity: Expose the gap between {company_name}'s innovation claims and corporate conformity
                Fidelity Pass: High-resolution corporate photography style with ironic visual elements
                Symbolic Anchoring: Corporate boardroom setting with employees in identical poses claiming "uniqueness"
                Environmental Context: Sterile office environment with motivational posters about "disruption"
                Brand World Constraints: Avoid direct logo usage, focus on archetypal corporate imagery
                '''
            },
            'total_processing_time': 2.5
        }
