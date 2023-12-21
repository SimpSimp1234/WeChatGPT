from openai import OpenAI

client = OpenAI(
    api_key="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",
)

# Upload a file with an "assistants" purpose
file = client.files.create(
  file=open("", "rb"),
  purpose='assistants'
)

print(file)