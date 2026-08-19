import streamlit as st
from matcher import extract_resume_text, get_match_score, get_skill_gaps

st.set_page_config(page_title="FitScore", page_icon="🎯", layout="wide")
# ---- Custom styling ----
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
    }
    .score-box {
        text-align: center;
        padding: 2rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(79, 70, 229, 0.3);
    }
    .score-box h2 {
        color: #E0E7FF;
        font-weight: 500;
        letter-spacing: 1px;
    }
    .score-box h1 {
        color: #FFFFFF;
        font-weight: 800;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25);
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Header ----
st.markdown("<div class='main-header'><h1>🎯 FitScore</h1><p>See how well your resume matches a job description, instantly.</p></div>", unsafe_allow_html=True)

# ---- Session state to hold results across reruns ----
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False

# ---- Two-panel input layout ----
left, right = st.columns(2)

with left:
    st.subheader("📎 Your Resume")
    resume_file = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed")

with right:
    st.subheader("📋 Job Description")
    jd_text = st.text_area("Paste JD", height=280, label_visibility="collapsed",
                            placeholder="Paste the full job description here...")

st.write("")  # spacing

# ---- Centered analyze button ----
btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
with btn_col2:
    analyze_clicked = st.button("🔍 Analyze Match", type="primary", use_container_width=True)

# ---- Results ----
if analyze_clicked:
    if not resume_file or not jd_text.strip():
        st.warning("Please upload a resume and paste a job description.")
    else:
        with st.spinner("Analyzing your resume against the job description..."):
            resume_text = extract_resume_text(resume_file)
            score = get_match_score(resume_text, jd_text)
            gaps = get_skill_gaps(resume_text, jd_text)

        st.divider()

        st.markdown(f"""
            <div class='score-box'>
                <h2 style='margin:0;'>Match Score</h2>
                <h1 style='font-size:3.5rem; margin:0;'>{score}%</h1>
            </div>
        """, unsafe_allow_html=True)

        if score >= 75:
            st.success("Strong match! You're well-aligned with this role.")
        elif score >= 50:
            st.info("Decent match — a few tweaks could strengthen your application.")
        else:
            st.warning("Low match — consider whether this role fits your current skillset, or update your resume.")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✅ Matching Skills")
            for skill in gaps["matching_skills"]:
                st.write(f"- {skill}")
        with col2:
            st.subheader("❌ Missing Skills")
            for skill in gaps["missing_skills"]:
                st.write(f"- {skill}")

        st.subheader("💡 Suggestions to Improve Your Match")
        for suggestion in gaps["suggestions"]:
            st.write(f"- {suggestion}")

# ---- Footer ----
st.divider()
st.caption("Built with Streamlit + an OpenAI-compatible LLM provider + Sentence Transformers. Your data isn't stored anywhere.")
