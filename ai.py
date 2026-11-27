import os
from notopenai import NotOpenAI

# Set CIP_API_KEY in your terminal before running the project.
API_KEY = os.environ.get("CIP_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "CIP_API_KEY is not set. Set your API key as an environment variable."
    )

client = NotOpenAI(API_KEY)


def call_gpt(prompt):
    """Send a prompt to the configured AI model and return its text response."""
    response = client.responses.create(
        model="gpt-5-nano",
        input=prompt
    )
    return response.output_text
