import html
import re
from datetime import datetime
from pathlib import Path

import streamlit as st
from matcher import (
    extract_resume_text, get_match_score, get_skill_gaps, create_pdf_report,
    get_verdict, get_skill_coverage,
)

MAX_RESUME_MB = 5  # keep in sync with server.maxUploadSize in .streamlit/config.toml
TONE_COLORS = {"good": "#22C55E", "ok": "#F59E0B", "low": "#EF4444"}

st.set_page_config(page_title="FitScore", page_icon="🎯", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.block-container { padding-top: 1.5rem; max-width: 1200px; }
header[data-testid="stHeader"] { background: transparent; }
[class^="fs-"], [class*=" fs-"] { font-family: 'Inter', sans-serif; }

/* Hero */
.fs-hero { text-align: center; padding: 2rem 1rem 2.2rem; }
.fs-badge {
    display: inline-block; padding: .35rem .95rem; border-radius: 999px;
    background: rgba(124, 58, 237, .15); border: 1px solid rgba(124, 58, 237, .45);
    color: #C4B5FD; font-size: .85rem; font-weight: 500;
}
.fs-title {
    font-size: 4.2rem; font-weight: 800; letter-spacing: -.03em; line-height: 1.1;
    margin: .9rem 0 .6rem;
    background: linear-gradient(135deg, #818CF8 0%, #C084FC 50%, #F472B6 100%);
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.fs-subtitle { color: #9CA3AF; font-size: 1.1rem; max-width: 640px; margin: 0 auto; line-height: 1.6; }
.fs-features { display: flex; gap: .6rem; justify-content: center; flex-wrap: wrap; margin-top: 1.4rem; }
.fs-features span {
    padding: .4rem .9rem; border-radius: 999px; background: #151A2D;
    border: 1px solid #262C44; color: #D1D5DB; font-size: .85rem;
}

/* Input cards */
.fs-step { display: flex; align-items: center; gap: .8rem; margin-bottom: .9rem; }
.fs-step-num {
    width: 34px; height: 34px; border-radius: 10px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; color: #fff; background: linear-gradient(135deg, #4F46E5, #7C3AED);
}
.fs-step-title { font-weight: 600; font-size: 1.05rem; color: #F3F4F6; }
.fs-step-sub { font-size: .82rem; color: #9CA3AF; }
.fs-file {
    display: flex; align-items: center; gap: .6rem; padding: .65rem .9rem; margin-top: .6rem;
    border-radius: 10px; background: rgba(34, 197, 94, .08);
    border: 1px solid rgba(34, 197, 94, .3); color: #BBF7D0; font-size: .9rem;
}
.fs-tips { margin-top: 1rem; color: #9CA3AF; font-size: .85rem; line-height: 1.8; }
.fs-tips b { color: #D1D5DB; }

/* Buttons */
button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    border: none; border-radius: 12px; padding: .75rem 2rem; font-weight: 600;
    box-shadow: 0 6px 20px rgba(79, 70, 229, .3); transition: all .2s ease;
}
button[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-2px); box-shadow: 0 10px 28px rgba(124, 58, 237, .45); color: #fff;
}
button[data-testid="stBaseButton-secondary"] { border-radius: 12px; padding: .75rem 1.2rem; }

/* Results */
.fs-section-title { font-size: 1.7rem; font-weight: 700; color: #F9FAFB; margin-top: .5rem; }
.fs-section-sub { color: #9CA3AF; font-size: .9rem; margin-bottom: 1.2rem; }
.fs-card { background: #151A2D; border: 1px solid #262C44; border-radius: 18px; padding: 1.5rem; }
.fs-card-title { font-weight: 600; font-size: 1.05rem; color: #F3F4F6; margin-bottom: 1rem; }
.fs-summary { display: grid; grid-template-columns: 280px 1fr; gap: 1rem; margin-bottom: 1rem; }
.fs-score-card { display: flex; align-items: center; justify-content: center; }
.fs-ring { position: relative; width: 190px; height: 190px; }
.fs-ring-label {
    position: absolute; inset: 0; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
}
.fs-ring-value { font-size: 2.7rem; font-weight: 800; color: #fff; line-height: 1; }
.fs-ring-caption {
    font-size: .75rem; color: #9CA3AF; text-transform: uppercase;
    letter-spacing: .1em; margin-top: .4rem;
}
.fs-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.fs-stat { background: #0F1424; border: 1px solid #262C44; border-radius: 14px; padding: 1.1rem; }
.fs-stat-value { font-size: 2rem; font-weight: 700; line-height: 1.1; }
.fs-stat-label { color: #9CA3AF; font-size: .85rem; margin-top: .3rem; }
.fs-verdict {
    margin-top: 1rem; padding: 1rem 1.2rem; border-radius: 14px; border: 1px solid;
    display: flex; align-items: center; gap: .9rem; color: #E5E7EB;
}
.fs-verdict b { display: block; font-size: 1.05rem; }
.fs-verdict span { color: #9CA3AF; font-size: .9rem; }
.fs-verdict-icon { font-size: 1.6rem; }
.fs-verdict.good { background: rgba(34, 197, 94, .08); border-color: rgba(34, 197, 94, .35); }
.fs-verdict.ok { background: rgba(245, 158, 11, .08); border-color: rgba(245, 158, 11, .35); }
.fs-verdict.low { background: rgba(239, 68, 68, .08); border-color: rgba(239, 68, 68, .35); }
.fs-skills { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.fs-chips { display: flex; flex-wrap: wrap; gap: .5rem; }
.fs-chip { padding: .4rem .85rem; border-radius: 999px; font-size: .88rem; font-weight: 500; }
.fs-chip.good { background: rgba(34, 197, 94, .12); color: #86EFAC; border: 1px solid rgba(34, 197, 94, .3); }
.fs-chip.bad { background: rgba(239, 68, 68, .12); color: #FCA5A5; border: 1px solid rgba(239, 68, 68, .3); }
.fs-empty { color: #6B7280; font-size: .9rem; }
.fs-suggestion {
    display: flex; gap: .9rem; align-items: flex-start; padding: 1rem 1.1rem; margin-bottom: .7rem;
    border-radius: 12px; background: #0F1424; border: 1px solid #262C44; color: #E5E7EB; line-height: 1.55;
}
.fs-suggestion-num {
    width: 28px; height: 28px; border-radius: 8px; flex-shrink: 0; font-size: .85rem;
    display: flex; align-items: center; justify-content: center;
    background: rgba(124, 58, 237, .2); color: #C4B5FD; font-weight: 700;
}
.fs-download-title { font-weight: 600; font-size: 1.05rem; color: #F3F4F6; }
.fs-download-sub { color: #9CA3AF; font-size: .88rem; margin-top: .2rem; }
.fs-footer { text-align: center; color: #6B7280; font-size: .85rem; padding: 2.5rem 0 1rem; }

@media (max-width: 760px) {
    .fs-title { font-size: 2.8rem; }
    .fs-summary, .fs-skills, .fs-stats { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)


def render(markup):
    # Strip indentation so Markdown doesn't turn indented HTML into code blocks
    lines = (line.strip() for line in markup.splitlines())
    st.markdown("\n".join(line for line in lines if line), unsafe_allow_html=True)


def chips(items, tone):
    if not items:
        return "<div class='fs-empty'>None identified</div>"
    return "<div class='fs-chips'>" + "".join(
        f"<span class='fs-chip {tone}'>{html.escape(str(item))}</span>" for item in items
    ) + "</div>"


def score_ring(score, color):
    radius = 78
    circumference = 2 * 3.14159 * radius
    filled = circumference * max(0, min(score, 100)) / 100
    return f"""
        <div class="fs-ring">
        <svg width="190" height="190" viewBox="0 0 190 190">
        <circle cx="95" cy="95" r="{radius}" stroke="rgba(255,255,255,0.08)" stroke-width="14" fill="none"/>
        <circle cx="95" cy="95" r="{radius}" stroke="{color}" stroke-width="14" fill="none"
        stroke-linecap="round" stroke-dasharray="{filled:.1f} {circumference:.1f}" transform="rotate(-90 95 95)"/>
        </svg>
        <div class="fs-ring-label">
        <div class="fs-ring-value">{score:.0f}%</div>
        <div class="fs-ring-caption">Match score</div>
        </div>
        </div>
    """


def reset():
    st.session_state.result = None
    st.session_state.uploader_key += 1
    st.session_state.jd_text = ""


if "result" not in st.session_state:
    st.session_state.result = None
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# ---------- Hero ----------
render("""
    <div class="fs-hero">
    <span class="fs-badge">✨ AI-powered resume analysis</span>
    <div class="fs-title">FitScore</div>
    <div class="fs-subtitle">Upload your resume, paste a job description, and see exactly how well you match &mdash; then download the full report as a PDF.</div>
    <div class="fs-features">
    <span>🧠 Semantic match score</span>
    <span>🧩 Skill gap analysis</span>
    <span>💡 Actionable suggestions</span>
    <span>📄 PDF report</span>
    </div>
    </div>
""")

# ---------- Inputs ----------
left, right = st.columns(2, gap="large")

with left:
    with st.container(border=True):
        render(f"""
            <div class="fs-step"><div class="fs-step-num">1</div><div>
            <div class="fs-step-title">Upload your resume</div>
            <div class="fs-step-sub">PDF only · max {MAX_RESUME_MB} MB</div>
            </div></div>
        """)
        resume_file = st.file_uploader(
            "Resume PDF", type="pdf", label_visibility="collapsed",
            key=f"resume_{st.session_state.uploader_key}",
        )
        resume_too_big = bool(resume_file) and resume_file.size > MAX_RESUME_MB * 1024 * 1024
        if resume_file and resume_too_big:
            st.error(f"This file is {resume_file.size / 1024 / 1024:.1f} MB. Please upload a resume under {MAX_RESUME_MB} MB.")
        elif resume_file:
            render(f"""
                <div class="fs-file">📄 <b>{html.escape(resume_file.name)}</b>
                <span style="margin-left:auto; opacity:.8;">{resume_file.size / 1024:.0f} KB</span></div>
            """)
        render("""
            <div class="fs-tips">
            <b>Tips for best results</b><br>
            • Use a text-based PDF (not a scanned image)<br>
            • Paste the complete JD, including requirements<br>
            • Your data is never stored
            </div>
        """)

with right:
    with st.container(border=True):
        render("""
            <div class="fs-step"><div class="fs-step-num">2</div><div>
            <div class="fs-step-title">Paste the job description</div>
            <div class="fs-step-sub">The more complete it is, the better the analysis</div>
            </div></div>
        """)
        jd_text = st.text_area(
            "Job description", key="jd_text", height=230, label_visibility="collapsed",
            placeholder="Paste the full job description here...",
        )
        st.caption(f"{len(jd_text.split())} words")

st.write("")
_, btn_col, _ = st.columns([1, 1, 1])
with btn_col:
    analyze_clicked = st.button("🔍 Analyze Match", type="primary", width="stretch")

if analyze_clicked:
    if not resume_file or not jd_text.strip():
        st.warning("Please upload a resume and paste a job description.")
    elif resume_too_big:
        st.error(f"Your resume must be under {MAX_RESUME_MB} MB.")
    else:
        with st.spinner("Analyzing your resume against the job description..."):
            try:
                resume_text = extract_resume_text(resume_file)
                if not resume_text:
                    st.error("Couldn't read any text from this PDF. If it's a scanned image, export it as a text-based PDF and try again.")
                    st.stop()
                score = get_match_score(resume_text, jd_text)
                gaps = get_skill_gaps(resume_text, jd_text)
            except Exception as e:
                st.error(f"Something went wrong during the analysis: {e}")
                st.stop()

        analyzed_at = datetime.now()
        # Stored in session state so results survive reruns (e.g. clicking Download)
        st.session_state.result = {
            "score": score,
            "gaps": gaps,
            "resume_name": resume_file.name,
            "analyzed_at": analyzed_at,
            "pdf": create_pdf_report(score, gaps, resume_file.name, jd_text, analyzed_at),
        }

# ---------- Results ----------
result = st.session_state.result
if result:
    score, gaps = result["score"], result["gaps"]
    tone, label, message = get_verdict(score)
    color = TONE_COLORS[tone]
    icon = {"good": "🎉", "ok": "👍", "low": "⚠️"}[tone]

    st.divider()
    render(f"""
        <div class="fs-section-title">Your results</div>
        <div class="fs-section-sub">{html.escape(result["resume_name"])} · analyzed {result["analyzed_at"]:%d %b %Y, %I:%M %p}</div>
    """)

    render(f"""
        <div class="fs-summary">
        <div class="fs-card fs-score-card">{score_ring(score, color)}</div>
        <div class="fs-card">
        <div class="fs-stats">
        <div class="fs-stat"><div class="fs-stat-value" style="color:#22C55E">{len(gaps["matching_skills"])}</div><div class="fs-stat-label">Matching skills</div></div>
        <div class="fs-stat"><div class="fs-stat-value" style="color:#EF4444">{len(gaps["missing_skills"])}</div><div class="fs-stat-label">Missing skills</div></div>
        <div class="fs-stat"><div class="fs-stat-value" style="color:#A78BFA">{get_skill_coverage(gaps)}%</div><div class="fs-stat-label">Skill coverage</div></div>
        </div>
        <div class="fs-verdict {tone}"><div class="fs-verdict-icon">{icon}</div>
        <div><b>{label}</b><span>{message}</span></div></div>
        </div>
        </div>
    """)

    render(f"""
        <div class="fs-skills">
        <div class="fs-card"><div class="fs-card-title">✅ Matching skills</div>{chips(gaps["matching_skills"], "good")}</div>
        <div class="fs-card"><div class="fs-card-title">❌ Missing skills</div>{chips(gaps["missing_skills"], "bad")}</div>
        </div>
    """)

    suggestions = "".join(
        f"<div class='fs-suggestion'><div class='fs-suggestion-num'>{i}</div><div>{html.escape(str(s))}</div></div>"
        for i, s in enumerate(gaps["suggestions"], 1)
    ) or "<div class='fs-empty'>No suggestions returned.</div>"
    render(f"""
        <div class="fs-card" style="margin-bottom:1rem;">
        <div class="fs-card-title">💡 Suggestions to improve your match</div>
        {suggestions}
        </div>
    """)

    with st.container(border=True):
        text_col, download_col, reset_col = st.columns([3, 1.4, 1.1], vertical_alignment="center")
        with text_col:
            render("""
                <div class="fs-download-title">📄 Save this analysis</div>
                <div class="fs-download-sub">Download a PDF with your score, skills, suggestions and the job description, so you can review it later.</div>
            """)
        with download_col:
            stem = re.sub(r"[^A-Za-z0-9_-]+", "_", Path(result["resume_name"]).stem)[:40]
            st.download_button(
                "⬇️ Download PDF",
                data=result["pdf"],
                file_name=f"FitScore_{stem}_{result['analyzed_at']:%Y%m%d_%H%M}.pdf",
                mime="application/pdf",
                type="primary",
                width="stretch",
                on_click="ignore",
            )
        with reset_col:
            st.button("↺ New analysis", on_click=reset, width="stretch")

render("""
    <div class="fs-footer">FitScore · Built with Streamlit, Groq and Sentence Transformers · Your data isn't stored anywhere.</div>
""")
