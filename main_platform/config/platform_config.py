"""
Comprehensive Configuration Management for Brand Deconstruction Platform
This centralizes all configuration settings and provides environment-specific configurations
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
import json
from pathlib import Path

@dataclass
class ImageGenerationConfig:
    """Configuration for GPT-Image-1 integration"""
    model: str = "dall-e-3"
    size: str = "1536x1024" 
    quality: str = "hd"
    style: str = "vivid"
    max_retries: int = 3
    timeout: int = 120
    cost_per_image: float = 0.080
    
@dataclass
class AgentConfig:
    """Configuration for AI agents"""
    default_model: str = "gpt-4"
    max_concurrent_agents: int = 5
    agent_timeout: int = 300
    retry_attempts: int = 3
    
@dataclass
class SecurityConfig:
    """Security and API configuration"""
    openai_api_key: Optional[str] = None
    rate_limit_per_minute: int = 60
    max_requests_per_hour: int = 1000
    enable_request_logging: bool = True
    cors_origins: list = None
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000", "http://localhost:5002"]

@dataclass
class DatabaseConfig:
    """Database configuration for campaign storage"""
    database_url: str = "sqlite:///campaigns.db"
    enable_analytics: bool = True
    retention_days: int = 90
    backup_enabled: bool = True

class PlatformConfig:
    """Main configuration manager for the Brand Deconstruction Platform"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.image_generation = ImageGenerationConfig()
        self.agents = AgentConfig()
        self.security = SecurityConfig()
        self.database = DatabaseConfig()
        
        # Load environment-specific settings
        self._load_environment_config()
        self._load_secrets()
    
    def _load_environment_config(self):
        """Load configuration based on environment"""
        config_file = Path(f"config/{self.environment}.json")
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                self._apply_config_overrides(config_data)
    
    def _load_secrets(self):
        """Load sensitive configuration from environment variables"""
        self.security.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Validate required secrets
        if not self.security.openai_api_key and self.environment == "production":
            raise ValueError("OPENAI_API_KEY is required for production environment")
    
    def _apply_config_overrides(self, config_data: Dict[str, Any]):
        """Apply configuration overrides from JSON file"""
        for section, values in config_data.items():
            if hasattr(self, section):
                section_config = getattr(self, section)
                for key, value in values.items():
                    if hasattr(section_config, key):
                        setattr(section_config, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'environment': self.environment,
            'image_generation': self.image_generation.__dict__,
            'agents': self.agents.__dict__,
            'security': {k: v for k, v in self.security.__dict__.items() if k != 'openai_api_key'},
            'database': self.database.__dict__
        }
