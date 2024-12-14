import base64
import json
from openai import OpenAI

class AIActions:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def audio_to_text(self, audio_path):
        # Transcribe audio using Whisper model
        with open(audio_path, "rb") as audio_file:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcription.text

    def image_to_text(self, image_path, prompt="What is in this image?"):
        # Encode image in base64
        base64_image = self._encode_image(image_path)

        # Get description from GPT model
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
        )
        return response.choices[0].message.content
            
    def ask_about_wall_in_image(self, image_path):
        # Encode image in base64
        base64_image = self._encode_image(image_path)

        # Updated prompt asking about walls and directions, and requesting a JSON response.
        prompt = [
            {
                "type": "text",
                "text": (
                    "Look at the image provided and respond in the following JSON format:\n"
                    "{\n"
                    "  \"description\": \"A detailed description of what is in the image, focusing heavily on one small detail.\",\n"
                    "  \"action\": \"left\"/\"right\"/\"forward\"\n"
                    "}\n\n"
                    "The camera is mounted on a small car, so consider the perspective as being low to the ground and close to obstacles.\n"
                    "If there is a wall or obstacle directly ahead, choose either \"left\" or \"right\" to avoid steering the car into a corner.\n"
                    "If there is no immediate wall or obstacle blocking forward movement, choose \"forward\".\n"
                    "Decide on the direction that most likely allows the car to continue without getting trapped or cornered.\n\n"
                    "Now, analyze the image carefully and produce ONLY the JSON object as described."
                )
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                },
            },
        ]

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )
        response_text = response.choices[0].message.content.strip()

        # Find the indices of the actual JSON object
        start = response_text.find('{')
        end = response_text.rfind('}')

        if start != -1 and end != -1:
            json_content = response_text[start:end+1].strip()
            try:
                result = json.loads(json_content)
                description = result.get("description", "")
                action = result.get("action", "")
                return description, action
            except json.JSONDecodeError:
                print("The AI did not return valid JSON.")
                return None, None
        else:
            print("Could not find a JSON object in the response.")
            return None, None
    
    def ask(self, text):
        # A generic method to send text queries to the AI
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": text
                }
            ],
        )
        return response.choices[0].message.content.strip()

    def text_to_audio(self, text, output_path):
        # Generate audio from text using a special model (as per the provided code)
        completion = self.client.chat.completions.create(
            model="gpt-4o-audio-preview",
            modalities=["text", "audio"],
            audio={"voice": "onyx", "format": "mp3"},
            messages=[
                {
                    "role": "user",
                    "content": text
                }
            ]
        )
        # Save the audio
        wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)
        with open(output_path, "wb") as f:
            f.write(wav_bytes)

    @staticmethod
    def _encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')