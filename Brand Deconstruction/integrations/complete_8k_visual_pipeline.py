# File: integrations/complete_8k_visual_pipeline.py

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio
import logging
import time
import json
import base64
from datetime import datetime

from workflows.brand_deconstruction import CompleteBrandDeconstructionWorkflow, BrandDeconstructionRequest
from integrations.pure_gpt4o_8k_client import PureGPT4o8KClient, Pure8KVisualRequest
from integrations.gpt_image_1_client import GPTImage1Client, GPTImage1Request

logger = logging.getLogger(__name__)

@dataclass
class Complete8KVisualPipelineResult:
    """Complete result from brand analysis to final 8K images"""
    success: bool
    brand_deconstruction: Any
    concept_development: Any
    generated_images: List[Any]
    pipeline_metadata: Dict[str, Any]
    total_processing_time: float
    error_message: Optional[str] = None

class Complete8KVisualPipeline:
    """
    Complete pipeline: Brand Analysis → GPT-4o Concepts → gpt-image-1 Generation.
    
    This pipeline combines the sophisticated concept development of GPT-4o
    with the high-quality image generation of gpt-image-1 to create
    professional satirical visuals that expose corporate contradictions.
    """
    
    def __init__(self, deconstruction_workflow: CompleteBrandDeconstructionWorkflow,
                 openai_api_key: str):
        self.deconstruction_workflow = deconstruction_workflow
        self.gpt4o_client = PureGPT4o8KClient(api_key=openai_api_key)
        self.gpt_image_1_client = GPTImage1Client(api_key=openai_api_key)
    
    async def execute_complete_pipeline(self, url: str,
                                      concept_modes: List[str] = None,
                                      generate_variations: bool = True,
                                      image_config: Dict[str, Any] = None) -> Complete8KVisualPipelineResult:
        """
        Execute the complete 8K visual pipeline.
        
        Phase 1: Brand Deconstruction
        Phase 2: GPT-4o Concept Development  
        Phase 3: gpt-image-1 Image Generation
        """
        
        start_time = time.time()
        concept_modes = concept_modes or ['8k_concept_development', 'technical_specifications']
        image_config = image_config or {}
        
        try:
            logger.info(f"Starting complete 8K visual pipeline for: {url}")
            
            # Phase 1: Brand Deconstruction
            brand_request = BrandDeconstructionRequest(
                url=url,
                satirical_intensity="high",
                style_preference="contradiction_expose"
            )
            
            brand_result = await self.deconstruction_workflow.execute_complete_deconstruction(brand_request)
            
            if not brand_result.success:
                return Complete8KVisualPipelineResult(
                    success=False,
                    brand_deconstruction=brand_result,
                    concept_development=None,
                    generated_images=[],
                    pipeline_metadata={},
                    total_processing_time=time.time() - start_time,
                    error_message=f"Brand deconstruction failed: {brand_result.error_message}"
                )
            
            # Phase 2: GPT-4o Concept Development
            concept_development = await self._develop_visual_concepts(brand_result, concept_modes)
            
            if not concept_development['success']:
                return Complete8KVisualPipelineResult(
                    success=False,
                    brand_deconstruction=brand_result,
                    concept_development=concept_development,
                    generated_images=[],
                    pipeline_metadata={},
                    total_processing_time=time.time() - start_time,
                    error_message=f"Concept development failed: {concept_development['error']}"
                )
            
            # Phase 3: gpt-image-1 Image Generation
            generated_images = await self._generate_images_from_concepts(
                concept_development, 
                brand_result,
                image_config,
                generate_variations
            )
            
            total_processing_time = time.time() - start_time
            
            # Compile pipeline metadata
            pipeline_metadata = {
                'pipeline_version': '3.0_complete_8k_visual',
                'brand_analysis_time': brand_result.total_processing_time,
                'concept_development_time': concept_development['processing_time'],
                'image_generation_time': sum(img.processing_time for img in generated_images if img.success),
                'total_processing_time': total_processing_time,
                'concepts_developed': len(concept_development['concepts']),
                'images_generated': len(generated_images),
                'successful_generations': sum(1 for img in generated_images if img.success),
                'gpt4o_model': 'gpt-4o',
                'image_model': 'gpt-image-1',
                'concept_modes_used': concept_modes
            }
            
            successful_images = sum(1 for img in generated_images if img.success)
            logger.info(f"Complete 8K pipeline completed: {successful_images}/{len(generated_images)} images generated in {total_processing_time:.2f}s")
            
            return Complete8KVisualPipelineResult(
                success=True,
                brand_deconstruction=brand_result,
                concept_development=concept_development,
                generated_images=generated_images,
                pipeline_metadata=pipeline_metadata,
                total_processing_time=total_processing_time
            )
            
        except Exception as e:
            logger.error(f"Complete 8K visual pipeline error: {str(e)}")
            return Complete8KVisualPipelineResult(
                success=False,
                brand_deconstruction=None,
                concept_development=None,
                generated_images=[],
                pipeline_metadata={},
                total_processing_time=time.time() - start_time,
                error_message=f"Pipeline error: {str(e)}"
            )
    
    async def _develop_visual_concepts(self, brand_result: Any, concept_modes: List[str]) -> Dict[str, Any]:
        """Use GPT-4o to develop sophisticated visual concepts."""
        
        start_time = time.time()
        concepts = []
        
        try:
            for mode in concept_modes:
                concept_request = Pure8KVisualRequest(
                    pentagram_prompt=brand_result.satirical_prompts['primary_prompt'].compile_full_prompt(),
                    brand_context={
                        'brand_name': brand_result.brand_analysis.brand_name,
                        'authenticity_score': brand_result.brand_analysis.authenticity_score,
                        'satirical_vulnerabilities': brand_result.brand_analysis.satirical_vulnerabilities,
                        'primary_positioning': brand_result.brand_analysis.primary_positioning
                    },
                    analysis_mode=mode,
                    visual_style="professional_satirical_8k",
                    resolution_target="8k_uhd"
                )
                
                concept_result = await self.gpt4o_client.develop_8k_concept(concept_request)
                
                if concept_result.success:
                    concepts.append(concept_result)
                else:
                    logger.warning(f"Concept development failed for mode {mode}: {concept_result.error_message}")
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'concepts': concepts,
                'processing_time': processing_time,
                'modes_completed': len(concepts),
                'modes_requested': len(concept_modes)
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                'success': False,
                'concepts': concepts,
                'processing_time': processing_time,
                'error': str(e)
            }
    
    async def _generate_images_from_concepts(self, concept_development: Dict[str, Any], 
                                           brand_result: Any,
                                           image_config: Dict[str, Any],
                                           generate_variations: bool) -> List[Any]:
        """Generate actual images using gpt-image-1 from GPT-4o concepts."""
        
        concepts = concept_development['concepts']
        image_requests = []
        
        # Create image generation requests from each concept
        for concept in concepts:
            if not concept.success:
                continue
            
            # Primary image request
            primary_request = GPTImage1Request(
                optimized_prompt=concept.visual_concept,
                brand_context={
                    'brand_name': brand_result.brand_analysis.brand_name,
                    'authenticity_score': brand_result.brand_analysis.authenticity_score,
                    'satirical_vulnerabilities': brand_result.brand_analysis.satirical_vulnerabilities
                },
                technical_specifications=concept.technical_specifications or {},
                generation_config={
                    **image_config,
                    'size': '1536x1024',  # High resolution landscape
                    'quality': 'high',
                    'output_format': 'png',
                    'output_compression': 95
                }
            )
            image_requests.append(primary_request)
            
            # Generate variations if requested
            if generate_variations and concept.alternative_concepts:
                for i, alt_concept in enumerate(concept.alternative_concepts[:2]):  # Limit to 2 variations
                    alt_prompt = alt_concept if isinstance(alt_concept, str) else alt_concept.get('concept_description', str(alt_concept))
                    variation_request = GPTImage1Request(
                        optimized_prompt=alt_prompt,
                        brand_context=primary_request.brand_context,
                        technical_specifications=primary_request.technical_specifications,
                        generation_config={
                            **primary_request.generation_config,
                            'size': '1024x1024' if i % 2 == 0 else '1536x1024'  # Mix of square and landscape
                        }
                    )
                    image_requests.append(variation_request)
        
        # Generate all images
        if image_requests:
            generated_images = await self.gpt_image_1_client.batch_generate_images(image_requests)
        else:
            generated_images = []
        
        return generated_images
    
    async def save_generated_images(self, pipeline_result: Complete8KVisualPipelineResult, 
                                  output_directory: str = "generated_images") -> Dict[str, Any]:
        """Save generated images to files with metadata."""
        
        import os
        from pathlib import Path
        
        # Create output directory
        output_path = Path(output_directory)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        brand_name = pipeline_result.brand_deconstruction.brand_analysis.brand_name
        brand_safe_name = brand_name.lower().replace(' ', '_').replace('.', '_')
        
        for i, image_result in enumerate(pipeline_result.generated_images):
            if not image_result.success or not image_result.image_data:
                continue
            
            try:
                # Decode base64 image data
                image_data = base64.b64decode(image_result.image_data)
                
                # Create filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{brand_safe_name}_satirical_{i+1}_{timestamp}.png"
                filepath = output_path / filename
                
                # Save image
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                # Save metadata
                metadata_filename = f"{brand_safe_name}_satirical_{i+1}_{timestamp}_metadata.json"
                metadata_filepath = output_path / metadata_filename
                
                metadata = {
                    'image_filename': filename,
                    'generation_metadata': image_result.generation_metadata,
                    'image_specs': image_result.image_specs,
                    'brand_context': {
                        'brand_name': brand_name,
                        'authenticity_score': pipeline_result.brand_deconstruction.brand_analysis.authenticity_score,
                        'satirical_vulnerabilities': pipeline_result.brand_deconstruction.brand_analysis.satirical_vulnerabilities
                    },
                    'pipeline_metadata': pipeline_result.pipeline_metadata
                }
                
                with open(metadata_filepath, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                saved_files.append({
                    'image_file': str(filepath),
                    'metadata_file': str(metadata_filepath),
                    'file_size': len(image_data),
                    'image_specs': image_result.image_specs
                })
                
            except Exception as e:
                logger.error(f"Failed to save image {i}: {str(e)}")
        
        return {
            'success': True,
            'saved_files': saved_files,
            'total_images_saved': len(saved_files),
            'output_directory': str(output_path),
            'brand_name': brand_name
        }
