# Chapter 7 — Glossary & Revision Notes

> **How to use this chapter:** Use the glossary to look up any word quickly. Use
> the one-page revision sheet the night before your viva. Finish with the
> self-assessment checklist — if you can tick every box, you are ready.

---

## 7.1 Glossary (plain definitions + project example)

| Term | Simple meaning | In this project |
|------|----------------|-----------------|
| **Module** | A Python file you can import. | `analyzer.py`, `sample_data.py`. |
| **Import** | Borrow code from another file. | `from sample_data import SKILL_DATABASE`. |
| **Function** | Named block of code with inputs/output. | `preprocess_text(text)`. |
| **Parameter / argument** | Input to a function. | `text` in `preprocess_text`. |
| **Default parameter** | Optional input with a preset value. | `skill_database=SKILL_DATABASE`. |
| **Return value** | What a function hands back. | `analyze_resume` returns the results dict. |
| **String** | Text data. | the resume and job text. |
| **Triple-quoted string** | A multi-line string in `""" """`. | each sample resume. |
| **List** | Ordered collection, allows duplicates. | a category's skills. |
| **Dictionary** | `key: value` pairs. | `SKILL_DATABASE`, the results dict. |
| **Dictionary of lists** | Dict whose values are lists. | `SKILL_DATABASE`. |
| **Set** | Unordered, unique collection. | resume skills, job skills. |
| **Intersection** | Items in both sets. | matched skills. |
| **Difference** | Items in one set but not the other. | missing skills (`job − resume`). |
| **Comprehension** | One-line loop to build a list/dict. | counting non-empty lines. |
| **f-string** | Text with `{variables}` inside. | report/message lines. |
| **Truthiness** | Empty values act as `False`. | `if not text`. |
| **Regular expression (regex)** | Pattern language for text. | finding emails, skills. |
| **`re`** | Python's regex module. | used across `analyzer.py`. |
| **Word boundary `\b`** | The edge of a word. | matching `r` safely. |
| **Look-around** | "(not) followed/preceded by X". | matching `c++`. |
| **Compile / cache (regex)** | Build a pattern once, reuse it. | `_skill_pattern_cache`. |
| **Exception** | A runtime error. | bad file upload. |
| **try/except** | Catch an error and continue. | file reading, batch. |
| **raise** | Deliberately signal an error. | `raise ValueError(...)`. |
| **Bytes** | Raw file data (not yet text). | uploaded file contents. |
| **Decode** | Turn bytes into text. | `.decode("utf-8")`. |
| **Class** | A blueprint for objects. | `unittest.TestCase`, `FPDF`. |
| **unittest** | Python's built-in testing tool. | `tests/test_analyzer.py`. |
| **assertion** | A test's pass/fail check. | `assertEqual`, `assertTrue`. |
| **Streamlit** | Python → web page framework. | all of `app.py`. |
| **Widget** | A UI control (button, text box). | `st.button`, `st.text_area`. |
| **Rerun** | Streamlit re-runs the script on each action. | why `session_state` is needed. |
| **session_state** | Streamlit's memory across reruns. | stores resume text + results. |
| **Callback** | Function run when a widget changes. | `_load_sample_resume`. |
| **DataFrame** | A pandas table. | skill-gap / batch tables. |
| **CSV** | Comma-separated values file. | table downloads. |
| **Plotly figure** | An interactive chart object. | gauges, bar charts. |
| **ATS** | Applicant Tracking System (recruiter software). | what we *cannot* guarantee. |
| **OCR** | Reading text from images. | needed for scanned PDFs (out of scope). |
| **Heuristic** | A rule-of-thumb, not a guarantee. | quality checks, scores. |
| **Virtual environment (venv)** | Per-project package box. | created during setup. |
| **pip** | Python's package installer. | installs requirements. |

---

## 7.2 One-page revision sheet

**Project:** ResumeIQ — Smart Resume Analyzer (Python + Streamlit).
**Goal:** compare a resume to a job description; report match %, missing skills,
tips. **Rule-based, offline, no AI, no database, no secrets.**

**Three layers:**
- `app.py` → UI (Streamlit): pages, inputs, charts, downloads.
- `analyzer.py` → engine: cleaning, matching, scoring, reports.
- `sample_data.py` → data: `SKILL_DATABASE` + 5 resumes + 5 jobs (embedded).

**Core maths (memorise):**
```
matched = resume_skills ∩ job_skills
missing = job_skills − resume_skills
match % = matched / total_job_skills × 100   (0 if no job skills)
readiness = 0.6×keywords + 0.2×sections + 0.1×contact + 0.1×readability  (0–100)
```

**Matching trick:** `\b` for normal skills (`r` ≠ `react`); look-arounds for
`c++`, `c#`, `.net`, `node.js`, `ci/cd`.

**Conductor:** `analyze_resume()` runs everything and returns one dict.

**Tested:** 31 unittest cases → `Ran 31 tests ... OK` (Python 3.14.6).

**Run:** `streamlit run app.py` · **Test:** `python -m unittest discover -s tests`.

**Honest limits:** keywords not meaning; no proficiency judgement; no ATS
guarantee; no OCR.

---

## 7.3 The 20 most important things to remember

