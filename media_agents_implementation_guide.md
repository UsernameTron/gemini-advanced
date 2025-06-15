
# Media Agents Implementation Guide

## ImageAgent Implementation
```python
async def execute(self, image_path: str, instruction: str) -> str:
    try:
        import base64
        from openai import OpenAI
        
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        response = self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": instruction},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error processing image: {e}"
```

## AudioAgent Implementation  
```python
async def execute(self, audio_path: str, instruction: str) -> str:
    try:
        from openai import OpenAI
        
        with open(audio_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return f"Transcript: {transcript.text}"
    except Exception as e:
        return f"Error processing audio: {e}"
```
