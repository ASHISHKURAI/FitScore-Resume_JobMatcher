# PDF Report Architecture for FitScore

This document outlines the planned architecture for adding a downloadable PDF report after the user uploads a resume, pastes a job description, and clicks Analyze.

Important: this is a design-only document. No production code is implemented here yet.

---

## 1. Goal

When the user analyzes a resume against a job description, the app should:

- show the overall match score
- highlight matching skills
- highlight missing skills
- provide improvement suggestions
- allow the user to download a polished PDF summary
- include a clear explanation of what skills are missing and how to improve them

The PDF must feel like a professional report, not just a raw list of text.

---

## 2. High-Level Flow

```text
User uploads resume PDF
        │
        ▼
Resume text extraction
        │
        ▼
Semantic similarity scoring
        │
        ▼
Skill comparison via LLM
        │
        ▼
Structured result object created
        │
        ▼
UI renders score + insights
        │
        ▼
User clicks "Download PDF"
        │
        ▼
PDF builder generates report
        │
        ▼
Browser downloads file
```

---

## 3. Proposed System Architecture

### 3.1 Frontend Layer

Responsible for:

- resume file upload
- job description input
- analyze button
- rendering the match result in Streamlit
- showing the PDF download button

Current UI responsibility:

- `app.py` handles user interactions
- it should also trigger the PDF generation request after analysis

Planned UI state:

```python
st.session_state = {
    "resume_text": "...",
    "job_description": "...",
    "match_score": 82,
    "matching_skills": [...],
    "missing_skills": [...],
    "suggestions": [...],
    "report_ready": True,
    "report_bytes": b"..."
}
```

This keeps the UI clean and allows the PDF to be generated from the same result object used by the screen.

### 3.2 Analysis Layer

Responsible for:

- extracting text from the uploaded resume PDF
- computing the overall semantic match score
- extracting and comparing skills between resume and JD
- returning structured JSON for rendering and PDF export

This layer should remain separate from the report layer so the same analysis can power both UI and PDF output.

Suggested functions:

```python
extract_resume_text(file) -> str
calculate_match_score(resume_text, jd_text) -> float
compare_skills(resume_text, jd_text) -> dict
build_analysis_result(resume_text, jd_text) -> AnalysisResult
```

### 3.3 Report Generation Layer

Responsible for:

- formatting the analysis into a document layout
- converting the structured result into a PDF document
- creating a professional summary with sections like:
  - headline summary
  - match score
  - matched skills
  - missing skills
  - improvement guidance
  - summary next steps

Recommended separation:

```python
create_pdf_report(analysis_result) -> bytes
```

This function should not contain business logic like scoring or JD parsing. It should only format already-computed results.

### 3.4 Data Model Layer

A clean result object is important so both the UI and PDF generator share the same standard structure.

Proposed dictionary or dataclass:

```python
AnalysisResult = {
    "match_score": 82.5,
    "matching_skills": ["Python", "SQL", "Machine Learning"],
    "missing_skills": ["Kafka", "AWS", "Docker"],
    "suggestions": [
        "Add Docker deployment experience to your resume.",
        "Mention cloud-native projects using AWS services."
    ],
    "summary": "Strong technical alignment with a few missing cloud and deployment skills.",
    "coverage_breakdown": {
        "matched_count": 3,
        "missing_count": 3,
        "total_required_skills": 6
    }
}
```

This structure gives enough information for both:

- the interactive UI cards
- the PDF report layout

---

## 4. Architectural Components

### 4.1 Resume Input Module

Purpose:

- accept PDF upload
- extract text reliably
- validate file type

Responsibilities:

- check if file is PDF
- extract text pages
- normalize whitespace and formatting
- return clean resume text

### 4.2 JD Input Module

Purpose:

- accept user-pasted text
- sanitize text input
- pass it to analysis logic

Responsibilities:

- trim extra whitespace
- handle empty or invalid input
- allow future integration with external JD parsing

### 4.3 Matching Engine

Purpose:

- compute similarity between resume and JD

Responsibilities:

- embeddings-based semantic comparison
- match score rounding and presentation
- future ability to swap scoring models without disrupting UI

### 4.4 Skill Comparator

Purpose:

- identify overlap and gaps

Responsibilities:

- compare resume skills with JD skills
- classify skills into matched vs missing
- generate improvement recommendations

This should be a structured output layer, not a free-form text dump.

