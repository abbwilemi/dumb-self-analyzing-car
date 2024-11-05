from openai import OpenAI
from pathlib import Path
client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an idiot car that can talk"},
        {
            "role": "user",
            "content": "You just rammed into a wall, use swearwords"
        }
    ]
)

content_text = completion.choices[0].message.content
print(content_text)

# speech
speech_file_path = Path(__file__).parent / "speech.mp3"
response = client.audio.speech.create(
  model="tts-1",
  voice="onyx",
  input=content_text
)

response.stream_to_file(speech_file_path)