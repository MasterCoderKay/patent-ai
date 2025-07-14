import os
from openai import OpenAI

print('=== Minimal Groq Test ===')
print('Key exists:', bool(os.getenv('GROQ_API_KEY')))

try:
    client = OpenAI(
        api_key=os.getenv('GROQ_API_KEY'),
        base_url='https://api.groq.com/openai/v1'
    )
    response = client.chat.completions.create(
        model='llama3-8b-8192',
        messages=[{'role':'user','content':'Hello'}],
        max_tokens=5
    )
    print('Success! Response:', response.choices[0].message.content)
except Exception as e:
    print(f'FAILED: {str(e)}')