### 4.5 PDF Report Builder

Purpose:

- produce final downloadable report in PDF format

Responsibilities:

- page layout design
- headline title and branding
- score card
- sections for matching and missing skills
- summary and recommendations
- footer metadata

This should be its own module for easier future maintenance and design changes.

---

## 5. Recommended Module Layout

A clean folder layout for the next stage would look like this:

```text
Resume_JobDescriptionMatcher/
├── app.py
├── matcher.py
├── services/
│   ├── resume_parser.py
│   ├── skill_matcher.py
│   ├── report_builder.py
│   └── pdf_generator.py
├── models/
│   └── analysis_result.py
├── utils/
│   ├── text_cleaner.py
│   └── formatting.py
├── ARCHITECTURE.md
├── README.md
└── requirements.txt
```

This keeps the responsibilities isolated and makes the PDF export easy to extend later.

---

## 6. PDF Report Layout Design

The generated PDF should be designed with a simple, professional structure:

### Page 1

1. Header: FitScore
2. Subtitle: Resume Job Match Report
3. Score card with large percentage value
4. Short summary paragraph
5. Section: Matching Skills
6. Section: Missing Skills
7. Section: Improvement Suggestions
8. Footer: generated timestamp and app name

### Optional Page 2

- more detailed recommendations
- skills grouped by category
- action plan for resume expansion

This layout is useful if the report becomes long or if the user wants a more polished document.

---

## 7. PDF Content Structure

The PDF should present information in this order:

```text
FitScore Report
│
├── Overall Match Score
├── Resume-to-JD Summary
├── Matching Skills
│   ├── Skill 1
│   ├── Skill 2
│   └── Skill 3
├── Missing Skills
│   ├── Skill A
│   ├── Skill B
│   └── Skill C
├── How to Improve
│   ├── Suggestion 1
│   ├── Suggestion 2
│   └── Suggestion 3
└── Final Advice
```

This progression helps the user understand:

- where they already fit
- where they are weak
- what to do next

---

## 8. Report Generation Pipeline

```text
AnalysisResult
    │
    ▼
PDFBuilder
    │
    ├── Build title + summary
    ├── Add score card
    ├── Add matching skills section
    ├── Add missing skills section
    ├── Add improvement suggestions
    ├── Add summary and final advice
    └── Export as PDF bytes
```

Key idea:

- analysis is done once
- same result is reused for UI and PDF
- no duplicate logic

---

## 9. Data Flow and Separation of Concerns

### Analysis vs Report

The analysis layer answers:

- What skills match?
- What skills are missing?
- How strong is the overall alignment?

The PDF layer answers:

- How should this information be displayed in a formal document?

This separation is important because it keeps the code clean and prevents UI formatting logic from mixing with the AI analysis logic.

---

## 10. Future Extension Points

This architecture supports future upgrades without rewriting the whole app:

- support DOCX resumes
- compare multiple resumes against one JD
- show a detailed skill-by-skill matrix
- generate a downloadable ATS-friendly version
- add resume rewrite recommendations
- export not only PDF but also HTML/JSON summary

---

## 11. Recommended Design Principles

1. Keep AI analysis and PDF generation as separate modules.
2. Use a shared result object for all outputs.
3. Make the PDF builder rely only on structured data, not raw resume text.
4. Keep the PDF layout simple and readable.
5. Use consistent naming for skills, scores, and suggestions.
6. Prioritize a clean user experience before visual complexity.

---

## 12. Suggested Next Implementation Step

The next implementation stage should be:

1. define a single `AnalysisResult` schema
2. create a `report_builder.py` or `pdf_generator.py` module
3. generate PDF bytes from a structured object
4. add a `Download PDF` button to the Streamlit UI
5. verify the report includes the match score, missing skills, and suggestions

---

## 13. Success Criteria

The report feature is considered successful when:

- user can click Analyze and immediately get a score
- same result is reused for UI and PDF output
- PDF contains matching skills, missing skills, and improvement advice
- the report is downloadable with one click
- the document is readable and professional in appearance

---

## 14. Final Architecture Summary

The right architecture for this app is a three-layer design:

- Input and analysis layer
- result model layer
- PDF report generation layer

This structure is simple, maintainable, and scalable. It keeps the mathematics and AI logic separate from presentation, which is exactly what you want for a tool like FitScore.

If needed later, we can extend this design into a concrete class-and-function blueprint for the actual implementation.
