"""
Enhanced Image Generation Service
Provides sophisticated image generation capabilities with advanced prompt optimization,
error handling, and cost management
"""

import asyncio
import base64
import io
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from PIL import Image
import openai
from main_platform.config.platform_config import PlatformConfig

class ImageGenerationError(Exception):
    """Custom exception for image generation errors"""
    pass

class ImageOptimizer:
    """Optimizes and enhances prompts for maximum image quality"""
    
    def __init__(self):
        self.optimization_templates = {
            'satirical_corporate': """
                Create a sophisticated satirical image that critiques corporate culture:
                {original_prompt}
                
                Style: Professional photography with subtle satirical elements
                Lighting: Corporate-style dramatic lighting
                Composition: Clean, minimalist design with ironic undertones
                Quality: Ultra-high definition, sharp details
                Color palette: Corporate blues and grays with strategic accent colors
                Avoid: Crude humor, obvious mockery, trademark violations
            """,
            
            'tech_satire': """
                Generate a high-quality satirical commentary on technology culture:
                {original_prompt}
                
                Style: Modern tech aesthetic with satirical twist
                Lighting: Clean, bright lighting typical of tech marketing
                Composition: Sleek, minimalist design with subtle contradictions
                Quality: Ultra-sharp, professional grade imagery
                Elements: Incorporate recognizable tech symbols without trademark issues
                Tone: Intelligent satire that respects the subject while exposing absurdities
            """,
            
            'luxury_brand_critique': """
                Create an elegant satirical image that comments on luxury brand positioning:
                {original_prompt}
                
                Style: High-end fashion photography with satirical undertones
                Lighting: Dramatic, high-contrast lighting
                Composition: Luxury aesthetic with ironic juxtapositions
                Quality: Gallery-worthy, ultra-high resolution
                Elements: Sophisticated visual metaphors and symbolic contradictions
                Approach: Tasteful critique that maintains visual sophistication
            """
        }
    
    def optimize_prompt(self, original_prompt: str, brand_category: str = "general", 
                       pentagram_element: str = "intent_clarity") -> str:
        """
        Optimize a prompt for maximum satirical impact and visual quality
        
        Args:
            original_prompt: The base prompt from pentagram framework
            brand_category: Category of brand being satirized
            pentagram_element: Which pentagram element is being emphasized
        
        Returns:
            Optimized prompt for DALL-E 3
        """
        
        # Select appropriate optimization template
        template_key = self._select_template(brand_category)
        template = self.optimization_templates.get(template_key, self.optimization_templates['satirical_corporate'])
        
        # Apply pentagram-specific enhancements
        pentagram_enhancements = self._get_pentagram_enhancements(pentagram_element)
        
        # Optimize for DALL-E 3 best practices
        dalle_optimizations = self._apply_dalle_optimizations(original_prompt)
        
        # Combine all optimizations
        optimized_prompt = template.format(original_prompt=dalle_optimizations)
        optimized_prompt += f"\n\nPentagram Focus: {pentagram_enhancements}"
        
        return self._finalize_prompt(optimized_prompt)
    
    def _select_template(self, brand_category: str) -> str:
        """Select the most appropriate optimization template"""
        category_mapping = {
            'technology': 'tech_satire',
            'consulting': 'satirical_corporate',
            'luxury': 'luxury_brand_critique',
            'automotive': 'tech_satire',
            'finance': 'satirical_corporate'
        }
        return category_mapping.get(brand_category.lower(), 'satirical_corporate')
    
    def _get_pentagram_enhancements(self, element: str) -> str:
        """Get specific enhancements based on pentagram framework element"""
        enhancements = {
            'intent_clarity': "Emphasize clear visual messaging with obvious but sophisticated satirical intent",
            'fidelity_pass': "Maintain visual consistency with target brand aesthetic while subverting meaning",
            'symbolic_anchoring': "Include recognizable symbols and visual cues from the brand world",
            'environmental_context': "Set in realistic environment where target audience would encounter the brand",
            'brand_world_constraints': "Respect brand visual language while exposing internal contradictions"
        }
        return enhancements.get(element, enhancements['intent_clarity'])
    
    def _apply_dalle_optimizations(self, prompt: str) -> str:
        """Apply DALL-E 3 specific optimizations"""
        # DALL-E 3 responds well to specific, descriptive language
        optimizations = [
            "Ultra-high resolution, professional photography quality",
            "Sharp focus with exceptional detail",
            "Perfect lighting and composition",
            "Sophisticated color grading",
            "Gallery-worthy artistic quality"
        ]
        
        return f"{prompt}\n\n" + " | ".join(optimizations)
    
    def _finalize_prompt(self, prompt: str) -> str:
        """Final prompt optimization and length management"""
        # DALL-E 3 handles longer prompts well, but we still want to be concise
        if len(prompt) > 1000:
            # Truncate while maintaining core message
            prompt = prompt[:950] + "..."
        
        return prompt.strip()

