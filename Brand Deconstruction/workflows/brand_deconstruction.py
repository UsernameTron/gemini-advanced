# File: workflows/brand_deconstruction.py

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import asyncio
import logging
import time
from datetime import datetime

# Import all our agents
from core.base_agents import AgentManager, AgentResponse
from agents.brand_scraper import BrandScrapingAgent
from agents.brand_analyzer import BrandAnalysisAgent  
from agents.satirical_generator import SatiricalPromptAgent

logger = logging.getLogger(__name__)

@dataclass
class BrandDeconstructionRequest:
    """Request structure for brand deconstruction analysis"""
    url: str
    satirical_intensity: str = "medium"  # low, medium, high
    style_preference: str = "contradiction_expose"  # or "buzzword_deflation", "aspiration_mockery"
    output_variations: int = 3
    depth_level: str = "comprehensive"  # basic, comprehensive, deep_dive

@dataclass 
class BrandDeconstructionResult:
    """Complete result from brand deconstruction analysis"""
    success: bool
    scraped_content: Any = None
    brand_analysis: Any = None
    satirical_prompts: Dict[str, Any] = None
    primary_satirical_prompt: Any = None
    execution_summary: Dict[str, Any] = None
    total_processing_time: float = 0
    error_message: Optional[str] = None

class CompleteBrandDeconstructionWorkflow:
    """
    Complete workflow orchestrating the Brand Deconstruction Engine.
    
    This workflow coordinates the entire pipeline from URL input to 
    finished satirical prompt generation, managing all agents and
    ensuring proper data flow between analysis phases.
    """
    
    def __init__(self, agent_manager: AgentManager = None):
        self.agent_manager = agent_manager or AgentManager()
        self.performance_history = []
        
        # Register all required agents
        self._register_agents()
        
    def _register_agents(self):
        """Register all agents required for the workflow"""
        # These agents should be implemented in their respective files
        self.agent_manager.register_agent('brand_scraper', BrandScrapingAgent)
        self.agent_manager.register_agent('brand_analyzer', BrandAnalysisAgent)
        self.agent_manager.register_agent('satirical_generator', SatiricalPromptAgent)
        
    async def execute_complete_deconstruction(self, request: BrandDeconstructionRequest) -> BrandDeconstructionResult:
        """
        Execute the complete brand deconstruction pipeline.
        """
        
        start_time = time.time()
        logger.info(f"Starting complete brand deconstruction for: {request.url}")
        
        try:
            # Phase 1: Brand Content Scraping
            logger.info("Phase 1: Brand content scraping")
            scraping_agent = self.agent_manager.create_agent('brand_scraper')
            scraping_result = await scraping_agent.execute({
                'url': request.url,
                'depth_level': request.depth_level
            })
            
            if not scraping_result.success:
                return BrandDeconstructionResult(
                    success=False,
                    error_message=f"Scraping failed: {scraping_result.error_message}",
                    total_processing_time=time.time() - start_time
                )
            
            # Phase 2: Brand Analysis
            logger.info("Phase 2: Brand contradiction analysis")
            analysis_agent = self.agent_manager.create_agent('brand_analyzer')
            analysis_result = await analysis_agent.execute({
                'scraped_content': scraping_result.data,
                'satirical_intensity': request.satirical_intensity,
                'url': request.url
            })
            
            if not analysis_result.success:
                return BrandDeconstructionResult(
                    success=False,
                    scraped_content=scraping_result.data,
                    error_message=f"Analysis failed: {analysis_result.error_message}",
                    total_processing_time=time.time() - start_time
                )
            
            # Phase 3: Satirical Prompt Generation
            logger.info("Phase 3: Satirical prompt generation")
            satirical_agent = self.agent_manager.create_agent('satirical_generator')
            satirical_result = await satirical_agent.execute({
                'brand_analysis': analysis_result.data,
                'style_preference': request.style_preference,
                'output_variations': request.output_variations,
                'satirical_intensity': request.satirical_intensity
            })
            
            if not satirical_result.success:
                return BrandDeconstructionResult(
                    success=False,
                    scraped_content=scraping_result.data,
                    brand_analysis=analysis_result.data,
                    error_message=f"Satirical generation failed: {satirical_result.error_message}",
                    total_processing_time=time.time() - start_time
                )
            
            # Compile complete results
            total_processing_time = time.time() - start_time
            
            # Extract primary prompt for easy access
            primary_prompt = None
            if satirical_result.data and 'primary_prompt' in satirical_result.data:
                primary_prompt = satirical_result.data['primary_prompt']
            
            # Create execution summary
            execution_summary = {
                'success': True,
                'total_execution_time': total_processing_time,
                'phases_completed': 3,
                'prompts_generated': len(satirical_result.data.get('alternative_variations', [])) + 1,
                'authenticity_score': analysis_result.data.authenticity_score if hasattr(analysis_result.data, 'authenticity_score') else 0,
                'vulnerabilities_found': len(analysis_result.data.satirical_vulnerabilities) if hasattr(analysis_result.data, 'satirical_vulnerabilities') else 0
            }
            
            # Record performance
            self.performance_history.append({
                'timestamp': datetime.now().isoformat(),
                'url': request.url,
                'execution_time': total_processing_time,
                'success': True,
                'phases_completed': 3
            })
            
            logger.info(f"Brand deconstruction completed successfully in {total_processing_time:.2f}s")
            
            return BrandDeconstructionResult(
                success=True,
                scraped_content=scraping_result.data,
                brand_analysis=analysis_result.data,
                satirical_prompts=satirical_result.data,
                primary_satirical_prompt=primary_prompt,
                execution_summary=execution_summary,
                total_processing_time=total_processing_time
            )
            
        except Exception as e:
            total_processing_time = time.time() - start_time
            logger.error(f"Brand deconstruction failed: {str(e)}")
            
            # Record failure
            self.performance_history.append({
                'timestamp': datetime.now().isoformat(),
                'url': request.url,
                'execution_time': total_processing_time,
                'success': False,
                'error': str(e)
            })
            
            return BrandDeconstructionResult(
                success=False,
                error_message=f"Workflow execution failed: {str(e)}",
                total_processing_time=total_processing_time
            )
    
    async def batch_process_urls(self, urls: List[str], common_params: Dict[str, Any]) -> List[BrandDeconstructionResult]:
        """
        Process multiple URLs in batch with controlled concurrency.
        """
        
        logger.info(f"Starting batch processing of {len(urls)} URLs")
        
        # Create requests for all URLs
        requests = []
        for url in urls:
            request = BrandDeconstructionRequest(
                url=url,
                satirical_intensity=common_params.get('satirical_intensity', 'medium'),
                style_preference=common_params.get('style_preference', 'contradiction_expose'),
                output_variations=common_params.get('output_variations', 3),
                depth_level=common_params.get('depth_level', 'comprehensive')
            )
            requests.append(request)
        
        # Process with controlled concurrency (avoid overwhelming target sites)
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests
        
        async def process_with_semaphore(request):
            async with semaphore:
                # Add small delay between requests
                await asyncio.sleep(0.5)
                return await self.execute_complete_deconstruction(request)
        
        # Execute all requests
        results = await asyncio.gather(
            *[process_with_semaphore(req) for req in requests],
            return_exceptions=True
        )
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch processing failed for {urls[i]}: {str(result)}")
                processed_results.append(BrandDeconstructionResult(
                    success=False,
                    error_message=f"Processing failed: {str(result)}",
                    total_processing_time=0
                ))
            else:
                processed_results.append(result)
        
        successful_count = sum(1 for r in processed_results if r.success)
        logger.info(f"Batch processing completed: {successful_count}/{len(urls)} successful")
        
        return processed_results
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring"""
        
        if not self.performance_history:
            return {
                'total_executions': 0,
                'success_rate': 0,
                'average_execution_time': 0
            }
        
        total_executions = len(self.performance_history)
        successful_executions = sum(1 for h in self.performance_history if h.get('success', False))
        success_rate = successful_executions / total_executions
        
        execution_times = [h.get('execution_time', 0) for h in self.performance_history if h.get('success', False)]
        average_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        return {
            'total_executions': total_executions,
            'success_rate': success_rate,
            'average_execution_time': average_execution_time,
            'recent_performance': self.performance_history[-10:]  # Last 10 executions
        }
