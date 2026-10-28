from llm_config import load_llm_config


def main():
    try:
        config = load_llm_config()
    except RuntimeError as error:
        print(f"LLM configuration error: {error}")
        return

    endpoint = config.base_url or "https://api.openai.com/v1"
    print(f"LLM configuration loaded for model '{config.model}' at {endpoint}")


if __name__ == '__main__':
    main()
