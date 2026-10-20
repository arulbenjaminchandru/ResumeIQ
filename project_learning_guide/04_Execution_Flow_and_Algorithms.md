# Chapter 4 — Execution Flow & Algorithms

> **How to read this chapter:** First we follow the program from the moment you
> run it, step by step. Then we zoom into the four most important algorithms and
> work through them with real numbers. Diagrams are plain text so they print
> cleanly.

---

## 4.1 How the program starts (startup sequence)

1. You type **`streamlit run app.py`** in the terminal.
2. Streamlit starts a small local web server and **runs `app.py` top to
   bottom**.
3. As `app.py` loads, its `import analyzer` line runs `analyzer.py`, whose
   `from sample_data import SKILL_DATABASE` line runs `sample_data.py`. So all
   three files are now loaded into memory.
4. `st.set_page_config(...)` sets the page title/layout (this must be the first
   Streamlit command).
5. The sidebar is drawn: `selection = st.sidebar.radio("Navigate", ...)`.
6. `PAGES[selection]()` calls the function for the chosen page (default:
   **Home**).
7. Your browser opens at `http://localhost:8501` and shows the page.

**Key Streamlit idea again:** every click or text change makes Streamlit **re-run
`app.py` from the top**. Values that must survive a rerun live in
`st.session_state`.

---

## 4.2 What happens when you click "Analyze" (end-to-end trace)

Imagine you loaded the **Python Developer** sample and clicked **🔍 Analyze**.

```
USER clicks "Analyze"
      │
      ▼
app.py: page_analyze()
      │  reads resume text from st.session_state["resume_area"]
      │  reads job text   from st.session_state["job_area"]
      │  VALIDATION: if either is empty -> show st.error() and STOP
      ▼
app.py calls analyzer.analyze_resume(resume_text, job_text, job_title)
      │
      ▼
analyzer.analyze_resume()  (the conductor)
      ├─ count_resume_statistics(resume_text)      -> words, lines, ...
      ├─ detect_contact_information(resume_text)   -> email/phone/...
      ├─ detect_resume_sections(resume_text)       -> which sections
      ├─ detect_experience_education(resume_text)  -> approx signals
      ├─ extract_skills(resume_text)   -- each calls preprocess_text()
      ├─ extract_skills(job_text)      -- then _build_skill_pattern() per skill
      ├─ calculate_keyword_match(resume_text, job_text)
      │        └ set intersection / difference  -> matched / missing / match %
      ├─ analyze_skill_gaps(resume_skills, job_skills)
      ├─ calculate_readiness_score(...)            -> weighted 0..100
      ├─ resume_quality_checks(...)
      ├─ generate_resume_strengths(analysis)
      └─ generate_improvement_suggestions(analysis)
      │
      ▼  returns ONE big dictionary `analysis`
app.py stores it in st.session_state["analysis"]
      │
      ▼
app.py: render_dashboard(analysis)
      ├─ st.metric() x4  (Match %, Readiness, Matched, Missing)
      └─ st.tabs([...])  (Overview, Skills, Skill Gap, Quality,
                          Strengths, Raw vs Clean, Report)
      │
      ▼
USER sees numbers, tables, charts; can download PDF / CSV
```

**Error path:** if a step inside the engine raised an error it would bubble up;
for file uploads and batch screening the code deliberately catches errors with
`try/except` and shows a friendly message instead of crashing.

---

## 4.3 What each major button does

| Where | Button | What happens in the code |
|-------|--------|--------------------------|
| Analyze page | **Load this sample resume** | callback `_load_sample_resume()` writes the chosen sample into `session_state["resume_area"]`. |
| Analyze page | **Load resume + job for this role** | callback `_load_role_demo()` fills both boxes from `ROLE_SAMPLES`. |
| Analyze page | **🚀 Analyze** | validates inputs, calls `analyze_resume()`, renders the dashboard. |
| Analyze page | **♻️ Clear / Reset** | callback `_reset_all()` empties the boxes and the stored analysis. |
| Report tab | **Download PDF** | `analyzer.create_analysis_pdf(analysis)` returns bytes to `st.download_button`. |
| Skill Gap tab | **Download CSV** | pandas `DataFrame.to_csv(...)` feeds `st.download_button`. |
| Compare page | **Compare** | `analyzer.compare_resumes(a, b, jd)` → table + bar chart. |
| Batch page | **Screen resumes** | extracts each file's text, calls `analyze_multiple_resumes(...)`, shows a sorted table + CSV. |

---

## 4.4 Algorithm 1 — Text preprocessing

**What it does:** turns messy raw text into clean, lowercase, single-spaced text
while protecting tech symbols.

**Pseudocode:**
```
function preprocess_text(text):
    if text is empty or not a string: return ""
    text = lowercase(text)
    replace every char that is NOT [a-z 0-9 space + # . / -] with a space
    collapse multiple spaces into one; trim the ends
    return text
```

**Worked example:**
```
Input : "C++, Python!!!   Node.js\n\nSQL"
step 1 : already handled (string)
step 2 : "c++, python!!!   node.js\n\nsql"
step 3 : "c++  python     node.js  sql"   (commas, ! -> spaces; + # . / - kept)
step 4 : "c++ python node.js sql"
Output : "c++ python node.js sql"
```

**Complexity:** O(n) in the length of the text (each character is processed a
constant number of times). **Edge cases handled:** empty input, non-string
input, text with lots of punctuation or blank lines.

---

## 4.5 Algorithm 2 — Safe skill matching (the regex trick)

**Problem:** we must match a skill as a whole token. Two traps:
- `r` must match the language *R*, but not the `r` in `react`.
- `c++` must match `c++`, but `\b` (word boundary) does not work because `+` is
  not a word character.

