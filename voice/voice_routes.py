"""
Voice Configuration API Routes
Provides endpoints for managing voice profiles and parameters
"""

from flask import Blueprint, request, jsonify, session
from typing import Dict, Any, List, Optional
import json
import os
import sys

# Import voice configuration system
sys.path.append('/Users/cpconnor/projects/UnifiedAIPlatform')
from voice.voice_config import voice_loader, build_voice_prompt_prefix, get_current_param

# Create blueprint for voice routes
voice_bp = Blueprint('voice', __name__, url_prefix='/api/voice')


@voice_bp.route('/profiles', methods=['GET'])
def get_voice_profiles():
    """Get available voice profiles."""
    try:
        profiles = []
        for profile_id in voice_loader.get_available_profiles():
            profile = voice_loader.get_profile(profile_id)
            if profile:
                profiles.append({
                    'id': profile.id,
                    'title': profile.title,
                    'description': profile.description,
                    'version': profile.version,
                    'category': profile.category,
                    'icon': profile.icon,
                    'color': profile.color
                })
        
        return jsonify({
            'success': True,
            'profiles': profiles
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@voice_bp.route('/profiles/<profile_id>', methods=['GET'])
def get_voice_profile(profile_id: str):
    """Get detailed voice profile configuration."""
    try:
        profile = voice_loader.get_profile(profile_id)
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
        
        return jsonify({
            'success': True,
            'profile': {
                'id': profile.id,
                'title': profile.title,
                'description': profile.description,
                'version': profile.version,
                'category': profile.category,
                'icon': profile.icon,
                'color': profile.color,
                'parameters': profile.parameters,
                'reasoning_modes': profile.reasoning_modes,
                'tone_mode': profile.tone_mode,
                'constraints': profile.constraints,
                'style_mandatory': profile.style_mandatory,
                'style_forbidden': profile.style_forbidden,
                'behavior_switches': profile.behavior_switches,
                'target_definitions': profile.target_definitions,
                'satire_mode_definitions': profile.satire_mode_definitions,
                'examples': profile.examples or []
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@voice_bp.route('/current', methods=['GET'])
def get_current_voice_profile():
    """Get current active voice profile."""
    try:
        profile = voice_loader.get_profile()
        if not profile:
            return jsonify({
                'success': False,
                'error': 'No active profile'
            }), 404
        
        return jsonify({
            'success': True,
            'current_profile': profile.id,
            'profile': {
                'id': profile.id,
                'title': profile.title,
                'description': profile.description,
                'parameters': profile.parameters
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@voice_bp.route('/current', methods=['POST'])
def set_current_voice_profile():
    """Set current active voice profile."""
    try:
        data = request.get_json()
        profile_id = data.get('profile_id')
        
        if not profile_id:
            return jsonify({
                'success': False,
                'error': 'Profile ID is required'
            }), 400
        
        success = voice_loader.set_current_profile(profile_id)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
        
        return jsonify({
            'success': True,
            'current_profile': profile_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@voice_bp.route('/session/config', methods=['GET'])
def get_session_voice_config():
    """Get voice configuration for current session."""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No session found'
            }), 400
        
        # Get session-specific voice config from session manager
        # For now, return current profile defaults
        profile = voice_loader.get_profile()
        if not profile:
            return jsonify({
                'success': False,
                'error': 'No active profile'
            }), 404
        
        # Extract default values from parameters
        session_config = {}
        for param in profile.parameters:
            param_id = param.get('id')
            default_value = param.get('default')
            if param_id and default_value:
                session_config[param_id] = default_value
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'voice_config': session_config,
            'profile_id': profile.id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@voice_bp.route('/session/config', methods=['POST'])
def update_session_voice_config():
    """Update voice configuration for current session."""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No session found'
            }), 400
        
        data = request.get_json()
        voice_config = data.get('voice_config', {})
        
        # Store voice config in session
        session['voice_config'] = voice_config
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'voice_config': voice_config,
            'message': 'Voice configuration updated'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@voice_bp.route('/prompt-prefix', methods=['POST'])
def generate_voice_prompt_prefix():
    """Generate voice-aware prompt prefix for current session."""
    try:
        data = request.get_json()
        voice_config = data.get('voice_config', {})
        
        # If no config provided, try to get from session
        if not voice_config:
            voice_config = session.get('voice_config', {})
        
        # Generate prompt prefix
        prompt_prefix = build_voice_prompt_prefix(voice_config if voice_config else None)
        
        return jsonify({
            'success': True,
            'prompt_prefix': prompt_prefix,
            'voice_config': voice_config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@voice_bp.route('/parameters/<profile_id>/<param_id>/options', methods=['GET'])
def get_parameter_options(profile_id: str, param_id: str):
    """Get options for a specific parameter."""
    try:
        profile = voice_loader.get_profile(profile_id)
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
        
        options = profile.get_param_options(param_id)
        default = profile.get_param_default(param_id)
        label = profile.get_param_label(param_id)
        
        return jsonify({
            'success': True,
            'parameter': {
                'id': param_id,
                'label': label,
                'options': options,
                'default': default
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def register_voice_routes(app):
    """Register voice configuration routes with the Flask app."""
    app.register_blueprint(voice_bp)
    print("✅ Voice configuration routes registered")
