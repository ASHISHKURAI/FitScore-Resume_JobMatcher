import pdfplumber
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
import os
import json
from llm_config import load_llm_config

model = SentenceTransformer('all-MiniLM-L6-v2')

llm_config = load_llm_config()
client_kwargs = {"api_key": llm_config.api_key}
if llm_config.base_url:
    client_kwargs["base_url"] = llm_config.base_url
client = OpenAI(**client_kwargs)


def extract_resume_text(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def get_match_score(resume_text, jd_text):
    embeddings = model.encode([resume_text, jd_text])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return round(float(score) * 100, 2)


def get_skill_gaps(resume_text, jd_text):
    prompt = f"""Compare this resume against this job description carefully.

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{jd_text[:3000]}

Return ONLY valid JSON (no markdown, no preamble, no explanation) in this exact structure:
{{
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "suggestions": ["specific actionable suggestion 1", "specific actionable suggestion 2"]
}}"""

    response = client.chat.completions.create(
        model=llm_config.model,
        max_tokens=llm_config.max_tokens,
        temperature=llm_config.temperature,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}]
    )

    raw_text = response.choices[0].message.content.strip()
    return json.loads(raw_text)


if __name__ == "__main__":
    jd = "We need a Python developer with FastAPI, Docker, and AWS experience."
    resume = "Experienced Python developer skilled in Flask, Docker, and Git."
    print("Match score:", get_match_score(resume, jd))
    print("Skill gaps:", get_skill_gaps(resume, jd))