**Pseudocode:**
```
function build_pattern(skill):
    if skill contains any of + # . / - :
        boundary = one of [a-z 0-9 + #]
        pattern  = (not boundary) + skill + (not boundary)   # look-arounds
    else:
        pattern  = \b + skill + \b                            # word boundaries
    return compiled, case-insensitive pattern
```

**Why it works:**

| Text | Skill | Pattern used | Match? | Reason |
|------|-------|--------------|--------|--------|
| `python, r, sql` | `r` | `\br\b` | ✅ yes | `r` has spaces/commas around it = boundaries |
| `react` | `r` | `\br\b` | ❌ no | `r` touches `e`, so no boundary after it |
| `c++ developer` | `c++` | `(?<![a-z0-9+#])c\+\+(?![a-z0-9+#])` | ✅ yes | nothing letter/`+`/`#` touches it |
| `c+++` | `c++` | same | ❌ no | a `+` follows, which is forbidden |
| `node.json` | `node.js` | look-arounds | ❌ no | an `o` follows `node.js`, forbidden |

**Caching:** every pattern is compiled once and stored in `_skill_pattern_cache`,
so repeated matching is fast. **Complexity:** matching one skill in text is
roughly O(n) in the text length; extracting all skills is O(S × n) where S is the
number of skills — small and fast in practice.

**Edge case / limitation:** `.net` won't match inside `asp.net` (the `p` touches
it). This is a documented trade-off that avoids worse false matches.

---

## 4.6 Algorithm 3 — Keyword match score (set maths) ⭐

**What it does:** compares resume skills with job skills and produces a %.

**Pseudocode:**
```
resume_skills = set of skills found in resume
job_skills    = set of skills found in job description
matched = resume_skills ∩ job_skills      # intersection (in both)
missing = job_skills − resume_skills       # difference (job needs, resume lacks)
if size(job_skills) == 0:
    match% = 0                             # avoid divide-by-zero
else:
    match% = round(size(matched) / size(job_skills) * 100, 2)
```

**Worked example:**
```
resume_skills = {python, sql, flask, git}
job_skills    = {python, sql, flask, docker, aws}

matched = {python, sql, flask}        -> size 3
missing = {docker, aws}               -> size 2
total job skills = 5
match% = 3 / 5 * 100 = 60.0%
```

**Why a set and not a list?** Sets drop duplicates automatically and give us
`∩` and `−` directly, which is both fast and easy to explain. **Complexity:**
set intersection/difference are about O(k) where k is the number of skills —
very fast.

**Edge cases:** empty resume → `matched` empty → 0%. Empty/keyword-free job
description → `total = 0` → the `if` returns 0% with no crash.

---

## 4.7 Algorithm 4 — Readiness score (weighted blend)

**What it does:** combines four signals into one 0–100 score. The weights are
fixed and **sum to 100**.

**The formula (plain language):**
```
readiness =  0.60 × (keyword match %)
          +  0.20 × (percent of 4 key sections present)
          +  0.10 × (contact completeness: 50 for email + 50 for phone)
          +  0.10 × (readability: 100, minus 50 if <80 words, minus 30 if cluttered)
then clamp the result to the range 0..100
```

**Variables explained:**
- *keyword match %* — from Algorithm 3 (0–100).
- *sections* — of `[Work Experience, Education, Technical Skills, Projects]`, how
  many are present, as a percentage.
- *contact* — 0, 50, or 100.
- *readability* — starts at 100 and loses points for being too short or cluttered.

**Worked example (a strong resume):**
```
keyword match % = 100     -> contributes 0.60 × 100 = 60
all 4 sections present    -> 100%  -> 0.20 × 100 = 20
email + phone found       -> 100   -> 0.10 × 100 = 10
long, tidy resume         -> 100   -> 0.10 × 100 = 10
TOTAL = 60 + 20 + 10 + 10 = 100  (clamped to 100)
```

**Worked example (a weaker resume):**
```
keyword match % = 40      -> 0.60 × 40 = 24
2 of 4 sections (50%)     -> 0.20 × 50 = 10
email only (50)           -> 0.10 × 50 = 5
short resume (100-50=50)  -> 0.10 × 50 = 5
TOTAL = 24 + 10 + 5 + 5 = 44
```

**Why clamp?** So the score can never be below 0 or above 100, even if weights
were changed. **Edge case:** empty inputs give 0 across the board → total 0, no
crash. The UI shows each component's contribution so nothing is a "black box".

---

## 4.8 Putting it together — a mini sequence diagram

```
 app.py            analyzer.py                         sample_data.py
   |                   |                                     |
   |-- analyze_resume->|                                     |
   |                   |-- extract_skills(resume) ---------->| (reads SKILL_DATABASE)
   |                   |<------- skills by category ---------|
   |                   |-- extract_skills(job) ------------->|
   |                   |<------- skills by category ---------|
   |                   |-- calculate_keyword_match (sets)    |
   |                   |-- calculate_readiness_score         |
   |                   |-- generate strengths/suggestions    |
   |<--- analysis dict-|                                     |
   |-- render_dashboard (metrics, tabs, charts)              |
```

---

## 4.9 Checklist for this chapter

- [ ] I can list the startup steps from `streamlit run app.py` to the browser.
- [ ] I can trace what happens when "Analyze" is clicked.
- [ ] I can work out a match % from two small skill sets by hand.
- [ ] I can explain why `\b` handles `r` but not `c++`.
- [ ] I can compute a readiness score from the four components.

➡️ **Next:** Chapter 5 shows how to install, run, test, and troubleshoot the
project.
