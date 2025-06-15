# File: agents/brand_scraper.py

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import time
import logging

from core.base_agents import AgentBase, AgentResponse

logger = logging.getLogger(__name__)

@dataclass
class ScrapedContent:
    """Structure for scraped website content"""
    url: str
    title: str
    main_content: str
    navigation_links: List[str]
    metadata: Dict[str, Any]
    sections: Dict[str, str]
    raw_html: str

class BrandScrapingAgent(AgentBase):
    """
    Intelligent web scraping agent that extracts brand content from corporate websites.
    
    This agent goes beyond simple HTML parsing to understand the structure and 
    meaning of corporate websites, extracting the content that reveals how 
    companies present themselves to the world.
    """
    
    def __init__(self, agent_config: Dict[str, Any] = None):
        super().__init__(agent_config)
        
        # Scraping configuration
        self.timeout = self.config.get('timeout_seconds', 30)
        self.max_retries = self.config.get('max_retries', 3)
        self.respect_robots_txt = self.config.get('respect_robots_txt', True)
        
        # Headers to appear like a normal browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Extract brand content from the specified URL.
        """
        
        start_time = time.time()
        
        if not self.validate_input(input_data):
            return AgentResponse(
                success=False,
                error_message="Invalid input: URL is required",
                execution_time=time.time() - start_time
            )
        
        url = input_data['url']
        depth_level = input_data.get('depth_level', 'comprehensive')
        
        try:
            logger.info(f"Starting brand content scraping for: {url}")
            
            # Scrape the main page
            scraped_content = await self._scrape_url(url)
            
            if not scraped_content:
                return AgentResponse(
                    success=False,
                    error_message="Failed to scrape content from URL",
                    execution_time=time.time() - start_time
                )
            
            # Enhance content based on depth level
            if depth_level in ['comprehensive', 'deep_dive']:
                scraped_content = await self._enhance_content_analysis(scraped_content)
            
            execution_time = time.time() - start_time
            logger.info(f"Brand scraping completed in {execution_time:.2f}s")
            
            return AgentResponse(
                success=True,
                data=scraped_content,
                execution_time=execution_time,
                metadata={
                    'url': url,
                    'content_length': len(scraped_content.main_content),
                    'sections_found': len(scraped_content.sections),
                    'depth_level': depth_level
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Brand scraping failed: {str(e)}")
            
            return AgentResponse(
                success=False,
                error_message=f"Scraping error: {str(e)}",
                execution_time=execution_time
            )
    
    async def _scrape_url(self, url: str) -> Optional[ScrapedContent]:
        """Scrape content from a single URL"""
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers=self.headers
                ) as session:
                    
                    async with session.get(url) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            return self._parse_html_content(url, html_content)
                        else:
                            logger.warning(f"HTTP {response.status} for {url}")
                            
            except Exception as e:
                logger.warning(f"Scraping attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1)  # Brief delay before retry
                
        return None
    
    def _parse_html_content(self, url: str, html_content: str) -> ScrapedContent:
        """Parse HTML content and extract meaningful brand information"""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract basic information
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title found"
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract main content areas
        main_content = self._extract_main_content(soup)
        
        # Extract navigation and structure
        navigation_links = self._extract_navigation_links(soup, url)
        
        # Extract metadata
        metadata = self._extract_metadata(soup, url)
        
        # Identify content sections
        sections = self._identify_content_sections(soup)
        
        return ScrapedContent(
            url=url,
            title=title_text,
            main_content=main_content,
            navigation_links=navigation_links,
            metadata=metadata,
            sections=sections,
            raw_html=html_content
        )
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract the main content text from the page"""
        
        # Look for main content areas (common patterns)
        main_selectors = [
            'main', '[role="main"]', '.main-content', '#main-content',
            '.content', '#content', 'article', '.article'
        ]
        
        main_content = ""
        
        for selector in main_selectors:
            elements = soup.select(selector)
            if elements:
                main_content = " ".join([elem.get_text().strip() for elem in elements])
                break
        
        # Fallback to body content if no main content found
        if not main_content:
            body = soup.find('body')
            if body:
                main_content = body.get_text()
        
        # Clean up whitespace
        main_content = " ".join(main_content.split())
        
        return main_content
    
    def _extract_navigation_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract navigation links to understand site structure"""
        
        nav_links = []
        
        # Look for navigation elements
        nav_selectors = ['nav', '.nav', '.navigation', '.menu', '.header-menu']
        
        for selector in nav_selectors:
            nav_elements = soup.select(selector)
            for nav in nav_elements:
                links = nav.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    full_url = urljoin(base_url, href)
                    nav_links.append(full_url)
        
        # Remove duplicates and filter for same domain
        parsed_base = urlparse(base_url)
        filtered_links = []
        
        for link in set(nav_links):
            parsed_link = urlparse(link)
            if parsed_link.netloc == parsed_base.netloc:
                filtered_links.append(link)
        
        return filtered_links[:10]  # Limit to first 10 navigation links
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata about the website and company"""
        
        metadata = {'url': url}
        
        # Extract meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            if meta.get('name') == 'description':
                metadata['description'] = meta.get('content', '')
            elif meta.get('name') == 'keywords':
                metadata['keywords'] = meta.get('content', '')
            elif meta.get('property') == 'og:title':
                metadata['og_title'] = meta.get('content', '')
            elif meta.get('property') == 'og:description':
                metadata['og_description'] = meta.get('content', '')
        
        # Try to identify company name
        company_indicators = [
            soup.find('title'),
            soup.find('meta', {'property': 'og:site_name'}),
            soup.find('h1'),
            soup.find('.logo'),
            soup.find('#logo')
        ]
        
        for indicator in company_indicators:
            if indicator:
                text = indicator.get_text() if hasattr(indicator, 'get_text') else indicator.get('content', '')
                if text:
                    metadata['company_name'] = text.strip()
                    break
        
        return metadata
    
    def _identify_content_sections(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Identify different content sections on the page"""
        
        sections = {}
        
        # Common section patterns for corporate websites
        section_patterns = {
            'hero': ['.hero', '.banner', '.jumbotron', '#hero'],
            'about': ['.about', '#about', '.company-info', '.overview'],
            'services': ['.services', '#services', '.products', '.offerings'],
            'values': ['.values', '#values', '.mission', '.vision'],
            'team': ['.team', '#team', '.leadership', '.people'],
            'contact': ['.contact', '#contact', '.get-in-touch']
        }
        
        for section_name, selectors in section_patterns.items():
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    section_text = " ".join([elem.get_text().strip() for elem in elements])
                    if section_text:
                        sections[section_name] = " ".join(section_text.split())[:1000]  # Limit length
                        break
        
        return sections
    
    async def _enhance_content_analysis(self, content: ScrapedContent) -> ScrapedContent:
        """Enhance content analysis for comprehensive depth"""
        
        # For comprehensive analysis, we could scrape additional pages
        # For now, we'll enhance the metadata analysis
        
        # Analyze content patterns
        enhanced_metadata = content.metadata.copy()
        
        # Count key corporate buzzwords
        buzzwords = ['innovative', 'solution', 'customer-centric', 'synergy', 'optimization', 
                    'digital transformation', 'best-in-class', 'cutting-edge', 'scalable']
        
        buzzword_count = 0
        content_lower = content.main_content.lower()
        for buzzword in buzzwords:
            buzzword_count += content_lower.count(buzzword.lower())
        
        enhanced_metadata['buzzword_density'] = buzzword_count
        enhanced_metadata['content_analysis'] = {
            'word_count': len(content.main_content.split()),
            'buzzword_count': buzzword_count,
            'sections_identified': len(content.sections)
        }
        
        # Return enhanced content
        return ScrapedContent(
            url=content.url,
            title=content.title,
            main_content=content.main_content,
            navigation_links=content.navigation_links,
            metadata=enhanced_metadata,
            sections=content.sections,
            raw_html=content.raw_html
        )
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate that we have a URL to scrape"""
        return input_data is not None and 'url' in input_data and input_data['url']
