# File: integrations/pure_8k_concept_pipeline.py

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio
import logging
import time

from workflows.brand_deconstruction import CompleteBrandDeconstructionWorkflow, BrandDeconstructionRequest
from integrations.pure_gpt4o_8k_client import PureGPT4o8KClient, Pure8KVisualRequest

logger = logging.getLogger(__name__)

@dataclass
class Pure8KConceptPipelineResult:
    """Complete result from brand analysis to 8K visual concept development"""
    success: bool
    brand_deconstruction: Any
    concept_developments: List[Any]
    technical_specifications: List[Any]
    creative_directions: List[Any]
    implementation_guides: List[Any]
    pipeline_metadata: Dict[str, Any]
    total_processing_time: float
    error_message: Optional[str] = None

class Pure8KConceptPipeline:
    """
    Pure GPT-4o pipeline for 8K visual concept development.
    
    This pipeline creates comprehensive visual concepts, technical specifications,
    creative direction, and implementation guidance without any image generation.
    Perfect for creating detailed briefs for manual creation or other tools.
    """
    
    def __init__(self, deconstruction_workflow: CompleteBrandDeconstructionWorkflow,
                 openai_api_key: str):
        self.deconstruction_workflow = deconstruction_workflow
        self.gpt4o_client = PureGPT4o8KClient(api_key=openai_api_key)
    
    async def execute_concept_pipeline(self, url: str, 
                                     analysis_modes: List[str] = None,
                                     include_alternatives: bool = True) -> Pure8KConceptPipelineResult:
        """
        Execute complete pipeline: URL → Brand Analysis → 8K Visual Concepts.
        
        Creates comprehensive visual concepts using only GPT-4o's advanced reasoning.
        """
        
        start_time = time.time()
        analysis_modes = analysis_modes or [
            '8k_concept_development',
            'technical_specifications', 
            'creative_direction',
            'implementation_guide'
        ]
        
        try:
            logger.info(f"Starting pure 8K concept pipeline for: {url}")
            
            # Phase 1: Brand deconstruction (unchanged)
            brand_request = BrandDeconstructionRequest(
                url=url,
                satirical_intensity="high",
                style_preference="contradiction_expose"
            )
            
            brand_result = await self.deconstruction_workflow.execute_complete_deconstruction(brand_request)
            
            if not brand_result.success:
                return Pure8KConceptPipelineResult(
                    success=False,
                    brand_deconstruction=brand_result,
                    concept_developments=[],
                    technical_specifications=[],
                    creative_directions=[],
                    implementation_guides=[],
                    pipeline_metadata={},
                    total_processing_time=time.time() - start_time,
                    error_message=f"Brand deconstruction failed: {brand_result.error_message}"
                )
            
            # Phase 2: GPT-4o 8K concept development
            concept_requests = self._prepare_concept_requests(brand_result, analysis_modes, include_alternatives)
            concept_results = await self.gpt4o_client.batch_develop_concepts(concept_requests)
            
            # Phase 3: Organize results by type
            concept_developments = []
            technical_specifications = []
            creative_directions = []
            implementation_guides = []
            
            for result in concept_results:
                if result.success:
                    # Determine result type based on content
                    if result.concept_title and result.alternative_concepts:
                        concept_developments.append(result)
                    elif result.technical_specifications:
                        technical_specifications.append(result)
                    elif result.creative_direction:
                        creative_directions.append(result)
                    elif result.implementation_steps:
                        implementation_guides.append(result)
                    else:
                        concept_developments.append(result)  # Default category
            
            total_processing_time = time.time() - start_time
            
            pipeline_metadata = {
                'pipeline_version': '3.0_pure_gpt4o_8k',
                'brand_analysis_time': brand_result.total_processing_time,
                'concept_development_time': total_processing_time - brand_result.total_processing_time,
                'total_concepts_developed': len(concept_developments),
                'technical_specs_created': len(technical_specifications),
                'creative_directions_provided': len(creative_directions),
                'implementation_guides_generated': len(implementation_guides),
                'total_processing_time': total_processing_time,
                'analysis_modes_used': analysis_modes,
                'gpt4o_model': self.gpt4o_client.model
            }
            
            successful_concepts = sum(1 for r in concept_results if r.success)
            logger.info(f"Pure 8K concept pipeline completed: {successful_concepts}/{len(concept_results)} concepts developed in {total_processing_time:.2f}s")
            
            return Pure8KConceptPipelineResult(
                success=True,
                brand_deconstruction=brand_result,
                concept_developments=concept_developments,
                technical_specifications=technical_specifications,
                creative_directions=creative_directions,
                implementation_guides=implementation_guides,
                pipeline_metadata=pipeline_metadata,
                total_processing_time=total_processing_time
            )
            
        except Exception as e:
            logger.error(f"Pure 8K concept pipeline error: {str(e)}")
            return Pure8KConceptPipelineResult(
                success=False,
                brand_deconstruction=None,
                concept_developments=[],
                technical_specifications=[],
                creative_directions=[],
                implementation_guides=[],
                pipeline_metadata={},
                total_processing_time=time.time() - start_time,
                error_message=f"Pipeline error: {str(e)}"
            )
    
    def _prepare_concept_requests(self, brand_result: Any, analysis_modes: List[str], 
                                include_alternatives: bool) -> List[Pure8KVisualRequest]:
        """Convert brand analysis into 8K concept development requests."""
        
        satirical_result = brand_result.satirical_prompts
        primary_prompt = satirical_result['primary_prompt']
        
        brand_context = {
            'brand_name': brand_result.brand_analysis.brand_name,
            'authenticity_score': brand_result.brand_analysis.authenticity_score,
            'satirical_vulnerabilities': brand_result.brand_analysis.satirical_vulnerabilities,
            'primary_positioning': brand_result.brand_analysis.primary_positioning,
            'brand_keywords': getattr(brand_result.brand_analysis, 'brand_keywords', []),
            'contradiction_themes': [vuln.get('theme', '') for vuln in brand_result.brand_analysis.satirical_vulnerabilities if isinstance(vuln, dict)]
        }
        
        requests = []
        
        # Create requests for each analysis mode
        for mode in analysis_modes:
            request = Pure8KVisualRequest(
                pentagram_prompt=primary_prompt.compile_full_prompt(),
                brand_context=brand_context,
                analysis_mode=mode,
                visual_style="professional_satirical_8k",
                resolution_target="8k_uhd",
                output_depth="comprehensive"
            )
            requests.append(request)
        
        # Add alternative concept variations if requested
        if include_alternatives and 'alternative_variations' in satirical_result:
            for i, alt_prompt in enumerate(satirical_result['alternative_variations'][:2]):  # Limit alternatives
                alt_request = Pure8KVisualRequest(
                    pentagram_prompt=alt_prompt.compile_full_prompt(),
                    brand_context=brand_context,
                    analysis_mode='8k_concept_development',
                    visual_style="professional_satirical_8k_alternative",
                    resolution_target="8k_uhd",
                    output_depth="comprehensive"
                )
                requests.append(alt_request)
        
        return requests
    
    async def export_concept_portfolio(self, result: Pure8KConceptPipelineResult, 
                                     output_format: str = "comprehensive") -> Dict[str, Any]:
        """
        Export the complete concept development portfolio in various formats.
        
        This method creates a comprehensive portfolio of all developed concepts,
        specifications, and guidance for use by designers, artists, or other tools.
        """
        
        if not result.success:
            return {
                'success': False,
                'error': result.error_message
            }
        
        try:
            portfolio = {
                'project_overview': {
                    'target_brand': result.brand_deconstruction.brand_analysis.brand_name,
                    'authenticity_score': result.brand_deconstruction.brand_analysis.authenticity_score,
                    'satirical_vulnerabilities': result.brand_deconstruction.brand_analysis.satirical_vulnerabilities,
                    'creation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'pipeline_version': result.pipeline_metadata.get('pipeline_version'),
                    'total_concepts': len(result.concept_developments)
                },
                
                'visual_concepts': [
                    {
                        'concept_id': i + 1,
                        'title': concept.concept_title,
                        'core_concept': concept.visual_concept,
                        'detailed_breakdown': concept.detailed_breakdown,
                        'satirical_strategy': concept.satirical_strategy,
                        'alternative_approaches': concept.alternative_concepts,
                        'quality_benchmarks': concept.quality_benchmarks,
                        'processing_time': concept.processing_time
                    }
                    for i, concept in enumerate(result.concept_developments)
                ],
                
                'technical_specifications': [
                    {
                        'spec_id': i + 1,
                        'overview': spec.visual_concept,
                        'detailed_specs': spec.technical_specifications,
                        'implementation_notes': spec.detailed_breakdown
                    }
                    for i, spec in enumerate(result.technical_specifications)
                ],
                
                'creative_directions': [
                    {
                        'direction_id': i + 1,
                        'creative_vision': direction.visual_concept,
                        'artistic_guidance': direction.creative_direction,
                        'satirical_approach': direction.satirical_strategy
                    }
                    for i, direction in enumerate(result.creative_directions)
                ],
                
                'implementation_guides': [
                    {
                        'guide_id': i + 1,
                        'overview': guide.visual_concept,
                        'step_by_step': guide.implementation_steps,
                        'technical_setup': guide.technical_specifications,
                        'quality_assurance': guide.quality_benchmarks
                    }
                    for i, guide in enumerate(result.implementation_guides)
                ],
                
                'execution_summary': {
                    'ready_for_production': len(result.concept_developments) > 0,
                    'technical_specs_available': len(result.technical_specifications) > 0,
                    'creative_direction_provided': len(result.creative_directions) > 0,
                    'implementation_guides_ready': len(result.implementation_guides) > 0,
                    'recommended_next_steps': self._generate_next_steps(result),
                    'estimated_production_time': self._estimate_production_time(result)
                }
            }
            
            return {
                'success': True,
                'portfolio': portfolio,
                'export_format': output_format,
                'total_size': len(str(portfolio))
            }
            
        except Exception as e:
            logger.error(f"Portfolio export error: {str(e)}")
            return {
                'success': False,
                'error': f"Portfolio export failed: {str(e)}"
            }
    
    def _generate_next_steps(self, result: Pure8KConceptPipelineResult) -> List[str]:
        """Generate recommended next steps based on available concepts and specifications."""
        
        next_steps = []
        
        if result.concept_developments:
            next_steps.append("Review and select primary visual concept from developed options")
        
        if result.technical_specifications:
            next_steps.append("Set up production environment according to technical specifications")
        
        if result.creative_directions:
            next_steps.append("Align creative team with provided artistic direction")
        
        if result.implementation_guides:
            next_steps.append("Begin production following step-by-step implementation guides")
        
        next_steps.extend([
            "Gather required assets and resources identified in concepts",
            "Create initial mockups or prototypes based on specifications",
            "Test concepts with target audience for satirical effectiveness",
            "Refine concepts based on feedback and technical constraints",
            "Proceed with full 8K production implementation"
        ])
        
        return next_steps
    
    def _estimate_production_time(self, result: Pure8KConceptPipelineResult) -> Dict[str, str]:
        """Estimate production time based on concept complexity."""
        
        concept_count = len(result.concept_developments)
        has_detailed_specs = len(result.technical_specifications) > 0
        has_implementation_guide = len(result.implementation_guides) > 0
        
        if concept_count == 0:
            return {"estimate": "Cannot estimate - no concepts developed"}
        
        base_time = "2-3 days" if concept_count == 1 else f"{concept_count * 2}-{concept_count * 3} days"
        
        if has_detailed_specs and has_implementation_guide:
            efficiency = "Highly efficient with complete guidance"
        elif has_detailed_specs or has_implementation_guide:
            efficiency = "Efficient with partial guidance"
        else:
            efficiency = "Additional planning time required"
        
        return {
            "estimated_time": base_time,
            "efficiency_note": efficiency,
            "factors": "Based on concept complexity and available guidance"
        }
