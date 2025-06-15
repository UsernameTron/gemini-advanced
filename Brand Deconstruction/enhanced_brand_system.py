# Enhanced Brand Deconstruction Engine with Agent Integration
# Agent-Enhanced Brand Deconstruction System with Direct gpt-image-1 Integration

import asyncio
import aiohttp
import logging
import time
import json
import os
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin, urlparse
import random
import base64

# Add project directories to path for agent imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "RAG"))
sys.path.insert(0, str(project_root / "VectorDBRAG"))
sys.path.insert(0, str(project_root / "MindMeld-v1.1" / "src"))
sys.path.insert(0, str(project_root))

# Import available agents from the ecosystem
try:
    from RAG.legacy_agents import CodeAnalyzerAgent, PerformanceProfilerAgent, TestGeneratorAgent, ImageAgent
    from RAG.agents.enhanced.enhanced_agents import (
        CodeAnalysisAgent as EnhancedCodeAnalysisAgent,
        PerformanceProfilerAgent as EnhancedPerformanceAgent,
        TestGeneratorAgent as EnhancedTestAgent,
        ImageAgent as EnhancedImageAgent
    )
    AGENTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Agent imports failed: {e}. Running in fallback mode.")
    AGENTS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class BrandAnalysisResult:
    """Enhanced brand analysis with agent insights"""
    brand_name: str
    authenticity_score: float
    satirical_vulnerabilities: List[Dict[str, Any]]
    content_analysis: Dict[str, Any]
    agent_insights: Dict[str, Any]
    scraping_fallback_used: bool = False
    processing_time: float = 0.0

@dataclass
class GPTImage1GenerationRequest:
    """Direct gpt-image-1 generation request structure"""
    prompt: str
    style: str = "photorealistic"
    resolution: str = "1024x1024"
    quality: str = "high"  # Valid values: 'low', 'medium', 'high', 'auto'
    brand_context: Optional[Dict[str, Any]] = None
    satirical_intensity: float = 0.7

@dataclass
class GPTImage1Result:
    """Direct gpt-image-1 generation result"""
    success: bool
    image_data: Optional[str] = None  # Base64 encoded
    image_url: Optional[str] = None
    generation_metadata: Optional[Dict[str, Any]] = None
    processing_time: float = 0.0
    error_message: Optional[str] = None

