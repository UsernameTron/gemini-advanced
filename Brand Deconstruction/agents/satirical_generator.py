# File: agents/satirical_generator.py

import time
import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from core.base_agents import AgentBase, AgentResponse

logger = logging.getLogger(__name__)

@dataclass
class PentagramPrompt:
    """Structure for the Pentagram Framework satirical prompts"""
    intent_clarity: str
    symbolic_anchoring: str
    environmental_context: str
    fidelity_specification: str
    audience_calibration: str
    
    def compile_full_prompt(self) -> str:
        """Compile the five elements into a complete prompt"""
        return f"{self.intent_clarity} through {self.symbolic_anchoring} in {self.environmental_context}, {self.fidelity_specification}, calibrated for {self.audience_calibration}"

@dataclass
class SatiricalPromptResult:
    """Results from satirical prompt generation"""
    primary_prompt: PentagramPrompt
    alternative_variations: List[PentagramPrompt]
    satirical_approach: str
    target_vulnerability: str
    effectiveness_prediction: float
    generation_metadata: Dict[str, Any]

class SatiricalPromptAgent(AgentBase):
    """
    Advanced satirical prompt generation agent using the Pentagram Framework.
    
    This agent transforms brand vulnerability analysis into targeted satirical
    prompts designed to expose corporate contradictions through visual metaphor
    and symbolic representation.
    """
    
    def __init__(self, agent_config: Dict[str, Any] = None):
        super().__init__(agent_config)
        
        # Generation configuration
        self.satirical_intensity = self.config.get('satirical_intensity', 'medium')
        self.creativity_level = self.config.get('creativity_level', 0.8)
        
        # Satirical approach templates
        self.satirical_approaches = {
            'contradiction_expose': {
                'description': 'Direct exposure of brand contradictions',
                'visual_style': 'Split-screen reality vs marketing',
                'tone': 'Sharp contrast revelation'
            },
            'buzzword_deflation': {
                'description': 'Deflating corporate buzzwords through literal interpretation',
                'visual_style': 'Absurdist literal translation',
                'tone': 'Playful absurdity'
            },
            'aspiration_mockery': {
                'description': 'Mocking unrealistic corporate aspirations',
                'visual_style': 'Exaggerated corporate utopia',
                'tone': 'Satirical overstatement'
            }
        }
        
        # Visual metaphor libraries
        self.metaphor_library = {
            'innovation_washing': [
                'hamster wheel labeled "innovation"',
                'recycling bin full of old ideas with "NEW" stickers',
                'innovation theater with empty seats',
                'copy machine producing "original" ideas'
            ],
            'customer_centricity_claims': [
                'customer service maze with no exit',
                'customer-first podium facing away from customers',
                'customer service rep behind bulletproof glass',
                'customer journey obstacle course'
            ],
            'simplicity_claims': [
                'simple button connected to massive machine',
                'minimalist facade hiding complex backend',
                'one-click solution requiring PhD manual',
                'elegant swan with frantic underwater paddling'
            ],
            'corporate_speak_overload': [
                'babel tower made of buzzwords',
                'translator converting human speech to corporate speak',
                'executive speaking in word salad',
                'buzzword bingo card as business plan'
            ]
        }
        
        # Environmental context options
        self.environmental_contexts = {
            'corporate_boardroom': 'sterile corporate boardroom with floor-to-ceiling windows',
            'startup_office': 'hip startup office with exposed brick and ping pong tables',
            'customer_service_center': 'busy call center with cubicles',
            'tech_conference': 'modern tech conference stage with LED screens',
            'office_kitchen': 'corporate break room with motivational posters',
            'zoom_meeting': 'video conference grid with participants in boxes'
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Generate satirical prompts using the Pentagram Framework.
        """
        
        start_time = time.time()
        
        if not self.validate_input(input_data):
            return AgentResponse(
                success=False,
                error_message="Invalid input: brand_analysis is required",
                execution_time=time.time() - start_time
            )
        
        brand_analysis = input_data['brand_analysis']
        style_preference = input_data.get('style_preference', 'contradiction_expose')
        output_variations = input_data.get('output_variations', 3)
        satirical_intensity = input_data.get('satirical_intensity', self.satirical_intensity)
        
        try:
            logger.info(f"Generating satirical prompts for: {brand_analysis.brand_name}")
            
            # Select primary vulnerability to target
            primary_vulnerability = self._select_primary_vulnerability(brand_analysis.satirical_vulnerabilities)
            
            # Generate primary prompt using Pentagram Framework
            primary_prompt = await self._generate_pentagram_prompt(
                brand_analysis, 
                primary_vulnerability, 
                style_preference,
                satirical_intensity
            )
            
            # Generate alternative variations
            alternative_prompts = []
            for i in range(output_variations - 1):  # -1 because we already have primary
                alt_prompt = await self._generate_alternative_prompt(
                    brand_analysis,
                    primary_vulnerability,
                    style_preference,
                    i
                )
                alternative_prompts.append(alt_prompt)
            
            # Predict effectiveness
            effectiveness = self._predict_prompt_effectiveness(primary_prompt, brand_analysis)
            
            # Create result
            result = SatiricalPromptResult(
                primary_prompt=primary_prompt,
                alternative_variations=alternative_prompts,
                satirical_approach=style_preference,
                target_vulnerability=primary_vulnerability['category'],
                effectiveness_prediction=effectiveness,
                generation_metadata={
                    'brand_name': brand_analysis.brand_name,
                    'vulnerabilities_analyzed': len(brand_analysis.satirical_vulnerabilities),
                    'satirical_intensity': satirical_intensity,
                    'style_preference': style_preference
                }
            )
            
            execution_time = time.time() - start_time
            logger.info(f"Satirical prompt generation completed in {execution_time:.2f}s")
            
            return AgentResponse(
                success=True,
                data={
                    'primary_prompt': primary_prompt,
                    'alternative_variations': alternative_prompts,
                    'satirical_approach': style_preference,
                    'target_vulnerability': primary_vulnerability['category'],
                    'effectiveness_prediction': effectiveness
                },
                execution_time=execution_time,
                metadata={
                    'prompts_generated': len(alternative_prompts) + 1,
                    'target_vulnerability': primary_vulnerability['category'],
                    'effectiveness_score': effectiveness
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Satirical prompt generation failed: {str(e)}")
            
            return AgentResponse(
                success=False,
                error_message=f"Generation error: {str(e)}",
                execution_time=execution_time
            )
    
    def _select_primary_vulnerability(self, vulnerabilities: List[Dict]) -> Dict:
        """Select the most promising vulnerability for satirical targeting"""
        
        if not vulnerabilities:
            # Create a generic vulnerability if none found
            return {
                'category': 'generic_corporate',
                'satirical_angle': 'Generic corporate contradiction',
                'intensity_rating': 0.5,
                'contradiction_evidence': ['Standard corporate behavior']
            }
        
        # Select vulnerability with highest intensity rating
        primary = max(vulnerabilities, key=lambda v: v.get('intensity_rating', 0))
        return primary
    
    async def _generate_pentagram_prompt(self, brand_analysis, vulnerability, style_preference, intensity) -> PentagramPrompt:
        """Generate a complete Pentagram Framework prompt"""
        
        # 1. Intent Clarity - What we're trying to expose
        intent_clarity = self._generate_intent_clarity(vulnerability, brand_analysis.brand_name)
        
        # 2. Symbolic Anchoring - Visual metaphor that embodies the contradiction
        symbolic_anchoring = self._generate_symbolic_anchoring(vulnerability, style_preference)
        
        # 3. Environmental Context - Where this contradiction plays out
        environmental_context = self._select_environmental_context(vulnerability, brand_analysis)
        
        # 4. Fidelity Specification - Technical and visual quality requirements
        fidelity_specification = self._generate_fidelity_specification(intensity)
        
        # 5. Audience Calibration - How sophisticated/subtle the satire should be
        audience_calibration = self._generate_audience_calibration(intensity, brand_analysis)
        
        return PentagramPrompt(
            intent_clarity=intent_clarity,
            symbolic_anchoring=symbolic_anchoring,
            environmental_context=environmental_context,
            fidelity_specification=fidelity_specification,
            audience_calibration=audience_calibration
        )
    
    def _generate_intent_clarity(self, vulnerability, brand_name) -> str:
        """Generate clear intent statement for what we're exposing"""
        
        category = vulnerability['category']
        
        intent_templates = {
            'innovation_washing': f"Expose {brand_name}'s innovation theater through visual contradiction",
            'customer_centricity_claims': f"Reveal the gap between {brand_name}'s customer-first claims and customer-hostile reality",
            'simplicity_claims': f"Unmask the complexity hiding behind {brand_name}'s simplicity marketing",
            'people_first_claims': f"Contrast {brand_name}'s people-first rhetoric with efficiency-first behavior",
            'corporate_speak_overload': f"Translate {brand_name}'s meaningless corporate jargon into visual absurdity",
            'sustainability_washing': f"Expose {brand_name}'s green marketing vs actual environmental impact"
        }
        
        return intent_templates.get(category, f"Expose {brand_name}'s core brand contradiction")
    
    def _generate_symbolic_anchoring(self, vulnerability, style_preference) -> str:
        """Generate powerful visual metaphor that anchors the satirical concept"""
        
        category = vulnerability['category']
        
        # Get metaphors for this category
        metaphors = self.metaphor_library.get(category, ['generic corporate facade'])
        
        # Select metaphor based on style preference
        if style_preference == 'contradiction_expose':
            # Use split-screen or before/after style metaphors
            return f"split-screen showing {metaphors[0]} vs reality"
        elif style_preference == 'buzzword_deflation':
            # Use literal interpretation metaphors
            return f"literal visualization of {metaphors[0]}"
        elif style_preference == 'aspiration_mockery':
            # Use exaggeration metaphors
            return f"exaggerated corporate utopia featuring {metaphors[0]}"
        else:
            return metaphors[0]
    
    def _select_environmental_context(self, vulnerability, brand_analysis) -> str:
        """Select appropriate environmental context for the satirical scene"""
        
        category = vulnerability['category']
        
        # Match environment to vulnerability type
        environment_mapping = {
            'innovation_washing': 'tech_conference',
            'customer_centricity_claims': 'customer_service_center',
            'simplicity_claims': 'startup_office',
            'people_first_claims': 'corporate_boardroom',
            'corporate_speak_overload': 'zoom_meeting',
            'sustainability_washing': 'corporate_boardroom'
        }
        
        env_key = environment_mapping.get(category, 'corporate_boardroom')
        return self.environmental_contexts[env_key]
    
    def _generate_fidelity_specification(self, intensity) -> str:
        """Generate technical and visual quality specifications"""
        
        intensity_specs = {
            'low': 'clean corporate photography style, professional lighting',
            'medium': 'high-contrast professional photography, dramatic corporate lighting, sharp detail',
            'high': 'ultra-high resolution corporate photography, cinematic lighting, hyperrealistic detail, magazine-quality finish'
        }
        
        return intensity_specs.get(intensity, intensity_specs['medium'])
    
    def _generate_audience_calibration(self, intensity, brand_analysis) -> str:
        """Generate audience sophistication and satirical subtlety calibration"""
        
        # Factor in brand's industry and sophistication
        brand_keywords = brand_analysis.brand_keywords
        tech_focused = any(keyword in ['technology', 'digital', 'platform', 'software'] for keyword in brand_keywords)
        
        if intensity == 'low':
            return 'general business audience, subtle satirical elements'
        elif intensity == 'medium':
            if tech_focused:
                return 'tech-savvy business audience, moderate satirical intensity with industry-specific references'
            else:
                return 'business-aware audience, clear satirical intent without being heavy-handed'
        else:  # high
            if tech_focused:
                return 'sophisticated tech industry audience, sharp satirical critique with insider knowledge'
            else:
                return 'business-sophisticated audience, bold satirical statement with corporate culture awareness'
    
    async def _generate_alternative_prompt(self, brand_analysis, vulnerability, style_preference, variation_index) -> PentagramPrompt:
        """Generate alternative prompt variations"""
        
        # Create variations by changing different elements
        if variation_index == 0:
            # Variation 1: Different symbolic anchoring
            alt_vulnerability = vulnerability.copy()
            alt_vulnerability['category'] = vulnerability['category']
            
            return await self._generate_pentagram_prompt(
                brand_analysis, 
                alt_vulnerability, 
                'buzzword_deflation',  # Different style
                self.satirical_intensity
            )
        
        else:
            # Variation 2: Different environmental context
            alt_vulnerability = vulnerability.copy()
            
            return await self._generate_pentagram_prompt(
                brand_analysis, 
                alt_vulnerability, 
                'aspiration_mockery',  # Different style
                self.satirical_intensity
            )
    
    def _predict_prompt_effectiveness(self, prompt: PentagramPrompt, brand_analysis) -> float:
        """Predict how effective this prompt will be at exposing contradictions"""
        
        effectiveness_score = 0.5  # Base score
        
        # Factor in vulnerability intensity
        vulnerabilities = brand_analysis.satirical_vulnerabilities
        if vulnerabilities:
            avg_intensity = sum(v.get('intensity_rating', 0.5) for v in vulnerabilities) / len(vulnerabilities)
            effectiveness_score += (avg_intensity * 0.3)
        
        # Factor in brand authenticity score (lower = more effective satire)
        authenticity_score = brand_analysis.authenticity_score
        effectiveness_score += ((1.0 - authenticity_score) * 0.2)
        
        # Factor in prompt specificity (longer, more detailed prompts tend to be more effective)
        prompt_length = len(prompt.compile_full_prompt())
        if prompt_length > 200:
            effectiveness_score += 0.1
        
        # Ensure score stays within bounds
        return min(1.0, max(0.0, effectiveness_score))
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate that we have brand analysis to work with"""
        return (input_data is not None and 
                'brand_analysis' in input_data and 
                input_data['brand_analysis'] is not None)
