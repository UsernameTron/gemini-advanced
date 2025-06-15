# Phase 2: Intelligent Web Scraping Agent
# File: agents/brand_scraper.py

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import Dict, List, Set
from dataclasses import dataclass
import time
from core.base_agents import AgentBase, AgentResponse

@dataclass
class BrandContent:
    """Structure for organizing extracted brand content by semantic meaning"""
    hero_sections: List[str]
    value_propositions: List[str]
    about_content: List[str]
    product_descriptions: List[str]
    testimonials: List[str]
    navigation_copy: List[str]
    metadata: Dict[str, str]

class BrandScrapingAgent(AgentBase):
    """
    Specialized agent for extracting brand-relevant content from corporate websites.
    
    This agent understands the semantic structure of marketing websites and focuses
    on areas where companies reveal their aspirational language and positioning.
    """
    
    def __init__(self, agent_id: str, agent_type: str, config: Dict):
        super().__init__(agent_id, agent_type, config)
        
        # CSS selectors for different types of brand content
        # These target the sections where companies typically put their most
        # polished and revealing marketing language
        self.content_selectors = {
            'hero_sections': [
                'h1', '.hero h1', '.hero h2', '.banner h1', '.jumbotron h1',
                '.hero-title', '.main-headline', '[class*="hero"] h1'
            ],
            'value_propositions': [
                '.features li', '.benefits li', '.why-us li', '.advantages li',
                '[class*="feature"] h3', '[class*="benefit"] h3', '.value-prop'
            ],
            'about_content': [
                '#about p', '.about-us p', '.our-story p', '.mission p',
                '.company-info p', '[class*="about"] p'
            ],
            'product_descriptions': [
                '.product-description p', '.service-overview p', 
                '.product-features li', '.service-benefits li'
            ],
            'testimonials': [
                '.testimonial', '.review', '.customer-story', '.quote',
                '[class*="testimonial"]', '[class*="review"]'
            ],
            'navigation_copy': [
                'nav a', '.menu a', '.navigation a', 'header a'
            ]
        }
        
        # Patterns for identifying low-value content to filter out
        self.noise_patterns = [
            r'cookie', r'privacy policy', r'terms of service', r'copyright',
            r'all rights reserved', r'sign up', r'login', r'cart', r'checkout'
        ]
        
    async def execute(self, input_data: Dict) -> AgentResponse:
        """Main execution method that orchestrates the scraping process"""
        
        start_time = time.time()
        url = input_data.get('url')
        
        if not url:
            return AgentResponse(
                success=False,
                result=None,
                agent_type=self.agent_type,
                error_message="No URL provided for scraping"
            )
        
        try:
            self.log_execution("Starting brand content extraction", f"URL: {url}")
            
            # Step 1: Fetch the webpage content
            html_content = await self._fetch_page_content(url)
            
            # Step 2: Parse and extract brand-relevant sections
            brand_content = await self._extract_brand_content(html_content, url)
            
            # Step 3: Clean and structure the extracted content
            cleaned_content = self._clean_and_structure_content(brand_content)
            
            execution_time = time.time() - start_time
            
            self.log_execution("Brand content extraction completed", 
                             f"Extracted {len(cleaned_content.hero_sections)} hero sections, "
                             f"{len(cleaned_content.value_propositions)} value props")
            
            return AgentResponse(
                success=True,
                result=cleaned_content,
                agent_type=self.agent_type,
                execution_time=execution_time,
                metadata={'source_url': url, 'content_sections': len(cleaned_content.__dict__)}
            )
            
        except Exception as e:
            self.log_execution("Scraping failed", str(e))
            return AgentResponse(
                success=False,
                result=None,
                agent_type=self.agent_type,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    async def _fetch_page_content(self, url: str) -> str:
        """
        Fetch webpage content with proper error handling and timeout.
        Uses aiohttp for async operations to avoid blocking.
        """
        
        timeout = aiohttp.ClientTimeout(total=self.config.get('timeout_seconds', 30))
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, 
                                 headers={'User-Agent': 'BrandAnalyzer/1.0'}) as response:
                
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: Failed to fetch {url}")
                
                content = await response.text()
                self.log_execution("Page fetched successfully", f"Content length: {len(content)}")
                return content
    
    async def _extract_brand_content(self, html_content: str, base_url: str) -> BrandContent:
        """
        Extract content using our semantic understanding of brand messaging areas.
        
        This method focuses on the sections where companies typically put their
        most revealing marketing language and positioning statements.
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements that clutter our analysis
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        
        extracted_content = {}
        
        # Extract content for each semantic category
        for section_name, selectors in self.content_selectors.items():
            section_content = []
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    
                    # Filter out noise and keep meaningful content
                    if self._is_meaningful_content(text):
                        section_content.append(text)
            
            extracted_content[section_name] = section_content
        
        # Extract metadata that might be useful for analysis
        metadata = {
            'page_title': soup.title.string if soup.title else '',
            'meta_description': '',
            'company_name': self._extract_company_name(soup)
        }
        
        # Look for meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['meta_description'] = meta_desc.get('content', '')
        
        return BrandContent(
            hero_sections=extracted_content['hero_sections'],
            value_propositions=extracted_content['value_propositions'],
            about_content=extracted_content['about_content'],
            product_descriptions=extracted_content['product_descriptions'],
            testimonials=extracted_content['testimonials'],
            navigation_copy=extracted_content['navigation_copy'],
            metadata=metadata
        )
    
    def _is_meaningful_content(self, text: str) -> bool:
        """
        Determine if a piece of text contains meaningful brand content.
        
        This filters out navigation elements, legal text, and other noise
        that doesn't reveal brand positioning or voice.
        """
        
        # Skip very short or very long texts
        if len(text) < 10 or len(text) > 500:
            return False
        
        # Skip content that matches noise patterns
        text_lower = text.lower()
        for pattern in self.noise_patterns:
            if re.search(pattern, text_lower):
                return False
        
        # Skip content that's mostly numbers or special characters
        if len(re.sub(r'[^a-zA-Z\s]', '', text)) < len(text) * 0.6:
            return False
        
        return True
    
    def _extract_company_name(self, soup: BeautifulSoup) -> str:
        """
        Try to identify the company name from various page elements.
        This helps us understand whose brand voice we're analyzing.
        """
        
        # Try multiple strategies to find company name
        strategies = [
            lambda: soup.find('meta', attrs={'property': 'og:site_name'}),
            lambda: soup.find('link', attrs={'rel': 'canonical'}),
            lambda: soup.find('h1'),
            lambda: soup.title
        ]
        
        for strategy in strategies:
            try:
                element = strategy()
                if element:
                    text = element.get('content') or element.get('href') or element.get_text()
                    if text and len(text) < 100:
                        return text.strip()
            except:
                continue
        
        return "Unknown Company"
    
    def _clean_and_structure_content(self, brand_content: BrandContent) -> BrandContent:
        """
        Final cleaning pass to remove duplicates and organize content logically.
        
        This ensures we have clean, unique content ready for analysis.
        """
        
        def deduplicate_list(items: List[str]) -> List[str]:
            """Remove duplicates while preserving order"""
            seen = set()
            result = []
            for item in items:
                if item not in seen:
                    seen.add(item)
                    result.append(item)
            return result
        
        # Clean each content section
        return BrandContent(
            hero_sections=deduplicate_list(brand_content.hero_sections),
            value_propositions=deduplicate_list(brand_content.value_propositions),
            about_content=deduplicate_list(brand_content.about_content),
            product_descriptions=deduplicate_list(brand_content.product_descriptions),
            testimonials=deduplicate_list(brand_content.testimonials),
            navigation_copy=deduplicate_list(brand_content.navigation_copy),
            metadata=brand_content.metadata
        )

# File: agents/__init__.py

from .brand_scraper import BrandScrapingAgent

# Function to register all agents with the manager
def register_scraping_agents(agent_manager):
    """Register scraping-related agents with the agent manager"""
    from config.agent_config import AGENT_CONFIGS
    
    agent_manager.register_agent_type(
        'brand_scraper', 
        BrandScrapingAgent, 
        AGENT_CONFIGS['brand_scraper']
    )

# File: examples/test_scraper.py

import asyncio
from core.base_agents import AgentManager
from agents import register_scraping_agents

async def test_brand_scraper():
    """
    Test the brand scraping agent with a real website.
    This shows you how to use the scraper independently.
    """
    
    # Set up the agent manager and register our scraper
    agent_manager = AgentManager()
    register_scraping_agents(agent_manager)
    
    # Create a brand scraper instance
    scraper = agent_manager.create_agent('brand_scraper')
    
    # Test with a well-known company website
    test_url = "https://www.apple.com"  # Replace with any company website
    
    print(f"Testing brand scraper with: {test_url}")
    
    result = await scraper.execute({'url': test_url})
    
    if result.success:
        content = result.result
        print(f"\n✅ Scraping successful! Execution time: {result.execution_time:.2f}s")
        print(f"Company: {content.metadata.get('company_name', 'Unknown')}")
        print(f"Hero sections found: {len(content.hero_sections)}")
        print(f"Value propositions found: {len(content.value_propositions)}")
        
        # Show some example content
        if content.hero_sections:
            print(f"\nExample hero content: {content.hero_sections[0]}")
        
        if content.value_propositions:
            print(f"Example value prop: {content.value_propositions[0]}")
            
    else:
        print(f"❌ Scraping failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(test_brand_scraper())