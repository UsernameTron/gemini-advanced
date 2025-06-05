import os
from datetime import datetime
from config import Config


class TTSService:
    """
    Service for generating speech using OpenAI Text-to-Speech API.
    """
    def __init__(self):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai library is required for TTSService")
        config = Config()
        config.validate()
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.supported_models = ["tts-1", "tts-1-hd", "gpt-4o-mini-tts"]
        self.supported_voices = [
            "alloy", "ash", "ballad", "coral", "echo",
            "fable", "onyx", "nova", "sage", "shimmer", "verse"
        ]
        self.supported_formats = ["mp3", "opus", "aac", "flac", "wav", "pcm"]

    def generate_speech(
        self,
        text: str,
        model: str = "tts-1",
        voice: str = "alloy",
        instructions: str = None,
        response_format: str = "mp3",
        speed: float = 1.0
    ) -> dict:
        """
        Generate speech from text using OpenAI TTS API.
        Returns a dict with success flag, audio_data bytes, or error details.
        """
        try:
            if not text or len(text) > 4096:
                raise ValueError("Text must be 1-4096 characters")
            if model not in self.supported_models:
                raise ValueError(f"Model {model} not supported")
            if voice not in self.supported_voices:
                raise ValueError(f"Voice {voice} not supported")
            if response_format not in self.supported_formats:
                raise ValueError(f"Format {response_format} not supported")
            if not (0.25 <= speed <= 4.0):
                raise ValueError("Speed must be between 0.25 and 4.0")

            params = {
                "model": model,
                "voice": voice,
                "input": text,
                "response_format": response_format
            }
            if instructions and model == "gpt-4o-mini-tts":
                params["instructions"] = instructions
            if speed != 1.0 and model != "gpt-4o-mini-tts":
                params["speed"] = speed

            response = self.client.audio.speech.create(**params)
            return {
                "success": True,
                "audio_data": response.content,
                "format": response_format,
                "params": params,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

    def save_audio(self, audio_data: bytes, filename: str = None, format: str = "mp3") -> str:
        """
        Save audio bytes to a file under generated_audio/.
        Returns the file path.
        """
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"tts_output_{timestamp}.{format}"
        os.makedirs("generated_audio", exist_ok=True)
        filepath = os.path.join("generated_audio", filename)
        with open(filepath, "wb") as f:
            f.write(audio_data)
        return filepath

    def get_voice_preview_text(self, voice: str) -> str:
        """
        Return a sample sentence for voice preview.
        """
        previews = {
            "alloy": "I'm Alloy, a balanced and versatile voice perfect for any content.",
            "ash": "I'm Ash, with a clear and professional tone ideal for business communications.",
            "ballad": "I'm Ballad, bringing a warm and storytelling quality to your text.",
            "coral": "I'm Coral, offering a friendly and approachable voice for conversations.",
            "echo": "I'm Echo, providing a distinctive and memorable audio experience.",
            "fable": "I'm Fable, perfect for narrating stories with engaging expression.",
            "onyx": "I'm Onyx, delivering a deep and authoritative voice for serious content.",
            "nova": "I'm Nova, bright and energetic, great for dynamic presentations.",
            "sage": "I'm Sage, wise and measured, ideal for educational content.",
            "shimmer": "I'm Shimmer, light and pleasant, perfect for cheerful messages.",
            "verse": "I'm Verse, poetic and expressive, bringing life to creative content."
        }
        return previews.get(voice, f"This is a preview of the {voice} voice.")