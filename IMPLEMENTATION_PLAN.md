# Future Implementation Plan

This document tracks deferred improvements for the FitScore application.

## 1. Optimize Sentence Transformer Loading

Status: Planned

### Objective

Ensure the Sentence Transformer model is loaded once per Streamlit process and reused across Streamlit reruns.

### Implementation steps

1. Add a cached model-loading function using `st.cache_resource`.
2. Move model initialization out of the module-level statement in `matcher.py`.
3. Keep the model on the available device automatically:
   - Use GPU when CUDA is available.
   - Use CPU when no GPU is available.
4. Confirm that the model is not reloaded when users interact with widgets or click the Analyze button.
5. Confirm that the model reloads when the Streamlit process is intentionally restarted.

### Verification

- Start the application with `streamlit run app.py`.
- Confirm the model loads during startup.
- Interact with the application multiple times.
- Confirm the model-loading message appears only once during that process.
- Restart Streamlit and confirm the model loads once again.

## 2. Add Hugging Face Authentication

Status: Planned

### Objective

Authenticate Hugging Face Hub requests to improve download rate limits and reliability when downloading models.

### Implementation steps

1. Create a Hugging Face User Access Token with read-only permissions.
2. Do not grant write, organization administration, or repository-management permissions.
3. Add the token locally to `.env`:

   ```env
   HF_TOKEN=hf_your_token_here
   ```

4. Confirm `.env` remains excluded by `.gitignore`.
5. Add `HF_TOKEN` as a documented placeholder in `.env.example`.
6. Ensure the application loads the token through `python-dotenv`.
7. Restart Streamlit and verify that the unauthenticated Hugging Face warning no longer appears.

### Verification

- Confirm the token is never printed in application logs.
- Confirm the token is not present in tracked files.
- Confirm the Sentence Transformer model still loads successfully.
- Confirm the application continues to work when the token is absent, unless authenticated access becomes necessary.

## Change Tracking

| Task | Status |
|---|---|
| Sentence Transformer loading optimization | Planned |
| Hugging Face token authentication | Planned |
