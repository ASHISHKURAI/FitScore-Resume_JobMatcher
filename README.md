# 🎯 FitScore

**Know your match before you apply.**

FitScore is an AI-powered resume-to-job-description matcher. Upload your resume, paste a job description, and get an instant compatibility score — plus a breakdown of exactly which skills you have, which ones you're missing, and concrete suggestions to close the gap.

Built to solve a real problem: most resumes never make it past an ATS or a first skim, and job seekers rarely know *why*. FitScore makes that gap visible and actionable.

---

## ✨ What it does

- 📎 **Upload your resume** (PDF) and paste any job description
- 🧠 **Get a match score (0–100%)** computed from semantic similarity — not just keyword matching
- ✅ **See matching skills** — what's already working in your favor
- ❌ **See missing skills** — what the role wants that your resume doesn't show
- 💡 **Get actionable suggestions** — specific, not generic, on how to close the gap
- ⚡ **Instant results** — powered by a fast, free LLM backend (Groq + Llama 3.3)

---

## 🖼️ Preview

> *Add a screenshot or GIF of the app here once deployed — this is the first thing people look at.*

```
[ Screenshot: two-panel upload UI ]
[ Screenshot: match score + skill breakdown ]
```

---

## 🏗️ How it works

FitScore combines two different AI techniques, each doing what it's best at:

```
┌─────────────────┐         ┌──────────────────────┐
│   Resume (PDF)   │         │  Job Description(txt) │
└────────┬─────────┘         └──────────┬────────────┘
         │                              │
         ▼                              ▼
   ┌─────────────────────────────────────────┐
   │        Text Extraction (pdfplumber)       │
   └────────────────────┬──────────────────────┘
                         │
         ┌───────────────┴────────────────┐
         ▼                                 ▼
┌─────────────────────┐        ┌─────────────────────────┐
│  Embedding Model      │        │   LLM Reasoning Layer   │
│  (Sentence-Transform.)│        │   (Groq · Llama 3.3 70B)│
│                       │        │                          │
│  → Cosine similarity  │        │  → Matching skills       │
│  → Match Score (%)    │        │  → Missing skills        │
│                       │        │  → Suggestions           │
└──────────┬────────────┘        └────────────┬─────────────┘
           │                                    │
           └───────────────┬────────────────────┘
                            ▼
                 ┌─────────────────────┐
                 │   Streamlit UI       │
                 │   (results rendered) │
                 └─────────────────────┘
```

**Why two models instead of one?**
- **Embeddings (local, free)** are fast and great at *semantic similarity* — they answer "how close are these two documents in meaning?" without needing an API call.
- **An LLM (Groq)** is better at *structured reasoning* — pulling out specific skills, comparing them individually, and writing human-readable suggestions. Embeddings alone can't do this well; LLMs alone are slower and costlier for a raw similarity score.

Using both together gives a score you can trust *and* an explanation you can act on.

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend/UI | [Streamlit](https://streamlit.io) | Fast to build, easy to deploy, ideal for ML-driven apps |
| Embeddings | [Sentence-Transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`) | Runs locally, free, no API cost, fast inference |
| LLM Reasoning | [Groq API](https://groq.com) (Llama 3.3 70B) | Free tier, extremely low latency, strong reasoning |
| PDF Parsing | [pdfplumber](https://github.com/jsvine/pdfplumber) | Reliable text extraction from resume PDFs |
| Similarity Scoring | [scikit-learn](https://scikit-learn.org) (cosine similarity) | Standard, well-tested vector comparison |

**100% free to run** — no paid APIs, no cloud costs. Everything here fits inside free tiers.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+ 
- A free [Groq API key](https://console.groq.com)

### Installation

```bash
# Clone the repo
git clone https://github.com/ASHISHKURAI/Resume_JobDescriptionMatcher.git
cd Resume_JobDescriptionMatcher

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\Activate.ps1      # Windows PowerShell
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

> Get a free key at [console.groq.com](https://console.groq.com) — no credit card required.

### Run it

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser. Upload a resume, paste a job description, hit **Analyze Match**.

---

## 📁 Project Structure

```
Resume_JobDescriptionMatcher/
├── app.py              # Streamlit UI — layout, styling, user interaction
├── matcher.py           # Core logic — PDF parsing, embeddings, LLM calls
├── requirements.txt     # Python dependencies
├── .env                 # API key (not committed — see .gitignore)
├── .gitignore
└── README.md
```

---

## 🎯 Why this project

Most "resume checker" tools either:
- Rely purely on keyword-matching (misses genuine skill overlap phrased differently), or
- Give a vague score with no explanation of *why*

FitScore combines semantic understanding with structured LLM reasoning to give both a trustworthy number **and** a clear next step — closer to what a career coach would tell you, generated instantly.

This project was built to explore practical, end-to-end AI engineering: combining a local embedding model with an LLM API, designing prompts for reliable structured output (JSON mode), and shipping a usable, deployed tool — not just a notebook experiment.

---

## 🔮 Potential improvements

- [ ] Support DOCX resumes in addition to PDF
- [ ] Multi-resume comparison against a single JD
- [ ] Downloadable PDF report of the analysis
- [ ] Resume rewrite suggestions inline, not just gap list
- [ ] Support pasting a JD via URL

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙋 About

Built by [Ashish Kumar Rai](https://github.com/ASHISHKURAI) as a hands-on AI engineering project — combining embeddings, LLM reasoning, and a clean deployed UI to solve a real job-search problem.

Feedback, issues, and PRs welcome.
