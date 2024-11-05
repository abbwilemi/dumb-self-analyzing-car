from openai import OpenAI
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
