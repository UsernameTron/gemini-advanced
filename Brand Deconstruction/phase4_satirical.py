# Phase 4: Satirical Prompt Generation with Pentagram Framework
# File: agents/satirical_generator.py

import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from core.base_agents import AgentBase, AgentResponse
from agents.brand_analyzer import BrandProfile
import time

@dataclass
class PentagramPrompt:
    """Structure for complete Pentagram Framework prompts"""
    intent_clarity: str          # What narrative punch are we delivering?
    fidelity_pass: str          # Technical specifications for quality
    symbolic_anchoring: str      # Metaphor and mood elements
    environmental_context: str   # Scene logic and setting
    brand_world_constraints: str # What NOT to include for authenticity
    
    def compile_full_prompt(self) -> str:
        """Combine all pentagram elements into a single coherent prompt"""
        return f"{self.intent_clarity}. {self.fidelity_pass}. {self.symbolic_anchoring}. {self.environmental_context}. {self.brand_world_constraints}"

@dataclass
class SatiricalConcept:
    """Core satirical concept before pentagram application"""
    primary_target: str          # Main contradiction or vulnerability
    satirical_angle: str         # How we're approaching the critique
    visual_metaphor: str         # Central metaphorical concept
    irony_mechanism: str         # How the irony reveals itself
    emotional_impact: str        # What feeling we want to evoke

