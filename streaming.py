from openai import OpenAI
import sys

client = OpenAI(
        base_url = "http://llama3.model/v1",
        #base_url = "http://llama3.llama-vllm-serving.192.168.2.100.sslip.io/v1",
        api_key="token-abc123",
    )

stream = client.chat.completions.create(
    model="llama3",
    messages=[{"role": "user", "content": "Write a fun story on growing up in the prairie."}],
    stream=True,
    max_tokens = 200,
    stop=["\n", "<|endoftext|>"],
)
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
