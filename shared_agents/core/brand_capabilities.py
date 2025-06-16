"""
Enhanced agent capabilities specifically for Brand Deconstruction Platform
Extends the existing AgentCapability enum with brand analysis capabilities
"""

from enum import Enum
from shared_agents.core.agent_factory import AgentCapability

class BrandCapability(Enum):
    """Extended capabilities for brand deconstruction and satirical analysis"""
    
    # Core Brand Analysis
    BRAND_POSITIONING_ANALYSIS = "brand_positioning_analysis"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    CLAIMS_VALIDATION = "claims_validation"
    AUTHENTICITY_SCORING = "authenticity_scoring"
    
    # Satirical Content Generation
    SATIRICAL_CONTENT_CREATION = "satirical_content_creation"
    PENTAGRAM_FRAMEWORK_ANALYSIS = "pentagram_framework_analysis"
    VIRAL_POTENTIAL_SCORING = "viral_potential_scoring"
    
    # Advanced Image Generation
    GPT_IMAGE_INTEGRATION = "gpt_image_integration"
    VISUAL_SATIRE_GENERATION = "visual_satire_generation"
    
    # Market Analysis
    MARKET_POSITIONING_AUDIT = "market_positioning_audit"
    TECHNICAL_CREDIBILITY_ASSESSMENT = "technical_credibility_assessment"
    CUSTOMER_EXPERIENCE_ANALYSIS = "customer_experience_analysis"
    
    # Additional needed capabilities
    MARKET_INTELLIGENCE = "market_intelligence"
    VOICE_SYNTHESIS = "voice_synthesis"
    VISUAL_CONTENT_CREATION = "visual_content_creation"
    BRAND_ASSET_GENERATION = "brand_asset_generation"
