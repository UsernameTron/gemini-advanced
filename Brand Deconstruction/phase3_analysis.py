# Phase 3: Brand Analysis and Profiling Agent
# File: agents/brand_analyzer.py

import re
import json
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from collections import Counter
import time
import asyncio
from core.base_agents import AgentBase, AgentResponse
from agents.brand_scraper import BrandContent

@dataclass
class VoiceCharacteristics:
    """Structure for analyzing brand voice patterns"""
    tone_indicators: Dict[str, float]  # authoritative, friendly, urgent, etc.
    vocabulary_patterns: Dict[str, int]  # word frequency analysis
    sentence_complexity: float  # average words per sentence
    emotional_triggers: List[str]  # words designed to evoke feelings
    power_words: List[str]  # action-oriented, compelling language
    jargon_density: float  # technical vs. accessible language ratio

@dataclass
class PsychologicalTactics:
    """Structure for analyzing psychological manipulation in brand messaging"""
    aspiration_triggers: List[str]  # language targeting customer desires
    social_proof_elements: List[str]  # testimonials, numbers, authority
    scarcity_urgency: List[str]  # limited time, exclusive offers
    authority_positioning: List[str]  # expertise claims, credentials
    community_belonging: List[str]  # "join us", "our community"
    fear_uncertainty_doubt: List[str]  # problems they claim to solve

@dataclass
class ContradictionFlags:
    """Structure for identifying brand messaging contradictions"""
    aspiration_reality_gaps: List[Tuple[str, str]]  # (claim, reality_indicator)
    buzzword_overuse: Dict[str, int]  # overused terms that signal emptiness
    tone_mismatches: List[str]  # inconsistent voice across sections
    authenticity_signals: Dict[str, float]  # genuine vs. manufactured feel

@dataclass
class BrandProfile:
    """Complete psychological profile of a brand's messaging strategy"""
    voice_characteristics: VoiceCharacteristics
    psychological_tactics: PsychologicalTactics
    contradiction_flags: ContradictionFlags
    authenticity_score: float  # 0-1 scale of perceived authenticity
    satirical_vulnerabilities: List[str]  # prime targets for satirical attack
    primary_positioning: str  # main brand identity claim
    target_audience_aspiration: str  # what customers want to become

