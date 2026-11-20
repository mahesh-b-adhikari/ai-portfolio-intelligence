from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6",
    input="Reply with exactly: API connection successful"
)

print(response.output_text)