class SatiricalPromptAgent(AgentBase):
    """
    Advanced agent for generating satirical prompts using the Pentagram Framework.
    
    This agent transforms brand psychological analysis into cutting visual satirical
    content. It specializes in the "controlled detonation" approach - precision 
    strikes that expose corporate pretension through visual contradiction.
    """
    
    def __init__(self, agent_id: str, agent_type: str, config: Dict):
        super().__init__(agent_id, agent_type, config)
        
        # Satirical style templates based on different approaches
        self.satirical_templates = {
            'contradiction_expose': {
                'description': 'Reveal gaps between claims and reality',
                'visual_strategy': 'juxtaposition of aspiration vs reality',
                'emotional_target': 'cognitive dissonance'
            },
            'buzzword_deflation': {
                'description': 'Render corporate speak absurd through literal interpretation',
                'visual_strategy': 'surreal literalization of metaphors',
                'emotional_target': 'amused recognition'
            },
            'aspiration_mockery': {
                'description': 'Expose the gap between customer dreams and actual outcomes',
                'visual_strategy': 'before/after or expectation vs reality',
                'emotional_target': 'rueful laughter'
            },
            'authority_undermining': {
                'description': 'Reveal manufactured expertise and false credentials',
                'visual_strategy': 'authority figures in ridiculous contexts',
                'emotional_target': 'skeptical amusement'
            },
            'scale_absurdity': {
                'description': 'Expose the absurdity of mass personalization claims',
                'visual_strategy': 'factory-produced "uniqueness"',
                'emotional_target': 'ironic awareness'
            }
        }
        
        # Visual metaphor libraries for different contradiction types
        self.metaphor_libraries = {
            'accessibility_vs_luxury': [
                'gold-plated cardboard',
                'diamond-encrusted thrift store tags',
                'velvet ropes around park benches',
                'crystal chandeliers in food banks'
            ],
            'innovation_vs_conventional': [
                'revolutionary wheels (reinventing the wheel)',
                'breakthrough rectangles (reinventing boxes)',
                'disruptive breathing (reinventing air)',
                'game-changing gravity (reinventing physics)'
            ],
            'personal_vs_scale': [
                'assembly line handwritten letters',
                'mass-produced snowflakes',
                'factory-made artisanal bread',
                'automated personal touches'
            ],
            'simplicity_vs_complexity': [
                'simple 47-step process',
                'minimalist instruction manuals',
                'easy-to-use Swiss Army chainsaw',
                'streamlined complexity'
            ]
        }
        
        # Environmental contexts that enhance satirical impact
        self.satirical_environments = {
            'corporate_sterile': 'pristine corporate boardroom with subtle cracks in the facade',
            'consumer_reality': 'cluttered real-world environment showing actual usage',
            'aspiration_space': 'impossibly perfect lifestyle setting with reality bleeding through',
            'manufacturing_truth': 'behind-the-scenes production revealing the machinery',
            'temporal_decay': 'future consequences of present claims'
        }
        
        # Fidelity specifications optimized for different satirical impacts
        self.fidelity_presets = {
            'hyperreal_expose': '8K photorealistic, hyperdetailed textures, studio lighting that reveals every flaw',
            'surreal_metaphor': 'photorealistic surrealism, Dalí-esque precision with impossible elements',
            'documentary_style': 'documentary photography aesthetic, natural lighting, candid imperfection',
            'advertising_parody': 'commercial photography perfection with subtle wrongness',
            'editorial_illustration': 'New Yorker cover style sophistication with sharp satirical edge'
        }
    
    async def execute(self, input_data: Dict) -> AgentResponse:
        """
        Transform brand analysis into cutting satirical prompts using Pentagram Framework.
        
        This is where psychological insights become visual ammunition for corporate critique.
        """
        
        start_time = time.time()
        
        try:
            brand_profile = input_data.get('brand_analysis')
            if not isinstance(brand_profile, BrandProfile):
                return AgentResponse(
                    success=False,
                    result=None,
                    agent_type=self.agent_type,
                    error_message="Invalid input: expected BrandProfile object"
                )
            
            satirical_intensity = input_data.get('satirical_intensity', 'medium')
            style_preference = input_data.get('style_preference', 'contradiction_expose')
            
            self.log_execution("Starting satirical prompt generation",
                             f"Target authenticity: {brand_profile.authenticity_score:.2f}, "
                             f"Vulnerabilities: {len(brand_profile.satirical_vulnerabilities)}")
            
            # Step 1: Identify the strongest satirical angle
            satirical_concept = await self._identify_primary_satirical_concept(
                brand_profile, satirical_intensity
            )
            
            # Step 2: Develop the core visual metaphor
            visual_metaphor = self._develop_visual_metaphor(satirical_concept, brand_profile)
            
            # Step 3: Apply Pentagram Framework
            pentagram_prompt = await self._apply_pentagram_framework(
                satirical_concept, visual_metaphor, brand_profile, style_preference
            )
            
            # Step 4: Generate alternative variations
            alternative_prompts = await self._generate_alternative_variations(
                satirical_concept, brand_profile
            )
            
            execution_time = time.time() - start_time
            
            result = {
                'primary_prompt': pentagram_prompt,
                'satirical_concept': satirical_concept,
                'alternative_variations': alternative_prompts,
                'brand_context': {
                    'company_positioning': brand_profile.primary_positioning,
                    'target_aspiration': brand_profile.target_audience_aspiration,
                    'authenticity_score': brand_profile.authenticity_score
                }
            }
            
            self.log_execution("Satirical prompt generation completed",
                             f"Generated {len(alternative_prompts) + 1} variations")
            
            return AgentResponse(
                success=True,
                result=result,
                agent_type=self.agent_type,
                execution_time=execution_time,
                metadata={
                    'satirical_intensity': satirical_intensity,
                    'primary_target': satirical_concept.primary_target
                }
            )
            
        except Exception as e:
            self.log_execution("Satirical generation failed", str(e))
            return AgentResponse(
                success=False,
                result=None,
                agent_type=self.agent_type,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    async def _identify_primary_satirical_concept(self, profile: BrandProfile, 
                                                intensity: str) -> SatiricalConcept:
        """
        Analyze brand profile to identify the most promising satirical attack vector.
        
        This method prioritizes contradictions and vulnerabilities based on their
        potential for visual satirical impact and emotional resonance.
        """
        
        # Rank vulnerabilities by satirical potential
        vulnerability_scores = {}
        
        for vulnerability in profile.satirical_vulnerabilities:
            score = 0
            
            # Buzzword overuse is immediately satirical
            if 'overuses' in vulnerability.lower():
                score += 40
            
            # Aspiration-reality gaps are gold mines
            if 'gap between' in vulnerability.lower():
                score += 35
            
            # Power word desperation suggests easy targets
            if 'aggressive' in vulnerability.lower() and 'power' in vulnerability.lower():
                score += 30
            
            # Innovation contradictions are visually rich
            if 'innovation' in vulnerability.lower() and 'jargon' in vulnerability.lower():
                score += 32
            
            vulnerability_scores[vulnerability] = score
        
        # Select the highest-scoring vulnerability as our primary target
        if vulnerability_scores:
            primary_vulnerability = max(vulnerability_scores, key=vulnerability_scores.get)
        else:
            # Fallback to general authenticity critique
            primary_vulnerability = f"Low authenticity score ({profile.authenticity_score:.2f}) suggests manufactured brand identity"
        
        # Determine satirical angle based on vulnerability type
        if 'overuses' in primary_vulnerability:
            angle = 'buzzword_deflation'
            metaphor = 'literal interpretation of corporate speak'
        elif 'gap between' in primary_vulnerability:
            angle = 'contradiction_expose'
            metaphor = 'visual juxtaposition of claim vs reality'
        elif 'aggressive' in primary_vulnerability:
            angle = 'authority_undermining'
            metaphor = 'desperate marketing as carnival barking'
        else:
            angle = 'aspiration_mockery'
            metaphor = 'customer dreams vs corporate profit motives'
        
        # Define the irony mechanism
        irony_mechanisms = {
            'buzzword_deflation': 'Corporate metaphors rendered literally reveal their emptiness',
            'contradiction_expose': 'Side-by-side comparison makes contradictions undeniable',
            'authority_undermining': 'Authoritative claims placed in ridiculous contexts',
            'aspiration_mockery': 'Customer aspirations shown as corporate products'
        }
        
        return SatiricalConcept(
            primary_target=primary_vulnerability,
            satirical_angle=angle,
            visual_metaphor=metaphor,
            irony_mechanism=irony_mechanisms[angle],
            emotional_impact=self.satirical_templates[angle]['emotional_target']
        )
    
    def _develop_visual_metaphor(self, concept: SatiricalConcept, 
                               profile: BrandProfile) -> str:
        """
        Create specific visual metaphor based on the satirical concept and brand analysis.
        
        This method translates abstract brand contradictions into concrete visual scenarios
        that will be immediately recognizable and impactful to viewers.
        """
        
        # Extract key contradiction elements from the brand profile
        positioning = profile.primary_positioning.lower()
        aspiration = profile.target_audience_aspiration.lower()
        
        # Match contradiction patterns to metaphor libraries
        metaphor_candidates = []
        
        # Check for accessibility vs luxury contradiction
        if any(word in positioning for word in ['affordable', 'accessible', 'everyone']) and \
           any(word in positioning for word in ['premium', 'luxury', 'exclusive']):
            metaphor_candidates.extend(self.metaphor_libraries['accessibility_vs_luxury'])
        
        # Check for innovation vs conventional contradiction
        if 'innovation' in concept.primary_target.lower() and 'jargon' in concept.primary_target.lower():
            metaphor_candidates.extend(self.metaphor_libraries['innovation_vs_conventional'])
        
        # Check for personal vs scale contradiction
        if any(word in aspiration for word in ['personal', 'individual', 'custom']) and \
           'scale' in concept.primary_target.lower():
            metaphor_candidates.extend(self.metaphor_libraries['personal_vs_scale'])
        
        # Select the most appropriate metaphor
        if metaphor_candidates:
            return random.choice(metaphor_candidates)
        else:
            # Create custom metaphor based on specific brand elements
            return self._create_custom_metaphor(concept, profile)
    
    def _create_custom_metaphor(self, concept: SatiricalConcept, profile: BrandProfile) -> str:
        """Create a custom visual metaphor when standard templates don't fit"""
        
        # Extract buzzwords for literal interpretation
        if profile.contradiction_flags.buzzword_overuse:
            top_buzzword = max(profile.contradiction_flags.buzzword_overuse.items(), 
                             key=lambda x: x[1])[0]
            return f"literal interpretation of '{top_buzzword}' as physical object in inappropriate context"
        
        # Use positioning claims
        positioning = profile.primary_positioning
        return f"{positioning} rendered as carnival attraction with hidden machinery visible"
    
    async def _apply_pentagram_framework(self, concept: SatiricalConcept, 
                                       visual_metaphor: str, profile: BrandProfile,
                                       style_preference: str) -> PentagramPrompt:
        """
        Apply the complete Pentagram Framework to create a structured satirical prompt.
        
        This method ensures every element serves the satirical intent while maintaining
        the technical quality needed for impactful visual content.
        """
        
        # 1. Intent Clarity - What narrative punch are we delivering?
        intent = f"Expose the absurdity of {profile.primary_positioning} through {concept.satirical_angle}"
        
        # 2. Fidelity Pass - Technical specifications optimized for satirical impact
        if concept.satirical_angle == 'buzzword_deflation':
            fidelity = self.fidelity_presets['surreal_metaphor']
        elif concept.satirical_angle == 'contradiction_expose':
            fidelity = self.fidelity_presets['hyperreal_expose']
        elif concept.satirical_angle == 'aspiration_mockery':
            fidelity = self.fidelity_presets['advertising_parody']
        else:
            fidelity = self.fidelity_presets['editorial_illustration']
        
        # 3. Symbolic Anchoring - Metaphor and mood elements
        symbolic_elements = [
            visual_metaphor,
            f"mood: {concept.emotional_impact}",
            f"symbolic tension between {profile.primary_positioning} and {profile.target_audience_aspiration}"
        ]
        symbolic_anchoring = ", ".join(symbolic_elements)
        
        # 4. Environmental Context - Scene logic and setting
        if 'luxury' in profile.primary_positioning.lower():
            environment = self.satirical_environments['aspiration_space']
        elif 'innovation' in profile.primary_positioning.lower():
            environment = self.satirical_environments['manufacturing_truth']
        elif 'personal' in profile.target_audience_aspiration.lower():
            environment = self.satirical_environments['consumer_reality']
        else:
            environment = self.satirical_environments['corporate_sterile']
        
        # 5. Brand World Constraints - What NOT to include for authenticity
        constraints = self._generate_brand_constraints(profile)
        
        return PentagramPrompt(
            intent_clarity=intent,
            fidelity_pass=fidelity,
            symbolic_anchoring=symbolic_anchoring,
            environmental_context=environment,
            brand_world_constraints=constraints
        )
    
    def _generate_brand_constraints(self, profile: BrandProfile) -> str:
        """
        Define what to exclude to maintain satirical authenticity.
        
        Constraints ensure our satire stays grounded in the brand's actual messaging
        rather than becoming generic corporate mockery.
        """
        
        constraints = []
        
        # Avoid contradicting the basic satirical premise
        constraints.append(f"no genuine {profile.primary_positioning} elements that would undermine the critique")
        
        # Maintain realistic corporate aesthetics
        constraints.append("maintain corporate visual language to enhance authenticity")
        
        # Avoid heavy-handed satirical elements
        constraints.append("subtle wrongness rather than obvious parody")
        
        # Brand-specific constraints based on analysis
        if profile.authenticity_score < 0.3:
            constraints.append("emphasize manufactured perfection over organic authenticity")
        
        if profile.contradiction_flags.buzzword_overuse:
            constraints.append("incorporate actual buzzwords used by the brand")
        
        return "; ".join(constraints)
    
    async def _generate_alternative_variations(self, concept: SatiricalConcept, 
                                             profile: BrandProfile) -> List[PentagramPrompt]:
        """
        Generate alternative prompt variations to provide creative options.
        
        Different variations explore the same satirical concept through different
        visual and stylistic approaches, giving users creative flexibility.
        """
        
        variations = []
        
        # Variation 1: Different environmental context
        alt_environments = list(self.satirical_environments.values())
        alt_environment = random.choice([env for env in alt_environments 
                                       if env != concept.visual_metaphor])
        
        variation_1 = PentagramPrompt(
            intent_clarity=f"Alternative perspective on {concept.primary_target}",
            fidelity_pass=self.fidelity_presets['documentary_style'],
            symbolic_anchoring=f"{concept.visual_metaphor}, documentary realism mood",
            environmental_context=alt_environment,
            brand_world_constraints="raw, unpolished reality bleeding through corporate presentation"
        )
        variations.append(variation_1)
        
        # Variation 2: Different satirical angle if multiple vulnerabilities exist
        if len(profile.satirical_vulnerabilities) > 1:
            secondary_vulnerability = profile.satirical_vulnerabilities[1]
            variation_2 = PentagramPrompt(
                intent_clarity=f"Expose {secondary_vulnerability}",
                fidelity_pass=self.fidelity_presets['advertising_parody'],
                symbolic_anchoring=f"commercial photography aesthetic with {secondary_vulnerability} revealed",
                environmental_context=self.satirical_environments['corporate_sterile'],
                brand_world_constraints="maintain advertising perfection while revealing underlying contradictions"
            )
            variations.append(variation_2)
        
        # Variation 3: Time-based perspective (before/after or future consequences)
        variation_3 = PentagramPrompt(
            intent_clarity=f"Show long-term consequences of {profile.primary_positioning}",
            fidelity_pass=self.fidelity_presets['editorial_illustration'],
            symbolic_anchoring=f"temporal decay, {concept.visual_metaphor} showing wear and age",
            environmental_context=self.satirical_environments['temporal_decay'],
            brand_world_constraints="realistic aging and consequences of present claims"
        )
        variations.append(variation_3)
        
        return variations

# File: examples/test_satirical_generator.py

import asyncio
from core.base_agents import AgentManager
from agents import register_scraping_agents
from agents.brand_analyzer import BrandAnalysisAgent
from agents.satirical_generator import SatiricalPromptAgent
from config.agent_config import AGENT_CONFIGS

async def test_complete_satirical_pipeline():
    """
    Test the complete pipeline from URL to satirical prompts.
    This demonstrates the full Brand Deconstruction Engine in action.
    """
    
    # Set up the agent manager with all our specialized agents
    agent_manager = AgentManager()
    register_scraping_agents(agent_manager)
    agent_manager.register_agent_type('brand_analyzer', BrandAnalysisAgent, AGENT_CONFIGS['brand_analyzer'])
    agent_manager.register_agent_type('satirical_generator', SatiricalPromptAgent, AGENT_CONFIGS['satirical_generator'])
    
    # Test URL - replace with any corporate website
    test_url = 'https://www.salesforce.com'
    
    print(f"🎯 Testing complete satirical pipeline with: {test_url}")
    print("=" * 60)
    
    # Step 1: Scrape brand content
    print("\n📡 Step 1: Scraping brand content...")
    scraper = agent_manager.create_agent('brand_scraper')
    scrape_result = await scraper.execute({'url': test_url})
    
    if not scrape_result.success:
        print(f"❌ Scraping failed: {scrape_result.error_message}")
        return
    
    print(f"✅ Scraping completed ({scrape_result.execution_time:.2f}s)")
    
    # Step 2: Analyze brand psychology
    print("\n🧠 Step 2: Analyzing brand psychology...")
    analyzer = agent_manager.create_agent('brand_analyzer')
    analysis_result = await analyzer.execute({'scraped_content': scrape_result.result})
    
    if not analysis_result.success:
        print(f"❌ Analysis failed: {analysis_result.error_message}")
        return
    
    brand_profile = analysis_result.result
    print(f"✅ Analysis completed ({analysis_result.execution_time:.2f}s)")
    print(f"   Authenticity Score: {brand_profile.authenticity_score:.2f}")
    print(f"   Vulnerabilities Found: {len(brand_profile.satirical_vulnerabilities)}")
    
    # Step 3: Generate satirical prompts
    print("\n🎨 Step 3: Generating satirical prompts...")
    generator = agent_manager.create_agent('satirical_generator')
    satirical_result = await generator.execute({
        'brand_analysis': brand_profile,
        'satirical_intensity': 'high',
        'style_preference': 'contradiction_expose'
    })
    
    if satirical_result.success:
        result = satirical_result.result
        print(f"✅ Satirical generation completed ({satirical_result.execution_time:.2f}s)")
        print(f"\n🎯 Primary Satirical Target:")
        print(f"   {result['satirical_concept'].primary_target}")
        print(f"\n📝 Primary Pentagram Prompt:")
        print(f"   {result['primary_prompt'].compile_full_prompt()}")
        print(f"\n🔄 Alternative Variations: {len(result['alternative_variations'])}")
        
        # Show one alternative
        if result['alternative_variations']:
            print(f"\n📝 Alternative Approach:")
            print(f"   {result['alternative_variations'][0].compile_full_prompt()}")
            
    else:
        print(f"❌ Satirical generation failed: {satirical_result.error_message}")

if __name__ == "__main__":
    asyncio.run(test_complete_satirical_pipeline())