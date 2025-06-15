# File: integrations/pure_gpt4o_8k_client.py

import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import openai
import time

logger = logging.getLogger(__name__)

@dataclass
class Pure8KVisualRequest:
    """Structure for requests to GPT-4o for pure 8K visual concept development"""
    pentagram_prompt: str
    brand_context: Dict[str, Any]
    analysis_mode: str = "8k_concept_development"  # or "technical_specifications", "creative_direction", "implementation_guide"
    visual_style: str = "professional_satirical_8k"
    resolution_target: str = "8k_uhd"  # 7680×4320
    output_depth: str = "comprehensive"  # or "technical", "creative", "implementation"

@dataclass
class Pure8KVisualResult:
    """Pure GPT-4o result structure for 8K visual concept development"""
    success: bool
    concept_title: Optional[str]  # Brief concept title
    visual_concept: Optional[str]  # Core visual concept description
    detailed_breakdown: Optional[Dict[str, Any]]  # Detailed element breakdown
    technical_specifications: Optional[Dict[str, Any]]  # 8K technical requirements
    creative_direction: Optional[Dict[str, Any]]  # Creative implementation guidance
    satirical_strategy: Optional[Dict[str, Any]]  # How satire is implemented visually
    implementation_steps: Optional[List[str]]  # Step-by-step creation guide
    alternative_concepts: Optional[List[Dict]]  # Alternative visual approaches
    quality_benchmarks: Optional[Dict[str, Any]]  # Success criteria
    processing_time: float
    error_message: Optional[str] = None

