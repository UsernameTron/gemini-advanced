# File: integrations/gpt4o_visual_client.py

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
class GPT4oVisualRequest:
    """Structure for requests to GPT-4o for 8K visual analysis and generation guidance"""
    pentagram_prompt: str
    brand_context: Dict[str, Any]
    analysis_mode: str = "satirical_visual_analysis"  # or "8k_detailed_concept", "composite_design", "8k_technical_specs"
    visual_style: str = "professional_satirical_8k"
    resolution_target: str = "8k"  # 7680×4320
    output_format: str = "detailed_instructions"  # or "8k_specs", "composite_elements"

@dataclass
class GPT4oVisualResult:
    """Enhanced result structure for GPT-4o 8K visual guidance"""
    success: bool
    visual_concept: Optional[str]  # Core visual concept
    detailed_instructions: Optional[str]  # Detailed 8K generation instructions
    visual_elements: Optional[Dict[str, Any]]  # Specific elements to include
    satirical_approach: Optional[str]  # How to approach the satire visually
    technical_specs: Optional[Dict[str, Any]]  # 8K technical requirements
    k8_optimization: Optional[Dict[str, Any]]  # 8K-specific optimization guidelines
    detail_hierarchy: Optional[Dict[str, Any]]  # Detail distribution for 8K
    processing_time: float
    error_message: Optional[str] = None

