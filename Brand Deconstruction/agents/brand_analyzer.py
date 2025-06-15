# File: agents/brand_analyzer.py

import re
import time
import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from core.base_agents import AgentBase, AgentResponse

logger = logging.getLogger(__name__)

@dataclass
class BrandAnalysisResult:
    """Structure for brand analysis results"""
    brand_name: str
    authenticity_score: float  # 0.0 to 1.0, lower = more contradictory
    satirical_vulnerabilities: List[Dict[str, Any]]
    contradiction_themes: List[str]
    primary_positioning: str
    brand_keywords: List[str]
    analysis_metadata: Dict[str, Any]

class BrandAnalysisAgent(AgentBase):
    """
    AI-powered brand analysis agent that identifies satirical vulnerabilities.
    
    This agent examines corporate content to find gaps between stated values
    and implied realities, measuring authenticity and identifying specific
    contradictions that can be exploited for satirical effect.
    """
    
    def __init__(self, agent_config: Dict[str, Any] = None):
        super().__init__(agent_config)
        
        # Analysis configuration
        self.analysis_depth = self.config.get('analysis_depth', 'comprehensive')
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        
        # Corporate buzzword patterns
        self.buzzword_patterns = {
            'innovation_washing': [
                'innovative', 'disruptive', 'cutting-edge', 'next-generation',
                'revolutionary', 'groundbreaking', 'transformative'
            ],
            'customer_centricity_claims': [
                'customer-first', 'customer-centric', 'customer-focused',
                'putting customers first', 'customer obsessed'
            ],
            'sustainability_washing': [
                'sustainable', 'green', 'eco-friendly', 'carbon-neutral',
                'environmentally responsible', 'sustainability'
            ],
            'people_first_claims': [
                'people-first', 'employee-centric', 'great place to work',
                'diverse and inclusive', 'work-life balance'
            ],
            'simplicity_claims': [
                'simple', 'easy', 'streamlined', 'user-friendly',
                'intuitive', 'hassle-free', 'effortless'
            ]
        }
        
        # Contradiction indicators
        self.contradiction_indicators = {
            'complexity_vs_simplicity': [
                'comprehensive suite', 'full-stack solution', 'end-to-end platform'
            ],
            'scale_vs_personal': [
                'enterprise-grade', 'scalable', 'global reach', 'millions of users'
            ],
            'automation_vs_human': [
                'AI-powered', 'automated', 'machine learning', 'algorithmic'
            ]
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Analyze brand content for satirical vulnerabilities and contradictions.
        """
        
        start_time = time.time()
        
        if not self.validate_input(input_data):
            return AgentResponse(
                success=False,
                error_message="Invalid input: scraped_content is required",
                execution_time=time.time() - start_time
            )
        
        scraped_content = input_data['scraped_content']
        satirical_intensity = input_data.get('satirical_intensity', 'medium')
        url = input_data.get('url', '')
        
        try:
            logger.info(f"Starting brand analysis for: {scraped_content.metadata.get('company_name', 'Unknown')}")
            
            # Extract brand name
            brand_name = self._extract_brand_name(scraped_content)
            
            # Analyze content for contradictions
            vulnerabilities = await self._identify_satirical_vulnerabilities(scraped_content, satirical_intensity)
            
            # Calculate authenticity score
            authenticity_score = self._calculate_authenticity_score(scraped_content, vulnerabilities)
            
            # Extract primary positioning
            primary_positioning = self._extract_primary_positioning(scraped_content)
            
            # Extract brand keywords
            brand_keywords = self._extract_brand_keywords(scraped_content)
            
            # Identify contradiction themes
            contradiction_themes = self._identify_contradiction_themes(vulnerabilities)
            
            # Create analysis result
            analysis_result = BrandAnalysisResult(
                brand_name=brand_name,
                authenticity_score=authenticity_score,
                satirical_vulnerabilities=vulnerabilities,
                contradiction_themes=contradiction_themes,
                primary_positioning=primary_positioning,
                brand_keywords=brand_keywords,
                analysis_metadata={
                    'url': url,
                    'content_length': len(scraped_content.main_content),
                    'satirical_intensity': satirical_intensity,
                    'vulnerabilities_found': len(vulnerabilities),
                    'analysis_depth': self.analysis_depth
                }
            )
            
            execution_time = time.time() - start_time
            logger.info(f"Brand analysis completed in {execution_time:.2f}s")
            logger.info(f"Authenticity score: {authenticity_score:.2f}, Vulnerabilities: {len(vulnerabilities)}")
            
            return AgentResponse(
                success=True,
                data=analysis_result,
                execution_time=execution_time,
                metadata={
                    'brand_name': brand_name,
                    'authenticity_score': authenticity_score,
                    'vulnerabilities_count': len(vulnerabilities)
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Brand analysis failed: {str(e)}")
            
            return AgentResponse(
                success=False,
                error_message=f"Analysis error: {str(e)}",
                execution_time=execution_time
            )
    
    def _extract_brand_name(self, content) -> str:
        """Extract the brand/company name from content"""
        
        # Try multiple sources for brand name
        potential_names = [
            content.metadata.get('company_name'),
            content.title.split(' - ')[0] if ' - ' in content.title else content.title,
            content.metadata.get('og_title')
        ]
        
        for name in potential_names:
            if name and len(name.strip()) > 0:
                return name.strip()
        
        return "Unknown Brand"
    
    async def _identify_satirical_vulnerabilities(self, content, intensity: str) -> List[Dict[str, Any]]:
        """Identify specific vulnerabilities that can be satirically exploited"""
        
        vulnerabilities = []
        content_lower = content.main_content.lower()
        
        # Check each buzzword category for contradictions
        for category, buzzwords in self.buzzword_patterns.items():
            buzzword_count = sum(content_lower.count(word.lower()) for word in buzzwords)
            
            if buzzword_count > 0:
                # Look for contradictory indicators
                contradictions = self._find_contradictions_for_category(content_lower, category)
                
                if contradictions:
                    vulnerability = {
                        'category': category,
                        'buzzword_frequency': buzzword_count,
                        'contradiction_evidence': contradictions,
                        'satirical_angle': self._generate_satirical_angle(category, contradictions),
                        'intensity_rating': self._rate_vulnerability_intensity(buzzword_count, len(contradictions)),
                        'recommended_approach': self._recommend_satirical_approach(category, intensity)
                    }
                    vulnerabilities.append(vulnerability)
        
        # Check for general corporate speak density
        corporate_speak_density = self._calculate_corporate_speak_density(content_lower)
        if corporate_speak_density > 0.05:  # More than 5% corporate buzzwords
            vulnerabilities.append({
                'category': 'corporate_speak_overload',
                'buzzword_frequency': int(corporate_speak_density * 100),
                'contradiction_evidence': ['Excessive use of meaningless corporate jargon'],
                'satirical_angle': 'The complete inability to speak like normal humans',
                'intensity_rating': min(corporate_speak_density * 10, 1.0),
                'recommended_approach': 'Translate corporate speak into plain English to reveal absurdity'
            })
        
        return vulnerabilities
    
    def _find_contradictions_for_category(self, content: str, category: str) -> List[str]:
        """Find specific contradictions for a buzzword category"""
        
        contradictions = []
        
        if category == 'innovation_washing':
            # Look for evidence of following rather than leading
            followers_indicators = ['industry standard', 'best practices', 'proven methods', 'established']
            for indicator in followers_indicators:
                if indicator in content:
                    contradictions.append(f"Claims innovation while promoting '{indicator}'")
        
        elif category == 'customer_centricity_claims':
            # Look for evidence of complexity or barriers
            barriers = ['enterprise sales', 'contact sales', 'custom pricing', 'implementation']
            for barrier in barriers:
                if barrier in content:
                    contradictions.append(f"Claims customer focus while requiring '{barrier}'")
        
        elif category == 'simplicity_claims':
            # Look for evidence of complexity
            complexity_indicators = ['integration', 'configuration', 'customization', 'setup']
            for indicator in complexity_indicators:
                if indicator in content:
                    contradictions.append(f"Claims simplicity while requiring '{indicator}'")
        
        elif category == 'people_first_claims':
            # Look for automation/efficiency focus
            automation_focus = ['automate', 'efficiency', 'productivity', 'optimization']
            for focus in automation_focus:
                if focus in content:
                    contradictions.append(f"Claims people-first while emphasizing '{focus}'")
        
        return contradictions
    
    def _generate_satirical_angle(self, category: str, contradictions: List[str]) -> str:
        """Generate a satirical angle based on the contradiction category"""
        
        angles = {
            'innovation_washing': "Revolutionary new way of doing exactly what everyone else does",
            'customer_centricity_claims': "Customer-first company that makes customers jump through hoops",
            'sustainability_washing': "Green company that's actually just good at green marketing",
            'people_first_claims': "People-first company that treats people like efficiency metrics",
            'simplicity_claims': "Simple solution that requires a PhD to understand",
            'corporate_speak_overload': "Company that forgot how to speak human"
        }
        
        return angles.get(category, "Generic corporate contradiction")
    
    def _rate_vulnerability_intensity(self, buzzword_count: int, contradiction_count: int) -> float:
        """Rate the intensity of a vulnerability from 0.0 to 1.0"""
        
        # Higher buzzword count + more contradictions = higher intensity
        intensity = min((buzzword_count * 0.1) + (contradiction_count * 0.2), 1.0)
        return round(intensity, 2)
    
    def _recommend_satirical_approach(self, category: str, intensity: str) -> str:
        """Recommend how to approach this vulnerability satirically"""
        
        approaches = {
            'low': {
                'innovation_washing': "Gentle mockery of buzzword usage",
                'customer_centricity_claims': "Highlight small customer friction points",
                'simplicity_claims': "Point out minor complexity contradictions"
            },
            'medium': {
                'innovation_washing': "Expose gap between claims and reality",
                'customer_centricity_claims': "Show customer journey obstacles",
                'simplicity_claims': "Demonstrate actual complexity involved"
            },
            'high': {
                'innovation_washing': "Full deconstruction of innovation theater",
                'customer_centricity_claims': "Expose customer-hostile business model",
                'simplicity_claims': "Reveal the complexity industrial complex"
            }
        }
        
        return approaches.get(intensity, {}).get(category, "Standard satirical approach")
    
    def _calculate_authenticity_score(self, content, vulnerabilities: List[Dict]) -> float:
        """Calculate overall authenticity score (0.0 = very inauthentic, 1.0 = authentic)"""
        
        # Start with base score
        base_score = 1.0
        
        # Subtract for each vulnerability
        for vulnerability in vulnerabilities:
            intensity = vulnerability.get('intensity_rating', 0.5)
            base_score -= (intensity * 0.1)  # Each vulnerability reduces score
        
        # Factor in corporate speak density
        corporate_density = self._calculate_corporate_speak_density(content.main_content.lower())
        base_score -= (corporate_density * 0.5)
        
        # Factor in buzzword density
        buzzword_density = content.metadata.get('buzzword_density', 0) / 100
        base_score -= (buzzword_density * 0.1)
        
        # Ensure score stays within bounds
        authenticity_score = max(0.0, min(1.0, base_score))
        
        return round(authenticity_score, 2)
    
    def _extract_primary_positioning(self, content) -> str:
        """Extract the primary way the brand positions itself"""
        
        # Look for common positioning patterns
        content_text = content.main_content.lower()
        
        positioning_patterns = {
            'innovation_leader': ['innovation', 'innovative', 'cutting-edge', 'revolutionary'],
            'customer_focused': ['customer', 'client', 'customer-first', 'customer-centric'],
            'simple_solution': ['simple', 'easy', 'streamlined', 'user-friendly'],
            'enterprise_focused': ['enterprise', 'business', 'corporate', 'professional'],
            'technology_focused': ['technology', 'tech', 'digital', 'AI', 'machine learning']
        }
        
        scores = {}
        for positioning, keywords in positioning_patterns.items():
            score = sum(content_text.count(keyword) for keyword in keywords)
            scores[positioning] = score
        
        # Return the highest-scoring positioning
        if scores:
            primary_positioning = max(scores, key=scores.get)
            return primary_positioning.replace('_', ' ').title()
        
        return "General Business"
    
    def _extract_brand_keywords(self, content) -> List[str]:
        """Extract key brand-related keywords from content"""
        
        # Get most frequent meaningful words
        text = content.main_content.lower()
        
        # Remove common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall', 'should', 'would', 'could', 'can', 'may', 'might', 'must', 'shall'}
        
        # Extract words
        words = re.findall(r'\b[a-z]+\b', text)
        word_freq = {}
        
        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top 10 most frequent words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
    
    def _identify_contradiction_themes(self, vulnerabilities: List[Dict]) -> List[str]:
        """Identify main themes of contradictions"""
        
        themes = []
        categories = [v['category'] for v in vulnerabilities]
        
        if any('innovation' in cat for cat in categories):
            themes.append('Innovation Theater')
        
        if any('customer' in cat for cat in categories):
            themes.append('Customer Experience Gap')
        
        if any('simplicity' in cat for cat in categories):
            themes.append('Complexity Masquerading as Simplicity')
        
        if any('people' in cat for cat in categories):
            themes.append('Human vs Efficiency Contradiction')
        
        if any('speak' in cat for cat in categories):
            themes.append('Communication Authenticity Issues')
        
        return themes if themes else ['General Corporate Contradiction']
    
    def _calculate_corporate_speak_density(self, content: str) -> float:
        """Calculate the density of corporate buzzwords in content"""
        
        all_buzzwords = []
        for category_words in self.buzzword_patterns.values():
            all_buzzwords.extend(category_words)
        
        # Add more corporate speak terms
        all_buzzwords.extend([
            'synergy', 'leverage', 'paradigm', 'holistic', 'robust', 'scalable',
            'optimization', 'monetize', 'utilize', 'facilitate', 'implement',
            'solution', 'platform', 'ecosystem', 'framework', 'methodology'
        ])
        
        word_count = len(content.split())
        if word_count == 0:
            return 0.0
        
        buzzword_count = sum(content.count(buzzword.lower()) for buzzword in all_buzzwords)
        return buzzword_count / word_count
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate that we have scraped content to analyze"""
        return (input_data is not None and 
                'scraped_content' in input_data and 
                input_data['scraped_content'] is not None)
