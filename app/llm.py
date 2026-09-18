import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("HKUST_API_KEY")

if not api_key:
    raise RuntimeError("HKUST_API_KEY is not set.")


client = OpenAI(
    base_url="https://hkust.azure-api.net/hkust-genai/v1",
    api_key=api_key,
    default_headers={
        "api-key": api_key,
    },
)


def generate_answer(
    system_prompt: str,
    user_prompt: str,
) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    return response.choices[0].message.content