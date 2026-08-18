"""Spike: list models currently available from Groq's inference API."""

import os

from dotenv import load_dotenv
from groq import Groq


def main() -> None:
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise RuntimeError(
            "GROQ_API_KEY is missing or still uses the placeholder value."
        )

    client = Groq(api_key=api_key)
    models = client.models.list()

    print("Models currently available through Groq:")
    for model in models.data:
        print(f"- {model.id}")


if __name__ == "__main__":
    main()
