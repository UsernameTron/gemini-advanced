"""
Voice Configuration System
Loads and manages voice profiles for the unified AI platform.
"""

import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VoiceProfile:
    """Represents a voice configuration profile."""
    id: str
    title: str
    description: str
    version: str
    category: str
    parameters: List[Dict[str, Any]]  # Changed from Dict to List to match template structure
    reasoning_modes: List[str]
    tone_mode: str
    constraints: Dict[str, Any]
    style_mandatory: List[str]
    style_forbidden: List[str]
    behavior_switches: Dict[str, str]  # Changed from List to Dict to match template structure
    target_definitions: Dict[str, Any]
    satire_mode_definitions: Dict[str, Any]
    icon: Optional[str] = None
    color: Optional[str] = None
    examples: Optional[List[Dict[str, Any]]] = None
    
    def get_param_options(self, param_id: str) -> List[Dict[str, str]]:
        """Get options for a specific parameter."""
        for param in self.parameters:
            if param.get('id') == param_id:
                return param.get('options', [])
        return []
    
    def get_param_default(self, param_id: str) -> Optional[str]:
        """Get default value for a specific parameter."""
        for param in self.parameters:
            if param.get('id') == param_id:
                return param.get('default')
        return None
    
    def get_param_label(self, param_id: str) -> Optional[str]:
        """Get label for a specific parameter."""
        for param in self.parameters:
            if param.get('id') == param_id:
                return param.get('label')
        return None


class VoiceConfigLoader:
    """Singleton class to load and manage voice profiles."""
    
    _instance = None
    _profiles: Dict[str, VoiceProfile] = {}
    _current_profile: Optional[VoiceProfile] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VoiceConfigLoader, cls).__new__(cls)
            cls._instance._load_profiles()
        return cls._instance
    
    def _load_profiles(self):
        """Load all voice profiles from the voice directory."""
        voice_dir = Path(__file__).parent
        profile_files = voice_dir.glob("*_profile.json")
        
        for profile_file in profile_files:
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                profile = VoiceProfile(
                    id=data.get('id', ''),
                    title=data.get('title', ''),
                    description=data.get('description', ''),
                    version=data.get('version', '1.0'),
                    category=data.get('category', ''),
                    parameters=data.get('parameters', []),
                    reasoning_modes=data.get('reasoningModes', []),
                    tone_mode=data.get('toneMode', ''),
                    constraints=data.get('constraints', {}),
                    style_mandatory=data.get('styleMandatory', []),
                    style_forbidden=data.get('styleForbidden', []),
                    behavior_switches=data.get('behaviorSwitches', {}),
                    target_definitions=data.get('targetDefinitions', {}),
                    satire_mode_definitions=data.get('satireModeDefinitions', {}),
                    icon=data.get('icon'),
                    color=data.get('color'),
                    examples=data.get('examples', [])
                )
                
                self._profiles[profile.id] = profile
                
                # Set default profile
                if not self._current_profile or profile.id == 'satirical-voice':
                    self._current_profile = profile
                    
            except Exception as e:
                print(f"Error loading voice profile {profile_file}: {e}")
    
    def get_profile(self, profile_id: Optional[str] = None) -> Optional[VoiceProfile]:
        """Get a specific voice profile or the current one."""
        if profile_id:
            return self._profiles.get(profile_id)
        return self._current_profile
    
    def set_current_profile(self, profile_id: str) -> bool:
        """Set the current active voice profile."""
        if profile_id in self._profiles:
            self._current_profile = self._profiles[profile_id]
            return True
        return False
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available profile IDs."""
        return list(self._profiles.keys())
    
    def get_current_param(self, param_id: str, default_value: Any = None) -> Any:
        """Get a parameter value from the current profile."""
        if self._current_profile:
            for param in self._current_profile.parameters:
                if param.get('id') == param_id:
                    return param.get('default', default_value)
        return default_value
    
    def get_current_param_options(self, param_id: str) -> List[Dict[str, str]]:
        """Get parameter options from the current profile."""
        if self._current_profile:
            return self._current_profile.get_param_options(param_id)
        return []
    
    def get_voice_style_prompt(self, voice_style: Optional[str] = None) -> str:
        """Generate prompt text based on voice style."""
        profile = self._current_profile
        if not profile:
            return ""
        
        if not voice_style:
            voice_style = self.get_current_param('voiceStyle')
        
        if voice_style and voice_style in profile.satire_mode_definitions:
            mode_def = profile.satire_mode_definitions[voice_style]
            return f"Adopt a {mode_def.get('description', '')} style. {mode_def.get('tone', '')} Use {mode_def.get('language', '')} language."
        
        return ""
    
    def build_system_prompt_prefix(self, session_config: Optional[Dict[str, Any]] = None) -> str:
        """Build a system prompt prefix based on current voice configuration."""
        profile = self._current_profile
        if not profile:
            return ""
        
        # Extract session-specific settings or use defaults
        if session_config:
            target = session_config.get('target', self.get_current_param('target'))
            satire_mode = session_config.get('satireModes', self.get_current_param('satireModes'))
            voice_style = session_config.get('voiceStyle', self.get_current_param('voiceStyle'))
        else:
            target = self.get_current_param('target')
            satire_mode = self.get_current_param('satireModes')
            voice_style = self.get_current_param('voiceStyle')
        
        prompt_parts = []
        
        # Add voice style context
        if voice_style and voice_style in profile.satire_mode_definitions:
            mode_def = profile.satire_mode_definitions[voice_style]
            prompt_parts.append(f"You are a {mode_def.get('description', '')} commentator.")
        
        # Add target context
        if target and target in profile.target_definitions:
            target_def = profile.target_definitions[target]
            prompt_parts.append(f"Focus on {target_def.get('description', '')}.")
        
        # Add satire mode context
        if satire_mode and satire_mode in profile.satire_mode_definitions:
            mode_def = profile.satire_mode_definitions[satire_mode]
            prompt_parts.append(f"Use {mode_def.get('humor', '')} with {mode_def.get('restraint', '')} restraint.")
        
        # Add style constraints
        if profile.style_mandatory:
            prompt_parts.append(f"Always include: {', '.join(profile.style_mandatory[:3])}.")
        
        if profile.style_forbidden:
            prompt_parts.append(f"Never: {', '.join(profile.style_forbidden[:3])}.")
        
        return " ".join(prompt_parts)


# Singleton instance
voice_loader = VoiceConfigLoader()


def get_current_param(param_key: str, default_value: Any = None) -> Any:
    """Helper function to get current voice parameter."""
    return voice_loader.get_current_param(param_key, default_value)


def get_current_param_options(param_key: str) -> List[Dict[str, str]]:
    """Helper function to get current voice parameter options."""
    return voice_loader.get_current_param_options(param_key)


def build_voice_prompt_prefix(session_config: Optional[Dict[str, Any]] = None) -> str:
    """Helper function to build voice-aware prompt prefix."""
    return voice_loader.build_system_prompt_prefix(session_config)


def get_voice_profile(profile_id: Optional[str] = None) -> Optional[VoiceProfile]:
    """Helper function to get voice profile."""
    return voice_loader.get_profile(profile_id)


def set_voice_profile(profile_id: str) -> bool:
    """Helper function to set current voice profile."""
    return voice_loader.set_current_profile(profile_id)