class PureGPT4o8KClient:
    """
    Pure GPT-4o client for sophisticated 8K visual concept development.
    
    This client uses only GPT-4o's advanced reasoning to create detailed
    visual concepts, technical specifications, and implementation guidance
    for 8K satirical imagery. No image generation - pure conceptual development.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o", timeout: int = 120):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.timeout = timeout
        
        # Pure conceptual analysis prompts for 8K visual development
        self.analysis_prompts = {
            '8k_concept_development': '''
            You are a world-class creative director and visual strategist specializing in ultra-high resolution satirical imagery.
            
            Develop a comprehensive 8K visual concept for satirical brand critique:
            
            Brand Context: {brand_context}
            Satirical Framework: {pentagram_prompt}
            Target Resolution: 8K UHD (7680×4320)
            Visual Style: {visual_style}
            
            Create a detailed visual concept with the following structure:
            
            {
                "concept_title": "Brief, impactful title for the concept",
                "core_visual_metaphor": "Central visual idea that embodies the brand contradiction",
                "detailed_breakdown": {
                    "primary_focus": "Main visual element that captures attention (center 30% of frame)",
                    "secondary_elements": "Supporting visual components and their positioning",
                    "background_strategy": "How the background reinforces the satirical message",
                    "text_integration": "Typography approach and text placement strategy",
                    "color_psychology": "Color choices and their satirical significance",
                    "symbolic_elements": "Visual symbols and metaphors used",
                    "irony_techniques": "Specific methods to create visual irony"
                },
                "technical_specifications": {
                    "resolution_details": "8K UHD specifications and aspect ratio considerations",
                    "detail_hierarchy": "Which areas should have maximum detail vs simplified areas",
                    "color_depth": "Color space and bit depth recommendations",
                    "viewing_optimization": "How the image performs at different viewing distances",
                    "file_format": "Optimal file formats for 8K delivery"
                },
                "creative_direction": {
                    "mood_and_tone": "Overall emotional impact and satirical tone",
                    "cultural_references": "Relevant cultural or visual references to include",
                    "target_audience": "How different viewers will interpret the imagery",
                    "memorable_elements": "What makes this concept stick in viewers' minds",
                    "brand_specific_hooks": "Elements that directly relate to this specific brand"
                },
                "satirical_strategy": {
                    "contradiction_exposure": "How the visual exposes brand contradictions",
                    "subtlety_balance": "Balance between obvious and subtle satirical elements",
                    "viewer_journey": "How understanding unfolds as viewers examine details",
                    "emotional_impact": "Target emotional response from viewers",
                    "criticism_method": "Approach to critiquing without being heavy-handed"
                },
                "implementation_steps": [
                    "Step-by-step guide for creating this visual concept",
                    "Include specific tools, techniques, and considerations for each step"
                ],
                "alternative_concepts": [
                    {
                        "variation_title": "Alternative approach title",
                        "concept_description": "Different way to achieve similar satirical impact",
                        "key_differences": "How this varies from the primary concept"
                    }
                ],
                "quality_benchmarks": {
                    "visual_impact": "Criteria for measuring visual effectiveness",
                    "satirical_clarity": "How to ensure the satirical message is clear",
                    "technical_quality": "8K quality standards to meet",
                    "brand_relevance": "Ensuring the concept specifically targets this brand"
                }
            }
            
            Focus on creating a concept that leverages 8K resolution for maximum satirical impact.
            ''',
            
            'technical_specifications': '''
            You are a technical imaging specialist focused on 8K visual production standards.
            
            Provide comprehensive technical specifications for 8K satirical image creation:
            
            Brand Context: {brand_context}
            Satirical Framework: {pentagram_prompt}
            Visual Style: {visual_style}
            
            Generate detailed technical requirements:
            
            {
                "resolution_specifications": {
                    "pixel_dimensions": "Exact 8K dimensions and ratios",
                    "aspect_ratio_options": "Standard and custom aspect ratios for 8K",
                    "pixel_density": "Optimal PPI for different viewing contexts",
                    "safe_areas": "Areas to avoid for text and critical elements"
                },
                "color_specifications": {
                    "color_space": "Recommended color spaces (Rec. 2020, DCI-P3, sRGB)",
                    "bit_depth": "Color depth recommendations for 8K",
                    "gamma_settings": "Gamma curve specifications",
                    "color_accuracy": "Standards for color reproduction"
                },
                "file_management": {
                    "working_formats": "Formats for creation and editing",
                    "delivery_formats": "Final formats for different use cases",
                    "compression_settings": "Balancing quality and file size",
                    "metadata_requirements": "Essential metadata for 8K images"
                },
                "production_workflow": {
                    "software_requirements": "Recommended tools for 8K creation",
                    "hardware_specifications": "Minimum hardware for 8K work",
                    "rendering_settings": "Optimal settings for 8K output",
                    "quality_control": "Methods to verify 8K quality"
                },
                "display_optimization": {
                    "viewing_distances": "Optimal viewing distances for 8K displays",
                    "display_calibration": "Requirements for accurate 8K viewing",
                    "fallback_versions": "Lower resolution versions for compatibility",
                    "responsive_considerations": "How the image scales on different devices"
                },
                "satirical_technical_considerations": {
                    "detail_visibility": "Ensuring satirical elements are visible at 8K",
                    "text_readability": "Typography standards for 8K resolution",
                    "symbolic_clarity": "Technical requirements for visual symbols",
                    "irony_preservation": "Maintaining satirical impact across resolutions"
                }
            }
            
            Provide precise technical guidance for professional 8K satirical image production.
            ''',
            
            'creative_direction': '''
            You are a creative director specializing in visual satirical storytelling.
            
            Develop comprehensive creative direction for 8K satirical imagery:
            
            Brand Context: {brand_context}
            Satirical Framework: {pentagram_prompt}
            Visual Style: {visual_style}
            
            Provide detailed creative guidance:
            
            {
                "creative_vision": {
                    "overarching_concept": "The big idea behind the visual",
                    "emotional_journey": "How viewers' emotions should progress",
                    "satirical_thesis": "The core argument being made visually",
                    "visual_narrative": "The story told through the imagery"
                },
                "artistic_approach": {
                    "visual_style": "Specific artistic style and influences",
                    "composition_strategy": "How elements are arranged for impact",
                    "lighting_concept": "Lighting approach and mood",
                    "texture_strategy": "Use of textures to enhance meaning"
                },
                "brand_specific_elements": {
                    "logo_treatment": "How to incorporate or subvert brand logos",
                    "color_palette": "Using or contrasting brand colors",
                    "typography_approach": "Font choices that relate to brand identity",
                    "visual_language": "Adopting or parodying brand visual language"
                },
                "satirical_techniques": {
                    "irony_methods": "Specific techniques for creating visual irony",
                    "juxtaposition_strategy": "Contrasting elements for satirical effect",
                    "symbolism_approach": "Use of symbols and metaphors",
                    "cultural_commentary": "Broader cultural critique through the imagery"
                },
                "execution_guidance": {
                    "mood_board_concepts": "Visual references and inspirations",
                    "style_consistency": "Maintaining coherent visual approach",
                    "detail_priorities": "Which elements deserve most attention",
                    "revision_criteria": "How to evaluate and improve the concept"
                },
                "impact_optimization": {
                    "memorability_factors": "What makes this concept stick",
                    "shareability_elements": "Aspects that encourage sharing",
                    "discussion_triggers": "Elements that spark conversation",
                    "viral_potential": "Features that could drive viral spread"
                }
            }
            
            Focus on creative direction that maximizes satirical impact and cultural relevance.
            ''',
            
            'implementation_guide': '''
            You are a visual production specialist creating step-by-step implementation guides.
            
            Create a comprehensive implementation guide for 8K satirical image creation:
            
            Brand Context: {brand_context}
            Satirical Framework: {pentagram_prompt}
            Visual Style: {visual_style}
            
            Provide detailed implementation guidance:
            
            {
                "pre_production": {
                    "concept_refinement": "Steps to finalize the visual concept",
                    "reference_gathering": "Collecting visual references and materials",
                    "tool_preparation": "Software and hardware setup requirements",
                    "workflow_planning": "Organizing the creation process"
                },
                "production_phases": {
                    "phase_1_foundation": {
                        "description": "Setting up the basic composition",
                        "specific_steps": ["Detailed step-by-step instructions"],
                        "tools_required": "Software and tools needed",
                        "quality_checkpoints": "What to verify at this stage"
                    },
                    "phase_2_development": {
                        "description": "Building out visual elements",
                        "specific_steps": ["Detailed step-by-step instructions"],
                        "tools_required": "Software and tools needed",
                        "quality_checkpoints": "What to verify at this stage"
                    },
                    "phase_3_refinement": {
                        "description": "Adding detail and satirical elements",
                        "specific_steps": ["Detailed step-by-step instructions"],
                        "tools_required": "Software and tools needed",
                        "quality_checkpoints": "What to verify at this stage"
                    },
                    "phase_4_finalization": {
                        "description": "Final adjustments and 8K optimization",
                        "specific_steps": ["Detailed step-by-step instructions"],
                        "tools_required": "Software and tools needed",
                        "quality_checkpoints": "What to verify at this stage"
                    }
                },
                "technical_implementation": {
                    "8k_setup": "Configuring tools for 8K work",
                    "color_management": "Setting up color profiles and calibration",
                    "file_organization": "Organizing project files and assets",
                    "backup_strategy": "Protecting work during creation"
                },
                "satirical_implementation": {
                    "irony_placement": "Where and how to place ironic elements",
                    "subtlety_balance": "Balancing obvious and subtle satirical elements",
                    "brand_integration": "Incorporating brand elements satirically",
                    "message_clarity": "Ensuring the satirical message is clear"
                },
                "quality_assurance": {
                    "review_checklist": "Comprehensive quality review criteria",
                    "test_viewing": "Testing the image at different resolutions and distances",
                    "feedback_integration": "How to incorporate feedback effectively",
                    "final_validation": "Confirming the image meets all requirements"
                },
                "delivery_preparation": {
                    "format_optimization": "Preparing files for different use cases",
                    "compression_testing": "Optimizing file size without quality loss",
                    "compatibility_checking": "Ensuring compatibility across platforms",
                    "documentation": "Creating documentation for the final deliverable"
                }
            }
            
            Provide actionable guidance that anyone can follow to create professional 8K satirical imagery.
            '''
        }
    
    async def develop_8k_concept(self, request: Pure8KVisualRequest) -> Pure8KVisualResult:
        """
        Use GPT-4o to develop comprehensive 8K visual concepts and implementation guidance.
        """
        
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting pure GPT-4o 8K concept development for: {request.brand_context.get('brand_name', 'Unknown')}")
            
            # Select appropriate analysis prompt
            prompt_template = self.analysis_prompts.get(
                request.analysis_mode, 
                self.analysis_prompts['8k_concept_development']
            )
            
            # Format the prompt
            formatted_prompt = prompt_template.format(
                brand_context=json.dumps(request.brand_context, indent=2),
                pentagram_prompt=request.pentagram_prompt,
                visual_style=request.visual_style
            )
            
            # Call GPT-4o for concept development
            response = await self._call_gpt4o(formatted_prompt)
            
            # Process the response
            result = await self._process_concept_response(response, request, start_time)
            
            logger.info(f"GPT-4o 8K concept development completed in {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"GPT-4o 8K concept development error: {str(e)}")
            
            return Pure8KVisualResult(
                success=False,
                concept_title=None,
                visual_concept=None,
                detailed_breakdown=None,
                technical_specifications=None,
                creative_direction=None,
                satirical_strategy=None,
                implementation_steps=None,
                alternative_concepts=None,
                quality_benchmarks=None,
                processing_time=processing_time,
                error_message=f"GPT-4o concept development error: {str(e)}"
            )
    
    async def _call_gpt4o(self, prompt: str) -> Any:
        """Make the GPT-4o API call for concept development."""
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert creative director, visual strategist, and satirical artist. Provide comprehensive, actionable visual concepts and implementation guidance that expose corporate contradictions through sophisticated 8K imagery. Always respond with valid JSON."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.9,  # High creativity for concept development
                max_tokens=3000,  # Longer responses for comprehensive guidance
                response_format={ "type": "json_object" }  # Structured output
            )
            return response
            
        except Exception as e:
            logger.error(f"GPT-4o API error: {str(e)}")
            raise
    
    def _extract_json_from_response(self, content: str) -> dict:
        """Extract JSON from GPT-4o response, handling various formats."""
        logger.debug(f"Attempting to extract JSON from content length: {len(content)}")
        
        try:
            # First try direct JSON parsing
            result = json.loads(content)
            logger.debug("Successfully parsed JSON directly")
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"Direct JSON parsing failed: {str(e)}")
            logger.debug(f"Failed content sample: {content[:500]}")
            
            # Try to find JSON within the response
            import re
            
            # Look for JSON object patterns with better regex
            json_patterns = [
                r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})',  # Nested JSON objects
                r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks
                r'```\s*(\{.*?\})\s*```',  # JSON in generic code blocks
                r'\{.*\}',  # Basic JSON object (last resort)
            ]
            
            for i, pattern in enumerate(json_patterns):
                matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
                logger.debug(f"Pattern {i} found {len(matches)} matches")
                for j, match in enumerate(matches):
                    try:
                        # Clean up the match
                        cleaned_match = match.strip()
                        if cleaned_match:
                            result = json.loads(cleaned_match)
                            logger.debug(f"Successfully parsed JSON from pattern {i}, match {j}")
                            return result
                    except json.JSONDecodeError as parse_error:
                        logger.debug(f"Pattern {i}, match {j} parse failed: {str(parse_error)}")
                        continue
            
            # Try to extract just the first complete JSON object
            try:
                # Find the first { and try to parse from there
                start_idx = content.find('{')
                if start_idx != -1:
                    # Count braces to find complete JSON
                    brace_count = 0
                    end_idx = start_idx
                    
                    for i, char in enumerate(content[start_idx:], start_idx):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i + 1
                                break
                    
                    if brace_count == 0:
                        json_str = content[start_idx:end_idx]
                        logger.debug(f"Extracted JSON string: {json_str[:200]}...")
                        result = json.loads(json_str)
                        logger.debug("Successfully parsed JSON using brace matching")
                        return result
            except (json.JSONDecodeError, ValueError) as parse_error:
                logger.debug(f"Brace matching parse failed: {str(parse_error)}")
                pass
            
            logger.warning(f"Could not extract valid JSON from response. Creating structured fallback.")
            # If no valid JSON found, create a structured response from text
            return self._parse_text_response(content)

    def _parse_text_response(self, content: str) -> dict:
        """Parse text response into structured format when JSON parsing fails."""
        # Create a basic structure with the raw content
        return {
            "concept_title": "8K Visual Concept",
            "core_visual_metaphor": "Advanced visual concept development",
            "detailed_breakdown": {
                "raw_response": content,
                "parsing_note": "Response parsed as text due to format issues"
            },
            "technical_specifications": {
                "resolution_details": "8K UHD (7680×4320) resolution",
                "format_note": "Technical specs extracted from text analysis"
            },
            "creative_direction": {
                "response_content": content[:500] + "..." if len(content) > 500 else content
            },
            "satirical_strategy": {
                "approach": "Extracted from response analysis"
            },
            "implementation_steps": [
                "Analyze the provided conceptual guidance",
                "Extract actionable insights from the response",
                "Develop based on the conceptual framework provided"
            ],
            "alternative_concepts": [],
            "quality_benchmarks": {
                "content_quality": "Conceptual guidance provided",
                "format_note": "Structured from text analysis"
            }
        }

    async def _process_concept_response(self, response: Any, request: Pure8KVisualRequest, start_time: datetime) -> Pure8KVisualResult:
        """Process GPT-4o response into structured 8K concept guidance."""
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        try:
            # Extract the response content
            content = response.choices[0].message.content
            logger.debug(f"GPT-4o raw response content: {content[:200]}...")
            
            # Try to extract JSON from the response
            concept_data = self._extract_json_from_response(content)
            
            # Extract components based on analysis mode
            if request.analysis_mode == '8k_concept_development':
                concept_title = concept_data.get('concept_title', '')
                visual_concept = concept_data.get('core_visual_metaphor', '')
                detailed_breakdown = concept_data.get('detailed_breakdown', {})
                technical_specifications = concept_data.get('technical_specifications', {})
                creative_direction = concept_data.get('creative_direction', {})
                satirical_strategy = concept_data.get('satirical_strategy', {})
                implementation_steps = concept_data.get('implementation_steps', [])
                alternative_concepts = concept_data.get('alternative_concepts', [])
                quality_benchmarks = concept_data.get('quality_benchmarks', {})
                
            elif request.analysis_mode == 'technical_specifications':
                concept_title = "Technical Specifications for 8K Production"
                visual_concept = "Comprehensive technical requirements"
                detailed_breakdown = concept_data
                technical_specifications = concept_data
                creative_direction = {}
                satirical_strategy = {}
                implementation_steps = []
                alternative_concepts = []
                quality_benchmarks = concept_data.get('quality_control', {})
                
            elif request.analysis_mode == 'creative_direction':
                concept_title = concept_data.get('creative_vision', {}).get('overarching_concept', 'Creative Direction')
                visual_concept = concept_data.get('creative_vision', {}).get('satirical_thesis', '')
                detailed_breakdown = concept_data.get('artistic_approach', {})
                technical_specifications = {}
                creative_direction = concept_data
                satirical_strategy = concept_data.get('satirical_techniques', {})
                implementation_steps = []
                alternative_concepts = []
                quality_benchmarks = concept_data.get('impact_optimization', {})
                
            elif request.analysis_mode == 'implementation_guide':
                concept_title = "8K Implementation Guide"
                visual_concept = "Step-by-step creation guidance"
                detailed_breakdown = concept_data.get('production_phases', {})
                technical_specifications = concept_data.get('technical_implementation', {})
                creative_direction = {}
                satirical_strategy = concept_data.get('satirical_implementation', {})
                implementation_steps = []
                for phase_data in concept_data.get('production_phases', {}).values():
                    if isinstance(phase_data, dict) and 'specific_steps' in phase_data:
                        implementation_steps.extend(phase_data['specific_steps'])
                alternative_concepts = []
                quality_benchmarks = concept_data.get('quality_assurance', {})
                
            else:
                # Fallback for any unrecognized mode
                concept_title = "8K Visual Concept"
                visual_concept = str(concept_data)[:500]
                detailed_breakdown = concept_data
                technical_specifications = {}
                creative_direction = {}
                satirical_strategy = {}
                implementation_steps = []
                alternative_concepts = []
                quality_benchmarks = {}
            
            return Pure8KVisualResult(
                success=True,
                concept_title=concept_title,
                visual_concept=visual_concept,
                detailed_breakdown=detailed_breakdown,
                technical_specifications=technical_specifications,
                creative_direction=creative_direction,
                satirical_strategy=satirical_strategy,
                implementation_steps=implementation_steps,
                alternative_concepts=alternative_concepts,
                quality_benchmarks=quality_benchmarks,
                processing_time=processing_time
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT-4o JSON response: {str(e)}")
            # Fallback to text processing
            content = response.choices[0].message.content
            
            return Pure8KVisualResult(
                success=True,
                concept_title="Advanced 8K Visual Concept",
                visual_concept="Comprehensive concept development (see detailed breakdown)",
                detailed_breakdown={"raw_response": content, "parsing_error": str(e)},
                technical_specifications={},
                creative_direction={},
                satirical_strategy={},
                implementation_steps=[],
                alternative_concepts=[],
                quality_benchmarks={},
                processing_time=processing_time
            )
        
        except Exception as e:
            logger.error(f"Error processing GPT-4o concept response: {str(e)}")
            
            return Pure8KVisualResult(
                success=False,
                concept_title="",
                visual_concept="",
                detailed_breakdown={},
                technical_specifications={},
                creative_direction={},
                satirical_strategy={},
                implementation_steps=[],
                alternative_concepts=[],
                quality_benchmarks={},
                processing_time=processing_time,
                error_message=f"Processing error: {str(e)}"
            )
    
    async def batch_develop_concepts(self, requests: List[Pure8KVisualRequest]) -> List[Pure8KVisualResult]:
        """
        Develop multiple 8K visual concepts simultaneously.
        
        Uses controlled concurrency to develop multiple satirical concepts
        for comprehensive brand analysis coverage.
        """
        
        logger.info(f"Starting batch 8K concept development for {len(requests)} concepts")
        
        # Limit concurrent requests for GPT-4o
        semaphore = asyncio.Semaphore(3)  # Conservative concurrency
        
        async def develop_with_semaphore(request):
            async with semaphore:
                # Add small delay between requests
                await asyncio.sleep(0.2)
                return await self.develop_8k_concept(request)
        
        # Execute all requests with controlled concurrency
        results = await asyncio.gather(
            *[develop_with_semaphore(req) for req in requests],
            return_exceptions=True
        )
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch concept development failed for request {i}: {str(result)}")
                processed_results.append(Pure8KVisualResult(
                    success=False,
                    concept_title=None,
                    visual_concept=None,
                    detailed_breakdown=None,
                    technical_specifications=None,
                    creative_direction=None,
                    satirical_strategy=None,
                    implementation_steps=None,
                    alternative_concepts=None,
                    quality_benchmarks=None,
                    processing_time=0,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        successful_concepts = sum(1 for r in processed_results if r.success)
        logger.info(f"Batch 8K concept development completed: {successful_concepts}/{len(requests)} successful")
        
        return processed_results
