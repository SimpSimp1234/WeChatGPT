from openai import OpenAI
client = OpenAI(
    api_key='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'
)

print(client.models.list())