class GPT4oVisualClient:
    """
    Advanced GPT-4o integration for sophisticated visual concept development.
    
    This client uses GPT-4o's advanced reasoning to create detailed visual concepts
    and generation instructions that go far beyond simple image prompts.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o", timeout: int = 60):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.timeout = timeout
        
        # GPT-4o specific prompts for 8K visual concept development
        self.visual_analysis_prompts = {
            'satirical_visual_analysis': '''
            You are a world-class creative director specializing in 8K visual satirical critique.
            
            Analyze this brand context and satirical framework to create a sophisticated 8K visual concept:
            
            Brand Context: {brand_context}
            Satirical Framework: {pentagram_prompt}
            Visual Style: {visual_style}
            
            Create a detailed 8K visual concept that:
            1. **Core Visual Metaphor**: A powerful central image that embodies the contradiction
            2. **8K Composition Strategy**: How ultra-high resolution elements should be arranged for maximum impact
            3. **Visual Irony Techniques**: Specific methods to expose the contradiction visually at 8K detail
            4. **Color Psychology**: Color choices that reinforce the satirical message in high resolution
            5. **Typography Integration**: How text elements should interact with visuals at 8K clarity
            6. **Cultural References**: Subtle visual references that enhance the critique
            7. **8K Technical Execution**: Specific technical requirements for 8K realization
            8. **Detail Hierarchy**: Which elements should have fine detail and which should be simplified
            9. **Visual Layers**: How to structure visual depth for 8K viewing
            
            Output as a structured JSON with detailed instructions for each element.
            Focus on creating something that would make viewers pause and think, leveraging 8K resolution for impact.
            ''',
            
            '8k_detailed_concept': '''
            You are an 8K visual concept specialist creating ultra-high resolution satirical imagery.
            
            Transform this satirical analysis into a compelling 8K image concept:
            
            Brand Context: {brand_context}
            Satirical Framework: {pentagram_prompt}
            
            Create a detailed 8K image specification that includes:
            1. **Primary Focus Area**: What draws attention in 8K detail (center 25% of image)
            2. **Secondary Elements**: Supporting visual elements (surrounding areas)
            3. **Background Complexity**: How much detail the background should contain
            4. **Text Integration**: Typography that works at 8K resolution
            5. **Color Depth**: Full color specifications for 8K color space
            6. **Satirical Layering**: How the satirical message unfolds as viewers examine details
            7. **8K Optimization**: Specific considerations for ultra-high resolution
            8. **Viewing Distance**: How the image works at different viewing distances
            9. **Detail Progression**: How satirical elements reveal themselves at different zoom levels
            
            Output detailed specifications optimized for 8K generation and viewing.
            ''',
            
            'composite_design': '''
            You are a graphic design expert creating detailed specifications for 8K composite visual creation.
            
            Design a satirical 8K composite image using the following context:
            
            Brand Context: {brand_context}
            Satirical Framework: {pentagram_prompt}
            
            Provide detailed specifications for 8K resolution (7680×4320):
            1. **Background Elements**: Specific 8K images, textures, or gradients needed
            2. **Foreground Objects**: Key visual elements and their positioning for 8K clarity
            3. **Text Integration**: Font choices, sizing, positioning optimized for 8K displays
            4. **Color Scheme**: Full 8K color space specifications and their satirical significance
            5. **Image Sources**: Types of ultra-high resolution stock images or graphics needed
            6. **Layer Composition**: How elements should be layered for 8K depth and clarity
            7. **Final Effects**: Filters, adjustments, or special effects that work at 8K
            8. **Detail Management**: Which areas should have maximum detail vs simplified areas
            9. **8K Viewing Optimization**: How the image performs on 8K displays at various distances
            
            Output detailed specifications that a graphic designer could follow to create professional 8K satirical content.
            ''',
            
            '8k_technical_specs': '''
            You are a technical imaging specialist creating 8K image generation specifications.
            
            Analyze this satirical concept and provide technical 8K specifications:
            
            Brand Context: {brand_context}
            Satirical Framework: {pentagram_prompt}
            
            Provide detailed 8K technical requirements:
            1. **Resolution Specs**: Exact pixel dimensions and aspect ratios for 8K
            2. **Color Depth**: Bit depth, color space (Rec. 2020, DCI-P3, etc.)
            3. **Compression**: Optimal file formats for 8K satirical content
            4. **Detail Distribution**: Pixel density allocation across image regions
            5. **Text Rendering**: Font rendering specifications for 8K clarity
            6. **Export Settings**: Technical export parameters for different 8K viewing contexts
            7. **Performance Optimization**: How to maintain quality while managing file size
            8. **Display Compatibility**: Ensuring compatibility across 8K display standards
            9. **Satirical Element Clarity**: Technical requirements to ensure satirical elements are visible at 8K
            
            Output precise technical specifications for professional 8K satirical image production.
            '''
        }
    
    async def analyze_and_conceptualize(self, request: GPT4oVisualRequest) -> GPT4oVisualResult:
        """
        Use GPT-4o to create sophisticated visual concepts and detailed instructions.
        """
        
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting GPT-4o visual conceptualization for: {request.brand_context.get('brand_name', 'Unknown')}")
            
            # Select appropriate prompt template
            prompt_template = self.visual_analysis_prompts.get(
                request.analysis_mode, 
                self.visual_analysis_prompts['satirical_visual_analysis']
            )
            
            # Format the prompt
            formatted_prompt = prompt_template.format(
                brand_context=json.dumps(request.brand_context, indent=2),
                pentagram_prompt=request.pentagram_prompt,
                visual_style=request.visual_style
            )
            
            # Call GPT-4o for advanced visual analysis
            response = await self._call_gpt4o(formatted_prompt)
            
            # Process the response
            result = await self._process_gpt4o_response(response, request, start_time)
            
            logger.info(f"GPT-4o visual conceptualization completed in {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"GPT-4o visual conceptualization error: {str(e)}")
            
            return GPT4oVisualResult(
                success=False,
                visual_concept=None,
                detailed_instructions=None,
                visual_elements=None,
                satirical_approach=None,
                technical_specs=None,
                k8_optimization=None,
                detail_hierarchy=None,
                processing_time=processing_time,
                error_message=f"GPT-4o error: {str(e)}"
            )
    
    async def _call_gpt4o(self, prompt: str) -> Any:
        """Make the GPT-4o API call with advanced reasoning."""
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert creative director and visual satirist. Provide detailed, actionable visual concepts that expose corporate contradictions through sophisticated visual techniques."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.8,  # Higher creativity for visual concepts
                max_tokens=2000,  # Longer responses for detailed instructions
                response_format={ "type": "json_object" }  # Structured output
            )
            return response
            
        except Exception as e:
            logger.error(f"GPT-4o API error: {str(e)}")
            raise
    
    async def _process_gpt4o_response(self, response: Any, request: GPT4oVisualRequest, start_time: datetime) -> GPT4oVisualResult:
        """Process GPT-4o response into structured 8K visual guidance."""
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        try:
            # Extract the response content
            content = response.choices[0].message.content
            
            # Parse JSON response
            visual_data = json.loads(content)
            
            # Extract key components for 8K visual concepts
            visual_concept = visual_data.get('core_visual_metaphor', '')
            detailed_instructions = visual_data.get('detailed_instructions', '')
            visual_elements = visual_data.get('visual_elements', {})
            satirical_approach = visual_data.get('satirical_approach', '')
            technical_specs = visual_data.get('technical_specs', {})
            
            # Handle 8K-specific optimizations
            k8_optimization = visual_data.get('8k_optimization', {})
            detail_hierarchy = visual_data.get('detail_hierarchy', {})
            
            return GPT4oVisualResult(
                success=True,
                visual_concept=visual_concept,
                detailed_instructions=detailed_instructions,
                visual_elements=visual_elements,
                satirical_approach=satirical_approach,
                technical_specs=technical_specs,
                k8_optimization=k8_optimization,
                detail_hierarchy=detail_hierarchy,
                processing_time=processing_time
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT-4o JSON response: {str(e)}")
            # Fallback to text processing
            content = response.choices[0].message.content
            
            return GPT4oVisualResult(
                success=True,
                visual_concept="Advanced 8K visual concept (see detailed instructions)",
                detailed_instructions=content,
                visual_elements={},
                satirical_approach="GPT-4o advanced 8K analysis",
                technical_specs={},
                k8_optimization={},
                detail_hierarchy={},
                processing_time=processing_time
            )