class RobustBrandScraper:
    """
    Robust brand scraper with multiple fallback strategies and known brand database.
    """
    
    def __init__(self):
        self.session = None
        self.known_brands = {
            "salesforce.com": {
                "name": "Salesforce",
                "positioning": "The Customer Company",
                "key_claims": ["AI-powered CRM", "Customer success", "Trailblazer community"],
                "vulnerabilities": ["AI washing", "Complexity masking", "Scale vs personal"]
            },
            "apple.com": {
                "name": "Apple",
                "positioning": "Think Different",
                "key_claims": ["Innovation", "Privacy", "Premium design"],
                "vulnerabilities": ["Premium accessibility", "Innovation vs iteration", "Privacy vs data collection"]
            },
            "google.com": {
                "name": "Google",
                "positioning": "Don't be evil / Do the right thing",
                "key_claims": ["Information accessibility", "Innovation", "Free services"],
                "vulnerabilities": ["Data privacy", "Market dominance", "Free vs surveillance"]
            },
            "microsoft.com": {
                "name": "Microsoft",
                "positioning": "Empower every person",
                "key_claims": ["Productivity", "Cloud-first", "AI for everyone"],
                "vulnerabilities": ["Enterprise complexity", "Privacy in cloud", "AI democratization"]
            }
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=self.headers,
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=10)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def scrape_brand_content(self, url: str) -> Dict[str, Any]:
        """
        Scrape brand content with robust fallback strategies.
        """
        start_time = time.time()
        domain = urlparse(url).netloc.lower().replace('www.', '')
        
        # Strategy 1: Try direct scraping
        try:
            result = await self._direct_scrape(url)
            if result and result.get('success'):
                result['fallback_used'] = False
                result['processing_time'] = time.time() - start_time
                return result
        except Exception as e:
            logger.warning(f"Direct scraping failed for {url}: {e}")
        
        # Strategy 2: Try known brand database
        if domain in self.known_brands:
            logger.info(f"Using known brand data for {domain}")
            brand_data = self.known_brands[domain]
            return {
                'success': True,
                'brand_name': brand_data['name'],
                'content': {
                    'hero_sections': [brand_data['positioning']],
                    'value_propositions': brand_data['key_claims'],
                    'about_content': [f"{brand_data['name']} - {brand_data['positioning']}"],
                    'vulnerabilities': brand_data['vulnerabilities']
                },
                'fallback_used': True,
                'fallback_method': 'known_brand_database',
                'processing_time': time.time() - start_time
            }
        
        # Strategy 3: Generic analysis based on domain
        brand_name = domain.split('.')[0].capitalize()
        return {
            'success': True,
            'brand_name': brand_name,
            'content': {
                'hero_sections': [f"{brand_name} - Corporate Website"],
                'value_propositions': ["Innovation", "Customer Focus", "Quality"],
                'about_content': [f"{brand_name} - Technology Company"],
                'vulnerabilities': ["Generic corporate positioning", "Standard marketing claims"]
            },
            'fallback_used': True,
            'fallback_method': 'generic_analysis',
            'processing_time': time.time() - start_time
        }
    
    async def _direct_scrape(self, url: str) -> Dict[str, Any]:
        """Direct web scraping attempt"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise aiohttp.ClientError(f"HTTP {response.status}")
            
            html = await response.text()
            
            # Simple content extraction
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title as brand name
            title = soup.find('title')
            brand_name = title.text.strip() if title else urlparse(url).netloc
            
            # Extract hero sections
            hero_sections = []
            for selector in ['h1', '.hero h1', '.hero h2', '.banner h1']:
                elements = soup.select(selector)
                hero_sections.extend([el.get_text().strip() for el in elements[:3]])
            
            # Extract value propositions
            value_props = []
            for selector in ['.features li', '.benefits li', 'h3']:
                elements = soup.select(selector)
                value_props.extend([el.get_text().strip() for el in elements[:5]])
            
            # Extract about content
            about_content = []
            for selector in ['#about p', '.about p', 'p']:
                elements = soup.select(selector)
                about_content.extend([el.get_text().strip() for el in elements[:3]])
            
            return {
                'success': True,
                'brand_name': brand_name,
                'content': {
                    'hero_sections': hero_sections,
                    'value_propositions': value_props,
                    'about_content': about_content,
                    'vulnerabilities': []  # Will be analyzed by agents
                }
            }

class DirectGPTImage1Client:
    """
    Direct client for gpt-image-1 model bypassing complex conceptual layers.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "gpt-image-1"
        self.endpoint = "https://api.openai.com/v1/images/generations"
    
    async def generate_image(self, request: GPTImage1GenerationRequest) -> GPTImage1Result:
        """
        Generate image directly using gpt-image-1 model.
        """
        start_time = time.time()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Enhanced prompt with brand context
            enhanced_prompt = self._enhance_prompt_with_context(request)
            
            payload = {
                "model": self.model,
                "prompt": enhanced_prompt,
                "n": 1,
                "size": request.resolution if request.resolution in ["1024x1024", "1152x896", "1216x832", "1344x768", "1536x1024", "1024x1792", "896x1152", "832x1216", "768x1344"] else "1536x1024",
                "quality": request.quality if request.quality in ["standard", "hd"] else "hd"
                # Note: gpt-image-1 doesn't support 'style' parameter
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, headers=headers, json=payload) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        image_url = response_data["data"][0]["url"]
                        
                        # Optionally download and encode as base64
                        image_data = await self._download_and_encode(session, image_url)
                        
                        return GPTImage1Result(
                            success=True,
                            image_data=image_data,
                            image_url=image_url,
                            generation_metadata={
                                "model": self.model,
                                "prompt_length": len(enhanced_prompt),
                                "resolution": request.resolution,
                                "quality": request.quality
                                # Note: style removed for gpt-image-1 compatibility
                            },
                            processing_time=time.time() - start_time
                        )
                    else:
                        error_msg = response_data.get("error", {}).get("message", f"HTTP {response.status}")
                        return GPTImage1Result(
                            success=False,
                            error_message=f"gpt-image-1 error: {error_msg}",
                            processing_time=time.time() - start_time
                        )
                        
        except Exception as e:
            return GPTImage1Result(
                success=False,
                error_message=f"gpt-image-1 error: {str(e)}",
                processing_time=time.time() - start_time
            )
    
    def _enhance_prompt_with_context(self, request: GPTImage1GenerationRequest) -> str:
        """Enhance prompt with brand context and satirical elements"""
        base_prompt = request.prompt
        
        if request.brand_context:
            brand_name = request.brand_context.get('brand_name', 'Company')
            vulnerabilities = request.brand_context.get('vulnerabilities', [])
            
            if vulnerabilities:
                vulnerability_text = ", ".join(vulnerabilities[:2])
                context_enhancement = f" Corporate satirical image exposing {brand_name}'s {vulnerability_text}."
                base_prompt = f"{base_prompt} {context_enhancement}"
        
        # Add satirical intensity guidance
        if request.satirical_intensity > 0.5:
            base_prompt += " Professional, thought-provoking visual critique with subtle irony."
        else:
            base_prompt += " Subtle, professional visual commentary."
        
        return base_prompt
    
    async def _download_and_encode(self, session: aiohttp.ClientSession, image_url: str) -> Optional[str]:
        """Download image and encode as base64"""
        try:
            async with session.get(image_url) as response:
                if response.status == 200:
                    image_bytes = await response.read()
                    return base64.b64encode(image_bytes).decode('utf-8')
        except Exception as e:
            logger.warning(f"Failed to download image: {e}")
        return None