class EnhancedImageService:
    """
    Production-ready image generation service with advanced features:
    - Intelligent prompt optimization
    - Cost management and budgeting
    - Error handling and retries
    - Quality validation
    - Analytics and reporting
    """
    
    def __init__(self, config: PlatformConfig):
        self.config = config
        self.optimizer = ImageOptimizer()
        self.client = None
        self.generation_stats = {
            'total_generated': 0,
            'total_cost': 0.0,
            'success_rate': 0.0,
            'average_generation_time': 0.0
        }
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client with proper configuration"""
        if self.config.security.openai_api_key:
            self.client = openai.AsyncOpenAI(api_key=self.config.security.openai_api_key)
        else:
            print("⚠️ Warning: No OpenAI API key configured. Image generation will use mock responses.")
    
    async def generate_concept_previews(self, satirical_concepts: List[Dict[str, Any]], 
                                      brand_category: str = "general") -> List[Dict[str, Any]]:
        """
        Generate optimized concept previews for user selection
        
        Args:
            satirical_concepts: List of concepts from pentagram framework
            brand_category: Category of brand for optimization
        
        Returns:
            List of enhanced concept previews with optimization data
        """
        concept_previews = []
        
        for i, concept in enumerate(satirical_concepts):
            try:
                # Optimize the prompt for this specific concept
                optimized_prompt = self.optimizer.optimize_prompt(
                    concept.get('visual_description', ''),
                    brand_category,
                    concept.get('pentagram_element', 'intent_clarity')
                )
                
                # Calculate estimated cost and generation time
                estimated_cost = self.config.image_generation.cost_per_image
                estimated_time = 30  # seconds
                
                preview = {
                    'concept_id': i,
                    'original_concept': concept,
                    'optimized_prompt': optimized_prompt,
                    'estimated_cost': estimated_cost,
                    'estimated_time': estimated_time,
                    'optimization_applied': True,
                    'brand_category': brand_category,
                    'preview_available': True
                }
                
                concept_previews.append(preview)
                
            except Exception as e:
                print(f"❌ Error optimizing concept {i}: {str(e)}")
                # Fallback to basic preview
                concept_previews.append({
                    'concept_id': i,
                    'original_concept': concept,
                    'optimized_prompt': concept.get('visual_description', ''),
                    'estimated_cost': estimated_cost,
                    'estimated_time': estimated_time,
                    'optimization_applied': False,
                    'error': str(e)
                })
        
        return concept_previews
    
    async def generate_high_quality_image(self, optimized_prompt: str, 
                                        concept_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate final high-quality image using GPT-Image-1 (DALL-E 3)
        
        Args:
            optimized_prompt: The optimized prompt for generation
            concept_metadata: Additional metadata about the concept
        
        Returns:
            Complete image generation result with metadata
        """
        start_time = time.time()
        
        try:
            if not self.client:
                # Return mock response for testing
                return await self._generate_mock_image(optimized_prompt, concept_metadata)
            
            # Generate image using DALL-E 3
            response = await self.client.images.generate(
                model=self.config.image_generation.model,
                prompt=optimized_prompt,
                size=self.config.image_generation.size,
                quality=self.config.image_generation.quality,
                style=self.config.image_generation.style,
                response_format="b64_json",
                n=1
            )
            
            generation_time = time.time() - start_time
            
            # Process the response
            image_data = response.data[0]
            
            # Validate image quality
            validation_result = await self._validate_image_quality(image_data.b64_json)
            
            result = {
                'success': True,
                'image_base64': image_data.b64_json,
                'original_prompt': optimized_prompt,
                'revised_prompt': getattr(image_data, 'revised_prompt', optimized_prompt),
                'image_specs': {
                    'model': self.config.image_generation.model,
                    'size': self.config.image_generation.size,
                    'quality': self.config.image_generation.quality,
                    'style': self.config.image_generation.style
                },
                'generation_metadata': {
                    'generation_time': generation_time,
                    'cost': self.config.image_generation.cost_per_image,
                    'timestamp': datetime.now().isoformat(),
                    'concept_metadata': concept_metadata,
                    'quality_validation': validation_result
                }
            }
            
            # Update statistics
            self._update_generation_stats(True, generation_time, self.config.image_generation.cost_per_image)
            
            return result
            
        except Exception as e:
            generation_time = time.time() - start_time
            self._update_generation_stats(False, generation_time, 0)
            
            raise ImageGenerationError(f"Image generation failed: {str(e)}")
    
    async def _validate_image_quality(self, image_base64: str) -> Dict[str, Any]:
        """
        Validate the quality and characteristics of generated image
        
        Args:
            image_base64: Base64 encoded image data
        
        Returns:
            Validation results and quality metrics
        """
        try:
            # Decode image for analysis
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            validation = {
                'resolution': image.size,
                'mode': image.mode,
                'format': image.format or 'PNG',
                'file_size_kb': len(image_data) / 1024,
                'aspect_ratio': image.size[0] / image.size[1],
                'quality_score': self._calculate_quality_score(image),
                'validation_passed': True
            }
            
            # Validate expected resolution
            expected_width, expected_height = map(int, self.config.image_generation.size.split('x'))
            if image.size != (expected_width, expected_height):
                validation['validation_passed'] = False
                validation['resolution_warning'] = f"Expected {expected_width}x{expected_height}, got {image.size}"
            
            return validation
            
        except Exception as e:
            return {
                'validation_passed': False,
                'error': str(e),
                'quality_score': 0.0
            }
    
    def _calculate_quality_score(self, image: Image.Image) -> float:
        """
        Calculate a quality score for the generated image
        This is a simplified quality assessment
        """
        try:
            # Basic quality indicators
            score = 0.0
            
            # Resolution score (higher resolution = higher score)
            total_pixels = image.size[0] * image.size[1]
            resolution_score = min(total_pixels / (1536 * 1024), 1.0) * 30
            score += resolution_score
            
            # Color depth score
            if image.mode == 'RGB':
                score += 20
            elif image.mode == 'RGBA':
                score += 15
            
            # File size score (reasonable file size indicates good compression)
            # This would need image_data which isn't available here, so we'll estimate
            score += 25  # Baseline for DALL-E 3 quality
            
            # Aspect ratio score (correct aspect ratio)
            target_ratio = 1536 / 1024
            actual_ratio = image.size[0] / image.size[1]
            ratio_diff = abs(target_ratio - actual_ratio)
            ratio_score = max(0, 25 - (ratio_diff * 100))
            score += ratio_score
            
            return min(score, 100.0)
            
        except Exception:
            return 50.0  # Default middle score if calculation fails
    
    async def _generate_mock_image(self, prompt: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock response for testing without API key"""
        await asyncio.sleep(2)  # Simulate generation time
        
        # Create a simple placeholder image
        mock_image = Image.new('RGB', (1536, 1024), color='#1a1a1a')
        
        # Convert to base64
        buffer = io.BytesIO()
        mock_image.save(buffer, format='PNG')
        mock_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            'success': True,
            'image_base64': mock_base64,
            'original_prompt': prompt,
            'revised_prompt': prompt,
            'image_specs': {
                'model': 'mock-dalle-3',
                'size': '1536x1024',
                'quality': 'hd',
                'style': 'vivid'
            },
            'generation_metadata': {
                'generation_time': 2.0,
                'cost': 0.0,
                'timestamp': datetime.now().isoformat(),
                'concept_metadata': metadata,
                'mock_generation': True,
                'quality_validation': {'validation_passed': True, 'quality_score': 85.0}
            }
        }
    
    def _update_generation_stats(self, success: bool, generation_time: float, cost: float):
        """Update internal generation statistics"""
        self.generation_stats['total_generated'] += 1
        self.generation_stats['total_cost'] += cost
        
        # Update success rate
        if success:
            # Simple moving average for success rate
            current_rate = self.generation_stats['success_rate']
            total = self.generation_stats['total_generated']
            self.generation_stats['success_rate'] = ((current_rate * (total - 1)) + 100) / total
        else:
            current_rate = self.generation_stats['success_rate']
            total = self.generation_stats['total_generated']
            self.generation_stats['success_rate'] = (current_rate * (total - 1)) / total
        
        # Update average generation time
        current_avg = self.generation_stats['average_generation_time']
        total = self.generation_stats['total_generated']
        self.generation_stats['average_generation_time'] = ((current_avg * (total - 1)) + generation_time) / total
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get current generation statistics"""
        return self.generation_stats.copy()
    
    async def batch_generate_concepts(self, concepts: List[Dict[str, Any]], 
                                    max_concurrent: int = 3) -> List[Dict[str, Any]]:
        """
        Generate multiple images concurrently with rate limiting
        
        Args:
            concepts: List of concepts to generate
            max_concurrent: Maximum concurrent generations
        
        Returns:
            List of generation results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_single(concept):
            async with semaphore:
                try:
                    return await self.generate_high_quality_image(
                        concept['optimized_prompt'],
                        concept['original_concept']
                    )
                except Exception as e:
                    return {
                        'success': False,
                        'error': str(e),
                        'concept_id': concept.get('concept_id', 'unknown')
                    }
        
        # Execute all generations concurrently
        tasks = [generate_single(concept) for concept in concepts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
