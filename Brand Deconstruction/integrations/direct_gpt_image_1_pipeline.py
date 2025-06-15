# File: integrations/direct_gpt_image_1_pipeline.py

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio
import logging
import time
import json
import base64
from datetime import datetime

from workflows.brand_deconstruction import CompleteBrandDeconstructionWorkflow, BrandDeconstructionRequest
from integrations.gpt_image_1_client import GPTImage1Client, GPTImage1Request

logger = logging.getLogger(__name__)

@dataclass
class DirectGPTImage1PipelineResult:
    """Result from brand analysis directly to gpt-image-1 generation"""
    success: bool
    brand_deconstruction: Any
    generated_images: List[Any]
    pipeline_metadata: Dict[str, Any]
    total_processing_time: float
    error_message: Optional[str] = None

class DirectGPTImage1Pipeline:
    """
    Simplified pipeline: Brand Analysis → Direct gpt-image-1 Generation.
    
    This pipeline takes brand analysis results and creates sophisticated
    prompts directly for gpt-image-1, eliminating the GPT-4o conceptual layer.
    """
    
    def __init__(self, deconstruction_workflow: CompleteBrandDeconstructionWorkflow,
                 openai_api_key: str):
        self.deconstruction_workflow = deconstruction_workflow
        self.gpt_image_1_client = GPTImage1Client(api_key=openai_api_key)
    
    async def execute_direct_pipeline(self, url: str,
                                    image_variations: int = 3,
                                    image_config: Dict[str, Any] = None) -> DirectGPTImage1PipelineResult:
        """
        Execute the direct gpt-image-1 pipeline.
        
        Phase 1: Brand Deconstruction
        Phase 2: Direct gpt-image-1 Generation with sophisticated prompts
        """
        
        start_time = time.time()
        image_config = image_config or {}
        
        try:
            logger.info(f"Starting direct gpt-image-1 pipeline for: {url}")
            
            # Phase 1: Brand Deconstruction
            brand_request = BrandDeconstructionRequest(
                url=url,
                satirical_intensity="high",
                style_preference="contradiction_expose"
            )
            
            brand_result = await self.deconstruction_workflow.execute_complete_deconstruction(brand_request)
            
            if not brand_result.success:
                return DirectGPTImage1PipelineResult(
                    success=False,
                    brand_deconstruction=brand_result,
                    generated_images=[],
                    pipeline_metadata={},
                    total_processing_time=time.time() - start_time,
                    error_message=f"Brand deconstruction failed: {brand_result.error_message}"
                )
            
            # Phase 2: Direct gpt-image-1 Generation
            generated_images = await self._generate_images_directly(
                brand_result,
                image_variations,
                image_config
            )
            
            total_processing_time = time.time() - start_time
            
            # Compile pipeline metadata
            pipeline_metadata = {
                'pipeline_version': '3.0_direct_gpt_image_1',
                'brand_analysis_time': brand_result.total_processing_time,
                'image_generation_time': sum(img.processing_time for img in generated_images if img.success),
                'total_processing_time': total_processing_time,
                'images_generated': len(generated_images),
                'successful_generations': sum(1 for img in generated_images if img.success),
                'image_model': 'gpt-image-1',
                'prompt_strategy': 'direct_from_brand_analysis',
                'variations_requested': image_variations
            }
            
            successful_images = sum(1 for img in generated_images if img.success)
            logger.info(f"Direct gpt-image-1 pipeline completed: {successful_images}/{len(generated_images)} images generated in {total_processing_time:.2f}s")
            
            return DirectGPTImage1PipelineResult(
                success=True,
                brand_deconstruction=brand_result,
                generated_images=generated_images,
                pipeline_metadata=pipeline_metadata,
                total_processing_time=total_processing_time
            )
            
        except Exception as e:
            logger.error(f"Direct gpt-image-1 pipeline error: {str(e)}")
            return DirectGPTImage1PipelineResult(
                success=False,
                brand_deconstruction=None,
                generated_images=[],
                pipeline_metadata={},
                total_processing_time=time.time() - start_time,
                error_message=f"Pipeline error: {str(e)}"
            )
    
    async def _generate_images_directly(self, brand_result: Any, 
                                      image_variations: int,
                                      image_config: Dict[str, Any]) -> List[Any]:
        """Generate images directly from brand analysis using sophisticated prompts."""
        
        # Create sophisticated prompts directly from brand analysis
        prompts = self._create_satirical_prompts(brand_result)
        
        image_requests = []
        
        # Create different variations with different styles and configurations
        base_configs = [
            {
                'size': '1536x1024',  # Landscape
                'quality': 'high',
                'output_format': 'png',
                'output_compression': 95
            },
            {
                'size': '1024x1024',  # Square
                'quality': 'high', 
                'output_format': 'png',
                'output_compression': 95
            },
            {
                'size': '1024x1536',  # Portrait
                'quality': 'high',
                'output_format': 'png',
                'output_compression': 90
            }
        ]
        
        # Generate multiple variations
        for i in range(min(image_variations, len(prompts))):
            prompt = prompts[i]
            config = base_configs[i % len(base_configs)]
            
            # Merge with user config
            final_config = {**config, **image_config}
            
            request = GPTImage1Request(
                optimized_prompt=prompt,
                brand_context={
                    'brand_name': brand_result.brand_analysis.brand_name,
                    'authenticity_score': brand_result.brand_analysis.authenticity_score,
                    'satirical_vulnerabilities': brand_result.brand_analysis.satirical_vulnerabilities
                },
                technical_specifications={
                    'intended_use': 'professional_satirical',
                    'quality_level': 'high'
                },
                generation_config=final_config
            )
            image_requests.append(request)
        
        # Generate all images
        if image_requests:
            generated_images = await self.gpt_image_1_client.batch_generate_images(image_requests)
        else:
            generated_images = []
        
        return generated_images
    
    def _create_satirical_prompts(self, brand_result: Any) -> List[str]:
        """Create sophisticated satirical prompts directly from brand analysis."""
        
        brand_name = brand_result.brand_analysis.brand_name
        vulnerabilities = brand_result.brand_analysis.satirical_vulnerabilities
        primary_prompt = brand_result.satirical_prompts['primary_prompt'].compile_full_prompt()
        
        # Base prompt components
        base_elements = [
            f"Professional corporate photography exposing {brand_name}'s contradictions",
            "Ultra-high resolution 8K quality",
            "Sophisticated satirical irony",
            "Studio lighting with dramatic contrast",
            "Photorealistic execution with subtle subversive elements"
        ]
        
        prompts = []
        
        # Prompt 1: Corporate Contradiction Focus
        if vulnerabilities:
            main_vulnerability = vulnerabilities[0] if vulnerabilities else {}
            vuln_theme = main_vulnerability.get('theme', 'corporate contradiction')
            vuln_desc = main_vulnerability.get('description', 'gap between promise and reality')
            
            prompt1_parts = base_elements + [
                f"Visual metaphor exposing {vuln_theme}",
                f"Showing the disconnect between {brand_name}'s marketing claims and reality",
                f"Corporate office setting with subtle signs of {vuln_desc}",
                "Employees looking confused or frustrated in the background",
                "Oversized corporate branding that appears hollow or cracking",
                "Professional business attire with ironic details"
            ]
            prompts.append(". ".join(prompt1_parts))
        
        # Prompt 2: AI/Technology Washing Focus (if applicable)
        ai_related_vulns = [v for v in vulnerabilities if 'AI' in v.get('theme', '').upper()]
        if ai_related_vulns:
            prompt2_parts = base_elements + [
                f"Modern office building with giant '{brand_name} AI POWERED' signage",
                "Building visibly cracking or unstable beneath the impressive facade",
                "Workers running out with computers showing error messages",
                "Contrast between futuristic AI promises and basic technical failures",
                "Dramatic lighting emphasizing the gap between marketing and reality",
                "High-tech displays showing simple 'SYSTEM ERROR' messages"
            ]
            prompts.append(". ".join(prompt2_parts))
        else:
            # Generic corporate irony prompt
            prompt2_parts = base_elements + [
                f"Corporate boardroom with {brand_name} executives presenting charts",
                "Charts showing upward growth while office windows reveal chaos outside",
                "Professional presentation with subtle absurdist elements",
                "Expensive suits and technology contrasted with obvious problems",
                "Satirical corporate stock photo style with ironic undertones"
            ]
            prompts.append(". ".join(prompt2_parts))
        
        # Prompt 3: Customer Promise vs Reality
        prompt3_parts = base_elements + [
            f"Split-screen composition showing {brand_name}'s customer promises vs reality",
            "Left side: glossy marketing materials with happy customers",
            "Right side: frustrated users dealing with complex, broken systems",
            "Stark visual contrast between promise and delivery",
            "Corporate customer service representatives looking overwhelmed",
            "Technology that appears impressive but clearly isn't working",
            "Professional satirical photography with documentary-style authenticity"
        ]
        prompts.append(". ".join(prompt3_parts))
        
        # Ensure we have the primary prompt if our generated ones aren't enough
        if len(prompts) < 3:
            enhanced_primary = base_elements + [
                primary_prompt,
                "8K ultra-high definition quality",
                "Corporate satirical photography style",
                "Sophisticated visual irony"
            ]
            prompts.append(". ".join(enhanced_primary))
        
        return prompts
    
    async def save_generated_images(self, pipeline_result: DirectGPTImage1PipelineResult, 
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
