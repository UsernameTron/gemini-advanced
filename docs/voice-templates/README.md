# Voice Template System Documentation

## Overview

The Voice Template System allows dynamic parameterization of AI agent behavior through structured JSON templates that define voice characteristics, satirical targets, behavioral switches, and style parameters.

## Architecture

### Components

1. **Voice Templates** (`voice/`)
   - `satirical_voice_template.json` - Pure JSON template with parameters
   - `voice_config.py` - Template loader and prompt generation
   - `voice_routes.py` - Flask API routes for voice management

2. **Session Integration** (`agent_system/`)
   - `web_interface.py` - Session manager with voice configuration methods
   - Templates include UI controls for voice parameter selection

3. **Original Reference** (`docs/voice-templates/`)
   - `satiricalVoiceTemplate_unleashed.ts` - Original TypeScript implementation

## Template Structure

### JSON Format
```json
{
  "id": "voice-identifier",
  "title": "Human-readable title",
  "description": "Template description",
  "parameters": [
    {
      "id": "parameter_name",
      "label": "UI Label",
      "type": "select|textarea|text",
      "options": [...],
      "default": "default_value",
      "required": true|false
    }
  ],
  "behaviorSwitches": {
    "mode_name": "Behavior description"
  },
  "targetDefinitions": {
    "target_name": {
      "description": "Target description",
      "elements": [...],
      "references": [...],
      "absurdities": [...]
    }
  }
}
```

## UI Integration

### Voice Configuration Panel
- **Profile Selection**: Default vs. Satirical voice
- **Dynamic Controls**: Show/hide based on profile selection
- **Session Persistence**: Configuration saved to localStorage and session
- **Real-time Updates**: Voice status indicator shows current configuration

### API Endpoints
- `GET /api/voice/profiles` - List available voice profiles
- `POST /api/voice/session-config` - Set voice configuration for session
- `GET /api/voice/session-config` - Get current session voice configuration
- `POST /api/voice/generate-prompt` - Generate prompt with voice configuration

## Prompt Generation

The system generates voice-aware prompts by:

1. Loading base template parameters
2. Applying user-selected configuration
3. Building behavioral context from switches and targets
4. Injecting into agent prompt assembly

### Example Flow
```python
# Load voice configuration
voice_config = session_manager.get_voice_config(session_id)

# Generate voice prompt prefix
voice_prefix = build_voice_prompt_prefix('satirical', voice_config)

# Combine with agent prompt
full_prompt = f"{voice_prefix}\n\n{agent_prompt}\n\n{user_message}"
```

## Implementation Notes

### Step-by-Step Integration
1. ✅ Convert TypeScript template to JSON format
2. ✅ Create voice configuration loader system
3. ✅ Integrate with session manager
4. ✅ Add UI controls to dashboard
5. ✅ Inject into prompt assembly
6. ✅ Archive original TypeScript for reference

### Key Features
- **Session-scoped Configuration**: Voice settings persist per user session
- **Auto-generated UI**: Dropdowns and controls generated from JSON parameters
- **Behavioral Switches**: Different satirical modes with distinct characteristics
- **Target Definitions**: Rich context for different satirical targets
- **Extensible Design**: Easy to add new voice templates and parameters

## Future Enhancements

1. **Multi-template Support**: Load multiple voice templates dynamically
2. **Template Validation**: JSON schema validation for templates
3. **Advanced UI**: Rich text editors, preview modes, template customization
4. **Analytics**: Track voice configuration usage patterns
5. **A/B Testing**: Compare response quality across voice configurations

## Usage Examples

### Corporate Satire Configuration
```json
{
  "profile": "satirical",
  "target": "corporate",
  "satireModes": "strategic-snark",
  "voiceStyle": "caustic",
  "outputFormat": "essay"
}
```

### Tech Industry Commentary
```json
{
  "profile": "satirical",
  "target": "tech",
  "satireModes": "high-satire",
  "voiceStyle": "insider",
  "outputFormat": "review"
}
```

This system establishes the core infrastructure for voice parameterization while maintaining the sophisticated satirical capabilities of the original template.
