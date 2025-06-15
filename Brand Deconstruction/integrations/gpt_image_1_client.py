# File: integrations/gpt_image_1_client.py

import asyncio
import aiohttp
import json
import base64
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import logging
import openai
from PIL import Image
import io
import os
import time

logger = logging.getLogger(__name__)

@dataclass
class GPTImage1Request:
    """Structure for requests to gpt-image-1 for high-quality image generation"""
    optimized_prompt: str  # From GPT-4o concept development
    brand_context: Dict[str, Any]
    technical_specifications: Dict[str, Any]
    generation_config: Optional[Dict[str, Any]] = None

@dataclass
class GPTImage1Result:
    """Result from gpt-image-1 generation"""
    success: bool
    image_data: Optional[str]  # Base64 encoded image
    generation_metadata: Dict[str, Any]
    processing_time: float
    image_specs: Dict[str, Any]
    error_message: Optional[str] = None

class GPTImage1Client:
    """
    Client for gpt-image-1 high-quality image generation.
    
    This client takes the sophisticated concepts from GPT-4o and generates
    actual high-quality images using OpenAI's latest gpt-image-1 model.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-image-1", timeout: int = 120):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.timeout = timeout
        
        # gpt-image-1 optimized configuration for satirical content
        self.default_config = {
            'size': '1536x1024',  # Landscape for most satirical content
            'quality': 'high',    # Maximum quality
            'output_format': 'png',  # Best quality format
            'output_compression': 95,  # High quality with reasonable file size
            'moderation': 'auto',  # Content moderation
            'background': 'auto',  # Let model decide background
            'n': 1  # One image per request
        }
    
    async def generate_satirical_image(self, request: GPTImage1Request) -> GPTImage1Result:
        """
        Generate high-quality satirical image using gpt-image-1.
        
        This method takes GPT-4o's sophisticated concept and converts it
        into an actual high-resolution image using gpt-image-1.
        """
        
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting gpt-image-1 generation for: {request.brand_context.get('brand_name', 'Unknown')}")
            
            # Step 1: Optimize prompt for gpt-image-1
            final_prompt = self._optimize_prompt_for_gpt_image_1(request)
            
            # Step 2: Configure generation parameters
            generation_params = self._prepare_generation_params(request)
            
            # Step 3: Call gpt-image-1 API
            response = await self._call_gpt_image_1(final_prompt, generation_params)
            
            # Step 4: Process the response
            if response and len(response.data) > 0:
                result = await self._process_successful_generation(response, request, start_time)
            else:
                result = GPTImage1Result(
                    success=False,
                    image_data=None,
                    generation_metadata={},
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    image_specs={},
                    error_message="No image data returned from gpt-image-1"
                )
            
            logger.info(f"gpt-image-1 generation completed in {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"gpt-image-1 generation error: {str(e)}")
            
            return GPTImage1Result(
                success=False,
                image_data=None,
                generation_metadata={},
                processing_time=processing_time,
                image_specs={},
                error_message=f"gpt-image-1 error: {str(e)}"
            )
    
    def _optimize_prompt_for_gpt_image_1(self, request: GPTImage1Request) -> str:
        """
        Optimize the GPT-4o concept for gpt-image-1 generation.
        
        gpt-image-1 supports up to 32,000 characters, so we can include
        very detailed descriptions from the GPT-4o concept development.
        """
        
        base_prompt = request.optimized_prompt
        brand_context = request.brand_context
        tech_specs = request.technical_specifications
        
        # Build comprehensive prompt for gpt-image-1
        prompt_parts = [base_prompt]
        
        # Add technical specifications
        if tech_specs:
            resolution = tech_specs.get('target_resolution', 'high resolution')
            lighting = tech_specs.get('lighting_setup', 'professional studio lighting')
            composition = tech_specs.get('composition_style', 'rule of thirds')
            
            prompt_parts.append(f"Technical requirements: {resolution}, {lighting}, {composition}")
        
        # Add brand-specific context for satirical accuracy
        brand_name = brand_context.get('brand_name', '')
        if brand_name:
            prompt_parts.append(f"Corporate context: {brand_name} brand identity and visual style")
        
        # Add satirical vulnerability context
        vulnerabilities = brand_context.get('satirical_vulnerabilities', [])
        if vulnerabilities:
            vuln_themes = [v.get('theme', '') for v in vulnerabilities[:2]]  # Top 2 vulnerabilities
            prompt_parts.append(f"Satirical focus: exposing {', '.join(vuln_themes)}")
        
        # Add quality and style requirements
        prompt_parts.extend([
            "Style: Professional corporate photography with satirical irony",
            "Quality: Ultra-high resolution, studio-quality lighting, sharp focus",
            "Mood: Sophisticated satirical critique, thought-provoking visual contradiction",
            "Execution: Photorealistic rendering with subtle ironic elements"
        ])
        
        final_prompt = ". ".join(prompt_parts)
        
        # Ensure we don't exceed the 32,000 character limit
        if len(final_prompt) > 31000:
            final_prompt = final_prompt[:30900] + "..."
        
        logger.debug(f"Optimized gpt-image-1 prompt: {len(final_prompt)} characters")
        return final_prompt
    
    def _prepare_generation_params(self, request: GPTImage1Request) -> Dict[str, Any]:
        """Prepare generation parameters optimized for gpt-image-1 only."""
        params = {
            'size': '1536x1024',
            'quality': 'high',
            'output_format': 'png',
            'output_compression': 95,
            'moderation': 'auto',
            'background': 'auto',
            'n': 1
        }
        valid_params = {
            'size', 'quality', 'output_format', 'output_compression', 
            'moderation', 'background', 'n'
        }
        # Override with request-specific parameters
        if request.generation_config:
            for key, value in request.generation_config.items():
                if key in valid_params:
                    params[key] = value
        # Optimize based on technical specifications
        tech_specs = request.technical_specifications
        if tech_specs:
            quality_level = tech_specs.get('quality_level', 'high')
            if quality_level in ['high', 'medium', 'low']:
                params['quality'] = quality_level
        return params
    
    async def _call_gpt_image_1(self, prompt: str, params: Dict[str, Any]) -> Any:
        """Make the actual gpt-image-1 API call."""
        
        try:
            # Use asyncio.to_thread for the synchronous OpenAI call
            response = await asyncio.to_thread(
                self.client.images.generate,
                model=self.model,
                prompt=prompt,
                **params
            )
            return response
            
        except openai.RateLimitError as e:
            logger.error(f"gpt-image-1 rate limit exceeded: {str(e)}")
            raise
        except openai.APIError as e:
            logger.error(f"gpt-image-1 API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected gpt-image-1 error: {str(e)}")
            raise
    
    async def _process_successful_generation(self, response: Any, request: GPTImage1Request, start_time: datetime) -> GPTImage1Result:
        """Process successful gpt-image-1 response."""
        
        image_data = response.data[0]
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Extract image data (gpt-image-1 returns base64)
        image_b64 = getattr(image_data, 'b64_json', None)
        
        # Prepare generation metadata
        generation_metadata = {
            'model_used': self.model,
            'generation_id': datetime.now().isoformat(),
            'prompt_optimization': 'gpt4o_enhanced',
            'brand_context': {
                'brand_name': request.brand_context.get('brand_name'),
                'authenticity_score': request.brand_context.get('authenticity_score'),
                'satirical_focus': [v.get('theme') for v in request.brand_context.get('satirical_vulnerabilities', [])]
            },
            'generation_config': request.generation_config or self.default_config,
            'processing_time': processing_time,
            'usage_info': getattr(response, 'usage', {})
        }
        
        # Extract image specifications
        image_specs = {
            'format': request.generation_config.get('output_format', 'png') if request.generation_config else 'png',
            'size': request.generation_config.get('size', '1536x1024') if request.generation_config else '1536x1024',
            'quality': request.generation_config.get('quality', 'high') if request.generation_config else 'high',
            'compression': request.generation_config.get('output_compression', 95) if request.generation_config else 95,
            'file_size_estimate': len(image_b64) * 3 // 4 if image_b64 else 0  # Estimate from base64
        }
        
        return GPTImage1Result(
            success=True,
            image_data=image_b64,
            generation_metadata=generation_metadata,
            processing_time=processing_time,
            image_specs=image_specs
        )
    
    async def batch_generate_images(self, requests: List[GPTImage1Request]) -> List[GPTImage1Result]:
        """
        Generate multiple images with controlled concurrency.
        
        Uses rate limiting appropriate for gpt-image-1 to generate
        multiple variations or concepts efficiently.
        """
        
        logger.info(f"Starting batch gpt-image-1 generation for {len(requests)} concepts")
        
        # Conservative concurrency for gpt-image-1
        semaphore = asyncio.Semaphore(2)
        
        async def generate_with_semaphore(request):
            async with semaphore:
                # Small delay between requests
                await asyncio.sleep(1.0)
                return await self.generate_satirical_image(request)
        
        # Execute all requests with controlled concurrency
        results = await asyncio.gather(
            *[generate_with_semaphore(req) for req in requests],
            return_exceptions=True
        )
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch generation failed for request {i}: {str(result)}")
                processed_results.append(GPTImage1Result(
                    success=False,
                    image_data=None,
                    generation_metadata={},
                    processing_time=0,
                    image_specs={},
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        successful_generations = sum(1 for r in processed_results if r.success)
        logger.info(f"Batch gpt-image-1 generation completed: {successful_generations}/{len(requests)} successful")
        
        return processed_results