class BrandAnalysisAgent(AgentBase):
    """
    Advanced agent for psychological analysis of brand content.
    
    This agent understands the rhetorical strategies companies use to position
    themselves and identifies the gaps between their claims and indicators of reality.
    It's designed to feed our satirical prompt generator with precise ammunition.
    """
    
    def __init__(self, agent_id: str, agent_type: str, config: Dict):
        super().__init__(agent_id, agent_type, config)
        
        # Emotional trigger words that brands use to manipulate feelings
        self.emotional_triggers = {
            'aspiration': ['transform', 'elevate', 'empower', 'unlock', 'achieve', 'realize'],
            'urgency': ['now', 'today', 'immediately', 'instant', 'fast', 'quick'],
            'exclusivity': ['exclusive', 'premium', 'luxury', 'elite', 'select', 'special'],
            'security': ['safe', 'secure', 'protected', 'guaranteed', 'trusted', 'reliable'],
            'innovation': ['revolutionary', 'breakthrough', 'cutting-edge', 'innovative', 'advanced']
        }
        
        # Power words that signal aggressive marketing
        self.power_words = [
            'revolutionary', 'game-changing', 'disruptive', 'innovative', 'breakthrough',
            'ultimate', 'premium', 'exclusive', 'guaranteed', 'proven', 'secret',
            'instant', 'effortless', 'powerful', 'advanced', 'superior'
        ]
        
        # Buzzwords that often signal empty marketing speak
        self.buzzword_indicators = [
            'synergy', 'leverage', 'optimize', 'streamline', 'maximize', 'enhance',
            'solution', 'ecosystem', 'platform', 'framework', 'methodology'
        ]
        
        # Tone indicators help us understand brand personality
        self.tone_patterns = {
            'authoritative': r'\b(we are|we provide|our expertise|industry leader|proven)\b',
            'friendly': r'\b(we love|excited to|happy to|together|community)\b',
            'urgent': r'\b(don\'t wait|limited time|act now|hurry|before it\'s too late)\b',
            'aspirational': r'\b(imagine|dream|achieve|become|transform|elevate)\b',
            'technical': r'\b(algorithm|methodology|framework|architecture|system)\b'
        }
    
    async def execute(self, input_data: Dict) -> AgentResponse:
        """
        Main execution method that transforms brand content into psychological insights.
        
        This is where we move from raw text to strategic understanding of what
        the brand is trying to accomplish psychologically with their messaging.
        """
        
        start_time = time.time()
        
        try:
            brand_content = input_data.get('scraped_content')
            if not isinstance(brand_content, BrandContent):
                return AgentResponse(
                    success=False,
                    result=None,
                    agent_type=self.agent_type,
                    error_message="Invalid input: expected BrandContent object"
                )
            
            self.log_execution("Starting brand psychological analysis", 
                             f"Company: {brand_content.metadata.get('company_name', 'Unknown')}")
            
            # Step 1: Analyze voice characteristics across all content
            voice_analysis = await self._analyze_voice_characteristics(brand_content)
            
            # Step 2: Identify psychological manipulation tactics
            psychological_analysis = await self._analyze_psychological_tactics(brand_content)
            
            # Step 3: Flag contradictions and authenticity issues
            contradiction_analysis = await self._analyze_contradictions(brand_content)
            
            # Step 4: Calculate overall authenticity score
            authenticity_score = self._calculate_authenticity_score(
                voice_analysis, psychological_analysis, contradiction_analysis
            )
            
            # Step 5: Identify prime satirical targets
            satirical_vulnerabilities = self._identify_satirical_vulnerabilities(
                voice_analysis, psychological_analysis, contradiction_analysis
            )
            
            # Step 6: Extract primary positioning and target aspiration
            positioning_analysis = self._analyze_positioning_strategy(brand_content)
            
            # Compile complete brand profile
            brand_profile = BrandProfile(
                voice_characteristics=voice_analysis,
                psychological_tactics=psychological_analysis,
                contradiction_flags=contradiction_analysis,
                authenticity_score=authenticity_score,
                satirical_vulnerabilities=satirical_vulnerabilities,
                primary_positioning=positioning_analysis['primary_positioning'],
                target_audience_aspiration=positioning_analysis['target_aspiration']
            )
            
            execution_time = time.time() - start_time
            
            self.log_execution("Brand analysis completed", 
                             f"Authenticity score: {authenticity_score:.2f}, "
                             f"Vulnerabilities found: {len(satirical_vulnerabilities)}")
            
            return AgentResponse(
                success=True,
                result=brand_profile,
                agent_type=self.agent_type,
                execution_time=execution_time,
                metadata={
                    'analysis_depth': self.config.get('analysis_depth', 'standard'),
                    'content_sections_analyzed': len(asdict(brand_content))
                }
            )
            
        except Exception as e:
            self.log_execution("Brand analysis failed", str(e))
            return AgentResponse(
                success=False,
                result=None,
                agent_type=self.agent_type,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    async def _analyze_voice_characteristics(self, content: BrandContent) -> VoiceCharacteristics:
        """
        Analyze the linguistic patterns that reveal brand personality.
        
        This method examines how the brand speaks, not just what they say.
        Voice characteristics reveal a lot about how a company sees itself
        and how they want to be perceived.
        """
        
        # Combine all text content for comprehensive analysis
        all_text = self._combine_all_content(content)
        
        # Analyze tone indicators using regex patterns
        tone_scores = {}
        for tone, pattern in self.tone_patterns.items():
            matches = len(re.findall(pattern, all_text, re.IGNORECASE))
            tone_scores[tone] = matches / max(1, len(all_text.split())) * 100
        
        # Analyze vocabulary patterns
        words = re.findall(r'\b[a-zA-Z]+\b', all_text.lower())
        word_freq = Counter(words)
        
        # Calculate sentence complexity
        sentences = re.split(r'[.!?]+', all_text)
        sentence_lengths = [len(sentence.split()) for sentence in sentences if sentence.strip()]
        avg_sentence_length = sum(sentence_lengths) / max(1, len(sentence_lengths))
        
        # Identify emotional triggers present in the content
        found_emotional_triggers = []
        for category, triggers in self.emotional_triggers.items():
            for trigger in triggers:
                if trigger.lower() in all_text.lower():
                    found_emotional_triggers.append(f"{category}: {trigger}")
        
        # Identify power words being used
        found_power_words = [word for word in self.power_words 
                           if word.lower() in all_text.lower()]
        
        # Calculate jargon density (technical vs accessible language)
        technical_words = sum(1 for word in words if len(word) > 8 or word in self.buzzword_indicators)
        jargon_density = technical_words / max(1, len(words))
        
        return VoiceCharacteristics(
            tone_indicators=tone_scores,
            vocabulary_patterns=dict(word_freq.most_common(20)),
            sentence_complexity=avg_sentence_length,
            emotional_triggers=found_emotional_triggers,
            power_words=found_power_words,
            jargon_density=jargon_density
        )
    
    async def _analyze_psychological_tactics(self, content: BrandContent) -> PsychologicalTactics:
        """
        Identify the psychological strategies the brand uses to influence customers.
        
        This reveals the deeper manipulation tactics beyond surface-level messaging.
        Understanding these tactics helps us identify where the brand is most
        vulnerable to satirical critique.
        """
        
        all_text = self._combine_all_content(content)
        
        # Analyze aspiration triggers (what they want customers to become)
        aspiration_patterns = [
            r'become \w+', r'achieve \w+', r'transform your \w+', 
            r'unlock your \w+', r'realize your \w+'
        ]
        aspiration_triggers = []
        for pattern in aspiration_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            aspiration_triggers.extend(matches)
        
        # Social proof elements
        social_proof = []
        social_proof.extend(content.testimonials)  # Customer testimonials
        
        # Look for numbers and statistics used as proof
        number_claims = re.findall(r'\d+[%+]?\s*(?:customers?|users?|people|companies?)', 
                                 all_text, re.IGNORECASE)
        social_proof.extend(number_claims)
        
        # Scarcity and urgency tactics
        scarcity_patterns = [
            r'limited time', r'exclusive offer', r'while supplies last',
            r'only \d+ left', r'don\'t miss out', r'act now'
        ]
        scarcity_urgency = []
        for pattern in scarcity_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            scarcity_urgency.extend(matches)
        
        # Authority positioning claims
        authority_patterns = [
            r'industry leader', r'award[- ]winning', r'expert', r'proven',
            r'\d+ years? of experience', r'trusted by', r'certified'
        ]
        authority_positioning = []
        for pattern in authority_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            authority_positioning.extend(matches)
        
        # Community belonging language
        community_patterns = [
            r'join (?:us|our)', r'our community', r'become (?:part|member)',
            r'together we', r'we believe'
        ]
        community_belonging = []
        for pattern in community_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            community_belonging.extend(matches)
        
        # Fear, uncertainty, doubt tactics
        fud_patterns = [
            r'without \w+, you', r'don\'t let \w+ happen', r'protect yourself',
            r'avoid \w+', r'prevent \w+'
        ]
        fear_uncertainty_doubt = []
        for pattern in fud_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            fear_uncertainty_doubt.extend(matches)
        
        return PsychologicalTactics(
            aspiration_triggers=aspiration_triggers,
            social_proof_elements=social_proof,
            scarcity_urgency=scarcity_urgency,
            authority_positioning=authority_positioning,
            community_belonging=community_belonging,
            fear_uncertainty_doubt=fear_uncertainty_doubt
        )
    
    async def _analyze_contradictions(self, content: BrandContent) -> ContradictionFlags:
        """
        Identify contradictions and authenticity red flags in brand messaging.
        
        This is where we find the satirical gold - the gaps between what they
        claim and what they actually reveal about themselves through their
        language choices and positioning.
        """
        
        all_text = self._combine_all_content(content)
        
        # Analyze buzzword overuse (often signals substance deficit)
        words = re.findall(r'\b[a-zA-Z]+\b', all_text.lower())
        buzzword_count = {buzzword: words.count(buzzword.lower()) 
                         for buzzword in self.buzzword_indicators}
        buzzword_overuse = {k: v for k, v in buzzword_count.items() if v > 2}
        
        # Look for aspiration-reality gaps
        aspiration_reality_gaps = []
        
        # Claims of accessibility vs. premium positioning
        if any(word in all_text.lower() for word in ['affordable', 'accessible', 'everyone']) and \
           any(word in all_text.lower() for word in ['premium', 'luxury', 'exclusive']):
            aspiration_reality_gaps.append(
                ("Claims accessibility", "Positions as premium/exclusive")
            )
        
        # Innovation claims vs. buzzword density
        innovation_claims = sum(1 for word in ['innovative', 'revolutionary', 'breakthrough'] 
                              if word in all_text.lower())
        if innovation_claims > 3 and len(buzzword_overuse) > 3:
            aspiration_reality_gaps.append(
                ("Claims innovation", "High buzzword density suggests conventional thinking")
            )
        
        # Personal touch vs. scale claims
        if any(word in all_text.lower() for word in ['personal', 'individual', 'custom']) and \
           any(word in all_text.lower() for word in ['scale', 'thousands', 'millions']):
            aspiration_reality_gaps.append(
                ("Claims personal attention", "Emphasizes massive scale")
            )
        
        # Tone consistency analysis
        tone_mismatches = []
        hero_tone = self._analyze_section_tone(content.hero_sections)
        about_tone = self._analyze_section_tone(content.about_content)
        
        if abs(hero_tone.get('friendly', 0) - about_tone.get('friendly', 0)) > 20:
            tone_mismatches.append("Inconsistent friendliness between hero and about sections")
        
        # Authenticity signals analysis
        authenticity_signals = {
            'specific_details': len(re.findall(r'\b\d+\b', all_text)) / max(1, len(all_text.split())),
            'personal_pronouns': (all_text.lower().count('we ') + all_text.lower().count('our ')) / max(1, len(all_text.split())),
            'hedge_words': (all_text.lower().count('maybe') + all_text.lower().count('perhaps') + 
                          all_text.lower().count('might')) / max(1, len(all_text.split()))
        }
        
        return ContradictionFlags(
            aspiration_reality_gaps=aspiration_reality_gaps,
            buzzword_overuse=buzzword_overuse,
            tone_mismatches=tone_mismatches,
            authenticity_signals=authenticity_signals
        )
    
    def _analyze_section_tone(self, section_content: List[str]) -> Dict[str, float]:
        """Helper method to analyze tone for a specific content section"""
        if not section_content:
            return {}
        
        section_text = ' '.join(section_content)
        tone_scores = {}
        
        for tone, pattern in self.tone_patterns.items():
            matches = len(re.findall(pattern, section_text, re.IGNORECASE))
            tone_scores[tone] = matches / max(1, len(section_text.split())) * 100
        
        return tone_scores
    
    def _calculate_authenticity_score(self, voice: VoiceCharacteristics, 
                                    psychology: PsychologicalTactics, 
                                    contradictions: ContradictionFlags) -> float:
        """
        Calculate overall authenticity score based on analysis results.
        
        Lower scores indicate higher susceptibility to satirical critique.
        """
        
        # Start with neutral score
        score = 0.5
        
        # Penalize excessive buzzword usage
        if contradictions.buzzword_overuse:
            score -= min(0.2, len(contradictions.buzzword_overuse) * 0.05)
        
        # Penalize contradiction flags
        score -= len(contradictions.aspiration_reality_gaps) * 0.1
        score -= len(contradictions.tone_mismatches) * 0.05
        
        # Penalize excessive power words
        if len(voice.power_words) > 10:
            score -= 0.15
        
        # Reward specific details (authenticity signal)
        if contradictions.authenticity_signals.get('specific_details', 0) > 0.02:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _identify_satirical_vulnerabilities(self, voice: VoiceCharacteristics,
                                          psychology: PsychologicalTactics,
                                          contradictions: ContradictionFlags) -> List[str]:
        """
        Identify the most promising targets for satirical attack.
        
        These are the areas where the brand is most vulnerable to having
        their pretensions exposed through visual satire.
        """
        
        vulnerabilities = []
        
        # Buzzword overuse is prime satirical material
        for buzzword, count in contradictions.buzzword_overuse.items():
            if count > 3:
                vulnerabilities.append(f"Overuses '{buzzword}' ({count} times) - ripe for literal interpretation")
        
        # Aspiration-reality gaps are satirical gold
        for claim, reality in contradictions.aspiration_reality_gaps:
            vulnerabilities.append(f"Gap between {claim.lower()} and {reality.lower()}")
        
        # Excessive power words signal aggressive marketing
        if len(voice.power_words) > 8:
            vulnerabilities.append("Aggressive power word usage suggests desperation")
        
        # High jargon density with innovation claims
        if voice.jargon_density > 0.1 and any('innovation' in trigger for trigger in voice.emotional_triggers):
            vulnerabilities.append("High jargon density contradicts innovation claims")
        
        return vulnerabilities
    
    def _analyze_positioning_strategy(self, content: BrandContent) -> Dict[str, str]:
        """Extract the primary brand positioning and target customer aspiration"""
        
        # Analyze hero content for primary positioning
        hero_text = ' '.join(content.hero_sections)
        
        # Look for positioning statements
        positioning_patterns = [
            r'we are (?:the )?(\w+(?:\s+\w+)*)',
            r'(?:the )?(\w+(?:\s+\w+)*) (?:solution|platform|company)',
            r'leading (\w+(?:\s+\w+)*)'
        ]
        
        primary_positioning = "Unknown positioning"
        for pattern in positioning_patterns:
            matches = re.search(pattern, hero_text, re.IGNORECASE)
            if matches:
                primary_positioning = matches.group(1).strip()
                break
        
        # Analyze aspiration triggers for target customer desires
        all_aspirations = ' '.join(content.about_content + content.value_propositions)
        aspiration_patterns = [
            r'help you (\w+(?:\s+\w+)*)',
            r'achieve (\w+(?:\s+\w+)*)',
            r'become (\w+(?:\s+\w+)*)'
        ]
        
        target_aspiration = "Unspecified aspiration"
        for pattern in aspiration_patterns:
            matches = re.search(pattern, all_aspirations, re.IGNORECASE)
            if matches:
                target_aspiration = matches.group(1).strip()
                break
        
        return {
            'primary_positioning': primary_positioning,
            'target_aspiration': target_aspiration
        }
    
    def _combine_all_content(self, content: BrandContent) -> str:
        """Helper method to combine all content sections into a single text for analysis"""
        
        all_content = []
        all_content.extend(content.hero_sections)
        all_content.extend(content.value_propositions)
        all_content.extend(content.about_content)
        all_content.extend(content.product_descriptions)
        all_content.extend(content.testimonials)
        
        return ' '.join(all_content)

# File: examples/test_analyzer.py

import asyncio
from core.base_agents import AgentManager
from agents import register_scraping_agents
from agents.brand_analyzer import BrandAnalysisAgent
from config.agent_config import AGENT_CONFIGS

async def test_complete_analysis_pipeline():
    """
    Test the complete scraping + analysis pipeline.
    This shows you how the two agents work together.
    """
    
    # Set up the agent manager
    agent_manager = AgentManager()
    register_scraping_agents(agent_manager)
    
    # Register the brand analyzer
    agent_manager.register_agent_type('brand_analyzer', BrandAnalysisAgent, AGENT_CONFIGS['brand_analyzer'])
    
    # First, scrape brand content
    scraper = agent_manager.create_agent('brand_scraper')
    scrape_result = await scraper.execute({'url': 'https://www.apple.com'})
    
    if not scrape_result.success:
        print(f"❌ Scraping failed: {scrape_result.error_message}")
        return
    
    print(f"✅ Scraping completed in {scrape_result.execution_time:.2f}s")
    
    # Now analyze the scraped content
    analyzer = agent_manager.create_agent('brand_analyzer')
    analysis_result = await analyzer.execute({'scraped_content': scrape_result.result})
    
    if analysis_result.success:
        profile = analysis_result.result
        print(f"✅ Analysis completed in {analysis_result.execution_time:.2f}s")
        print(f"\n📊 Brand Analysis Results:")
        print(f"Primary Positioning: {profile.primary_positioning}")
        print(f"Target Aspiration: {profile.target_audience_aspiration}")
        print(f"Authenticity Score: {profile.authenticity_score:.2f}")
        print(f"Satirical Vulnerabilities: {len(profile.satirical_vulnerabilities)}")
        
        if profile.satirical_vulnerabilities:
            print(f"\n🎯 Top Satirical Targets:")
            for vulnerability in profile.satirical_vulnerabilities[:3]:
                print(f"  • {vulnerability}")
                
    else:
        print(f"❌ Analysis failed: {analysis_result.error_message}")

if __name__ == "__main__":
    asyncio.run(test_complete_analysis_pipeline())