1. It matches **keywords**, it does **not understand meaning**.
2. "Embedded strings" = text in the code, **not** AI embeddings.
3. Three layers: UI (`app.py`), logic (`analyzer.py`), data (`sample_data.py`).
4. `SKILL_DATABASE` is a **dictionary of lists**, all lowercase.
5. Matching uses **sets**: intersection = matched, difference = missing.
6. Match % = matched ÷ total job skills × 100.
7. The `if total > 0` check prevents **divide-by-zero**.
8. Readiness weights (60/20/10/10) **sum to 100** and the total is **clamped**.
9. `\b` makes `r` match only as a whole word.
10. `c++`/`c#`/`.net`/`node.js` need **look-arounds**, not `\b`.
11. `preprocess_text` keeps `+ # . / -` to protect tech names.
12. `analyze_resume()` is the single conductor reused everywhere.
13. `app.py` is the entry point; `streamlit run app.py` starts it.
14. Streamlit **reruns** the script on every action; `session_state` remembers.
15. The uploaded-text bug was caused by `value=` + `key=` on a widget.
16. Files (`pdf/docx/txt`) are read by pypdf / python-docx / direct decode.
17. Scanned PDFs have no text → handled with a clear error (no OCR).
18. 31 unittest cases verify the engine; they don't need the web page.
19. No database, no API keys, no secrets — nothing to leak or configure.
20. It never guesses sensitive attributes and keeps a human in the loop.

---

## 7.4 Important files and their responsibilities

| File | Responsibility |
|------|----------------|
| `app.py` | Streamlit UI: pages, inputs, validation, charts, downloads. |
| `analyzer.py` | Engine: preprocessing, matching, scoring, reports. |
| `sample_data.py` | Embedded data: skills, sample resumes, sample jobs. |
| `tests/test_analyzer.py` | 31 automated tests for the engine. |
| `requirements.txt` | The 6 packages to install. |
| `README.md` | Beginner install & run guide. |
| `PROJECT_REPORT.md` | Formal academic report. |

---

## 7.5 Most important functions and their purpose

| Function (in `analyzer.py`) | Purpose |
|-----------------------------|---------|
| `preprocess_text(text)` | Clean + lowercase text, keep tech symbols. |
| `_build_skill_pattern(skill)` | Build/cache a safe regex per skill. |
| `extract_skills(text, db)` | Find skills by category in text. |
| `flatten_skills(...)` | Merge category lists into one set. |
| `count_resume_statistics(text)` | Words, chars, lines, sentences, avg length. |
| `detect_contact_information(text)` | Find email/phone/LinkedIn/GitHub/portfolio. |
| `detect_resume_sections(text)` | Detect sections (with alternate headings). |
| `calculate_keyword_match(r, j)` | Set maths → matched/missing/extra/match %. |
| `calculate_readiness_score(...)` | Weighted 0–100 score with breakdown. |
| `analyze_skill_gaps(r, j)` | Per-skill table with honest recommendations. |
| `generate_resume_strengths(a)` | Evidence-backed positives. |
| `generate_improvement_suggestions(a)` | Rule-based, honest tips. |
| `analyze_resume(...)` | Conductor: runs all steps, returns one dict. |
| `compare_resumes(...)` | Two resumes vs one job, side by side. |
| `analyze_multiple_resumes(...)` | Batch screening, robust to bad files. |
| `extract_text_from_file(f)` | Read `.txt/.pdf/.docx` into text. |
| `create_analysis_report(a)` | Markdown report string. |
| `create_analysis_pdf(a)` | PDF report bytes (fpdf2). |

---

## 7.6 Execution flow in one line

```
streamlit run app.py → choose page → input resume+job → Analyze →
analyze_resume() → {preprocess → extract_skills → set match → readiness →
strengths/suggestions} → render_dashboard() → metrics/charts/tabs → download PDF/CSV
```

---

## 7.7 Common viva mistakes to avoid

- ❌ Saying "it uses AI/ML". ✅ It is **rule-based**; no ML.
- ❌ Confusing embedded strings with AI embeddings.
- ❌ Saying it "understands" the resume. ✅ It matches keywords.
- ❌ Forgetting the divide-by-zero guard when asked about empty inputs.
- ❌ Claiming it guarantees ATS success. ✅ It's a heuristic indicator.
- ❌ Saying `\b` handles `c++` (it doesn't — look-arounds do).
- ❌ Not being able to compute a match % by hand. Practise it!
- ❌ Saying the tests need the web page. ✅ They test `analyzer.py` directly.

---

## 7.8 Final self-assessment checklist

- [ ] I can explain the project in 30 seconds, 2 minutes, and 5 minutes.
- [ ] I can draw the three-layer architecture.
- [ ] I can compute matched/missing/match % from two small sets.
- [ ] I can compute a readiness score from the four components.
- [ ] I can explain `\b` vs look-arounds with the `r` and `c++` examples.
- [ ] I can name what `analyze_resume()` returns.
- [ ] I can run the app and the tests, and read the results.
- [ ] I can state three honest limitations.
- [ ] I can explain the Streamlit rerun / session_state idea and the bug it fixed.
- [ ] I can answer any question in Chapter 6 in my own words.

**If every box is ticked, you are ready for your viva. Good luck! 🎓**