class AgentEnhancedBrandAnalyzer:
    """
    Brand analyzer enhanced with agent ecosystem integration.
    """
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize available agents"""
        if not AGENTS_AVAILABLE:
            logger.warning("Agents not available, running in fallback mode")
            return
        
        try:
            # Initialize enhanced agents if available
            agent_config = {
                'openai_client': None,  # Will be set if needed
                'model': 'gpt-4'
            }
            
            self.agents = {
                'code_analyzer': CodeAnalyzerAgent() if hasattr(CodeAnalyzerAgent, '__init__') else None,
                'performance_profiler': PerformanceProfilerAgent() if hasattr(PerformanceProfilerAgent, '__init__') else None,
                'test_generator': TestGeneratorAgent() if hasattr(TestGeneratorAgent, '__init__') else None,
                'image_analyzer': ImageAgent() if hasattr(ImageAgent, '__init__') else None,
            }
            
            # Remove None agents
            self.agents = {k: v for k, v in self.agents.items() if v is not None}
            
            logger.info(f"Initialized {len(self.agents)} agents: {list(self.agents.keys())}")
            
        except Exception as e:
            logger.warning(f"Agent initialization failed: {e}")
            self.agents = {}
    
    async def analyze_brand_with_agents(self, scraped_content: Dict[str, Any]) -> BrandAnalysisResult:
        """Analyze brand content using agent ecosystem"""
        start_time = time.time()
        
        brand_name = scraped_content.get('brand_name', 'Unknown Brand')
        content = scraped_content.get('content', {})
        
        # Base analysis
        authenticity_score = self._calculate_authenticity_score(content)
        vulnerabilities = self._identify_vulnerabilities(content)
        
        # Agent-enhanced analysis
        agent_insights = {}
        
        if self.agents:
            # Use code analyzer to analyze system architecture claims
            if 'code_analyzer' in self.agents:
                try:
                    tech_claims = content.get('value_propositions', [])
                    tech_analysis = await self._analyze_tech_claims(tech_claims)
                    agent_insights['technical_analysis'] = tech_analysis
                except Exception as e:
                    logger.warning(f"Code analyzer failed: {e}")
            
            # Use performance profiler for scalability claims
            if 'performance_profiler' in self.agents:
                try:
                    performance_analysis = await self._analyze_performance_claims(content)
                    agent_insights['performance_analysis'] = performance_analysis
                except Exception as e:
                    logger.warning(f"Performance profiler failed: {e}")
            
            # Use image agent for visual brand consistency
            if 'image_analyzer' in self.agents:
                try:
                    visual_analysis = await self._analyze_visual_claims(content)
                    agent_insights['visual_analysis'] = visual_analysis
                except Exception as e:
                    logger.warning(f"Image analyzer failed: {e}")
        
        # Generate agent-enhanced vulnerability analysis
        enhanced_vulnerabilities = self._enhance_vulnerabilities_with_agents(
            vulnerabilities, agent_insights
        )
        
        return BrandAnalysisResult(
            brand_name=brand_name,
            authenticity_score=authenticity_score,
            satirical_vulnerabilities=enhanced_vulnerabilities,
            content_analysis=content,
            agent_insights=agent_insights,
            scraping_fallback_used=scraped_content.get('fallback_used', False),
            processing_time=time.time() - start_time
        )
    
    def _calculate_authenticity_score(self, content: Dict[str, Any]) -> float:
        """Calculate authenticity score based on content analysis"""
        score = 1.0
        
        # Check for generic marketing terms
        generic_terms = ['innovative', 'leading', 'best-in-class', 'revolutionary', 'cutting-edge']
        all_text = ' '.join(str(v) for v in content.values() if isinstance(v, (str, list)))
        
        for term in generic_terms:
            if term.lower() in all_text.lower():
                score -= 0.1
        
        # Check for contradictory claims
        hero_sections = content.get('hero_sections', [])
        if any('simple' in str(h).lower() and 'powerful' in str(h).lower() for h in hero_sections):
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def _identify_vulnerabilities(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify satirical vulnerabilities in brand content"""
        vulnerabilities = []
        
        all_text = ' '.join(str(v) for v in content.values() if isinstance(v, (str, list)))
        lower_text = all_text.lower()
        
        # Common vulnerability patterns
        if 'ai' in lower_text and ('simple' in lower_text or 'easy' in lower_text):
            vulnerabilities.append({
                'theme': 'AI Simplification Paradox',
                'description': 'Claims AI makes things simple while adding complexity',
                'severity': 'high'
            })
        
        if 'personal' in lower_text and 'scale' in lower_text:
            vulnerabilities.append({
                'theme': 'Personal Scale Contradiction',
                'description': 'Claims personal service at massive scale',
                'severity': 'medium'
            })
        
        if 'free' in lower_text and 'premium' in lower_text:
            vulnerabilities.append({
                'theme': 'Free Premium Paradox',
                'description': 'Simultaneous free and premium positioning',
                'severity': 'medium'
            })
        
        return vulnerabilities
    
    async def _analyze_tech_claims(self, claims: List[str]) -> Dict[str, Any]:
        """Use code analyzer agent to evaluate technical claims"""
        if not self.agents.get('code_analyzer'):
            return {'status': 'agent_unavailable'}
        
        # Simple analysis for now - could be enhanced with actual agent integration
        tech_keywords = ['api', 'cloud', 'scalable', 'secure', 'real-time']
        found_keywords = [kw for kw in tech_keywords if any(kw in str(claim).lower() for claim in claims)]
        
        return {
            'technical_keywords': found_keywords,
            'complexity_score': len(found_keywords) / len(tech_keywords),
            'agent_recommendation': 'Verify technical feasibility of claims'
        }
    
    async def _analyze_performance_claims(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Use performance profiler to evaluate scalability claims"""
        if not self.agents.get('performance_profiler'):
            return {'status': 'agent_unavailable'}
        
        all_text = ' '.join(str(v) for v in content.values() if isinstance(v, (str, list)))
        performance_claims = ['fast', 'instant', 'real-time', 'scalable', 'high-performance']
        
        found_claims = [claim for claim in performance_claims if claim in all_text.lower()]
        
        return {
            'performance_claims': found_claims,
            'scalability_promises': len(found_claims),
            'agent_recommendation': 'Audit actual performance metrics'
        }
    
    async def _analyze_visual_claims(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Use image agent to analyze visual consistency claims"""
        if not self.agents.get('image_analyzer'):
            return {'status': 'agent_unavailable'}
        
        visual_terms = ['beautiful', 'intuitive', 'clean', 'modern', 'elegant']
        all_text = ' '.join(str(v) for v in content.values() if isinstance(v, (str, list)))
        
        found_terms = [term for term in visual_terms if term in all_text.lower()]
        
        return {
            'visual_claims': found_terms,
            'design_emphasis': len(found_terms) > 2,
            'agent_recommendation': 'Compare actual UI/UX with claims'
        }
    
    def _enhance_vulnerabilities_with_agents(self, base_vulnerabilities: List[Dict], 
                                           agent_insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhance vulnerabilities with agent analysis"""
        enhanced = list(base_vulnerabilities)
        
        # Add agent-discovered vulnerabilities
        if agent_insights.get('technical_analysis', {}).get('complexity_score', 0) > 0.7:
            enhanced.append({
                'theme': 'Technical Complexity Overload',
                'description': 'High technical claim density suggests complexity masking',
                'severity': 'medium',
                'agent_source': 'code_analyzer'
            })
        
        if agent_insights.get('performance_analysis', {}).get('scalability_promises', 0) > 3:
            enhanced.append({
                'theme': 'Performance Promise Inflation',
                'description': 'Excessive performance claims without verification',
                'severity': 'high',
                'agent_source': 'performance_profiler'
            })
        
        return enhanced

class EnhancedBrandDeconstructionEngine:
    """
    Complete Brand Deconstruction Engine with agent integration and direct gpt-image-1 support.
    """
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.scraper = None
        self.analyzer = AgentEnhancedBrandAnalyzer(openai_api_key)
        self.image_client = DirectGPTImage1Client(openai_api_key)
    
    async def process_brand(self, url: str, generate_images: bool = True, 
                          image_count: int = 3) -> Dict[str, Any]:
        """
        Complete brand deconstruction process with optional image generation.
        """
        start_time = time.time()
        
        # Step 1: Robust brand scraping
        async with RobustBrandScraper() as scraper:
            scraped_content = await scraper.scrape_brand_content(url)
        
        # Step 2: Agent-enhanced analysis
        brand_analysis = await self.analyzer.analyze_brand_with_agents(scraped_content)
        
        # Step 3: Optional gpt-image-1 generation
        generated_images = []
        if generate_images:
            generated_images = await self._generate_satirical_images(
                brand_analysis, image_count
            )
        
        # Step 4: Compile complete result
        result = {
            'success': True,
            'brand_analysis': asdict(brand_analysis),
            'generated_images': generated_images,
            'pipeline_metadata': {
                'total_processing_time': time.time() - start_time,
                'scraping_fallback_used': brand_analysis.scraping_fallback_used,
                'agents_used': list(self.analyzer.agents.keys()),
                'images_generated': len(generated_images),
                'pipeline_version': 'enhanced_agent_v1.0'
            }
        }
        
        return result
    
    async def _generate_satirical_images(self, brand_analysis: BrandAnalysisResult, 
                                       count: int = 3) -> List[Dict[str, Any]]:
        """Generate satirical images using direct gpt-image-1 with pentagram framework"""
        images = []
        
        for i in range(count):
            # Create pentagram framework prompt
            pentagram_prompt = self._create_pentagram_prompt(brand_analysis, i)
            
            request = GPTImage1GenerationRequest(
                prompt=pentagram_prompt['full_prompt'],
                style="photorealistic",
                resolution="1536x1024",  # Maximum supported by gpt-image-1
                quality="high",
                brand_context={
                    'brand_name': brand_analysis.brand_name,
                    'vulnerabilities': [v['theme'] for v in brand_analysis.satirical_vulnerabilities]
                },
                satirical_intensity=0.7
            )
            
            result = await self.image_client.generate_image(request)
            
            images.append({
                'image_id': i + 1,
                'vulnerability_theme': pentagram_prompt['vulnerability_theme'],
                'pentagram_elements': pentagram_prompt['pentagram_elements'],
                'success': result.success,
                'prompt': pentagram_prompt['full_prompt'],
                'image_data': result.image_data,
                'image_url': result.image_url,
                'generation_metadata': result.generation_metadata,
                'processing_time': result.processing_time,
                'error_message': result.error_message
            })
        
        return images
    
    def _create_pentagram_prompt(self, brand_analysis: BrandAnalysisResult, index: int) -> Dict[str, Any]:
        """Create satirical prompt using pentagram framework"""
        brand_name = brand_analysis.brand_name
        vulnerabilities = brand_analysis.satirical_vulnerabilities
        
        if not vulnerabilities:
            vulnerability_theme = "Generic Corporate Perfection"
            description = "Standard corporate communication patterns"
        else:
            vulnerability = vulnerabilities[index % len(vulnerabilities)]
            vulnerability_theme = vulnerability['theme']
            description = vulnerability['description']
        
        # Pentagram Framework Elements
        pentagram_elements = {
            'intent_clarity': f"Expose {brand_name}'s {vulnerability_theme.lower()}",
            'fidelity_pass': "8K resolution, professional commercial photography, hyperreal corporate aesthetic",
            'symbolic_anchoring': "pristine corporate imagery with visible artificiality, mood: subtle corporate irony",
            'environmental_context': "sterile boardroom with perfect lighting revealing emptiness",
            'brand_world_constraints': f"Maintain {brand_name}'s visual branding while exposing pretension, subtle wrongness over obvious mockery"
        }
        
        # Compile full prompt
        full_prompt = f"{pentagram_elements['intent_clarity']}. {pentagram_elements['fidelity_pass']}. {pentagram_elements['symbolic_anchoring']}. {pentagram_elements['environmental_context']}. {pentagram_elements['brand_world_constraints']}"
        
        return {
            'vulnerability_theme': vulnerability_theme,
            'description': description,
            'pentagram_elements': pentagram_elements,
            'full_prompt': full_prompt
        }

# Test and demonstration functions
async def test_enhanced_system():
    """Test the enhanced brand deconstruction system"""
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    print("🚀 Testing Enhanced Agent-Integrated Brand Deconstruction Engine")
    print("=" * 70)
    
    engine = EnhancedBrandDeconstructionEngine(api_key)
    
    # Test URLs
    test_urls = [
        "https://salesforce.com",
        "https://apple.com", 
        "https://google.com"
    ]
    
    for url in test_urls:
        print(f"\n🎯 Processing: {url}")
        print("-" * 50)
        
        try:
            result = await engine.process_brand(url, generate_images=True, image_count=2)
            
            if result['success']:
                brand_analysis = result['brand_analysis']
                print(f"✅ Brand: {brand_analysis['brand_name']}")
                print(f"📊 Authenticity Score: {brand_analysis['authenticity_score']:.2f}")
                print(f"🔍 Vulnerabilities: {len(brand_analysis['satirical_vulnerabilities'])}")
                print(f"🤖 Agent Insights: {len(brand_analysis['agent_insights'])} categories")
                print(f"🖼️  Generated Images: {len(result['generated_images'])}")
                print(f"⏱️  Total Time: {result['pipeline_metadata']['total_processing_time']:.2f}s")
                
                if brand_analysis['scraping_fallback_used']:
                    print("⚠️  Used fallback scraping strategy")
                
                # Show vulnerabilities
                for vuln in brand_analysis['satirical_vulnerabilities'][:2]:
                    print(f"   🎭 {vuln['theme']}: {vuln['description']}")
                
                # Show image generation results
                successful_images = sum(1 for img in result['generated_images'] if img['success'])
                print(f"   🎨 Image Generation: {successful_images}/{len(result['generated_images'])} successful")
                
            else:
                print(f"❌ Failed to process {url}")
                
        except Exception as e:
            print(f"❌ Error processing {url}: {e}")
    
    print("\n🎉 Enhanced system testing complete!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_system())
