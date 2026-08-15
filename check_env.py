from dotenv import load_dotenv
import os


def main():
    load_dotenv()  # reads .env in current working directory
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        print("GROQ_API_KEY loaded")
    else:
        print("GROQ_API_KEY not found")


if __name__ == '__main__':
    main()
