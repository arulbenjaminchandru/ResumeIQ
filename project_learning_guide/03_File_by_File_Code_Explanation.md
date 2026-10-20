# Chapter 3 — File-by-File Code Explanation

> **How to read this chapter:** We go through the real code, one file at a time,
> in **dependency order** (data first, then the engine that uses it, then the
> web page that uses the engine, then the tests). Each function says: its
> **purpose**, **inputs**, **outputs**, the **important lines**, and a **small
> example**. Line numbers refer to the real files.
>
> **Runtime entry point reminder:** when you *run* the app, Python starts at
> `app.py` (because you type `streamlit run app.py`). But `app.py` imports
> `analyzer.py`, which imports `sample_data.py`. So to *understand* the code it
> is easiest to read them in the reverse (dependency) order below.

**Files covered in this chapter:**
1. `sample_data.py` (the data)
2. `analyzer.py` (the engine) — all 15 sections
3. `app.py` (the web page)
4. `tests/test_analyzer.py` (the tests)

---

## 3.1 `sample_data.py` — the data layer

**Purpose:** Hold all the *data* the app ships with, as **embedded strings**
(text typed directly into the file). It contains **no logic** — nothing is
calculated here.

**What it defines:**

### (a) `SKILL_DATABASE` — a dictionary of lists
```python
SKILL_DATABASE = {
    "Programming Languages": ["python", "java", "c++", "c#", "javascript", ...],
    "Web Development":       ["streamlit", "flask", "django", "node.js", ...],
    "Databases":             ["sql", "mysql", "postgresql", "mongodb", ...],
    ...
}
```
- **Key** = a category name (a string).
- **Value** = a list of skill words, all **lowercase** (so matching is
  case-insensitive).
- There are **10 categories**. Multiword skills (`"machine learning"`,
  `"spring boot"`, `"power bi"`) and special-character skills (`"c++"`, `"c#"`,
  `".net"`, `"node.js"`, `"ci/cd"`, `"scikit-learn"`) are included on purpose to
  show off the matching logic.

**Why lowercase?** Because `analyzer.py` lowercases the resume text too, then
compares. Same case on both sides = reliable matching.

### (b) Five sample resumes
Each is a **triple-quoted string** (a string that can span many lines):
```python
RESUME_PYTHON_DEVELOPER = """
John Mathew
Email: john.mathew@example.com | Phone: +91 98765 43210
...
Technical Skills
Python, SQL, Flask, Streamlit, pandas, NumPy, Git, Docker, REST APIs, Linux
...
"""
```
They are collected into a dictionary so the UI can list them in a dropdown:
```python
SAMPLE_RESUMES = {
    "Python Developer": RESUME_PYTHON_DEVELOPER,
    "Data Analyst":     RESUME_DATA_ANALYST,
    "Java Developer":   RESUME_JAVA_DEVELOPER,
    "AI/ML Engineer":   RESUME_AIML_ENGINEER,
    "Cloud Engineer":   RESUME_CLOUD_ENGINEER,
}
```

### (c) Five sample job descriptions
Same idea, collected into `SAMPLE_JOB_DESCRIPTIONS` with the same five keys.

### (d) `ROLE_SAMPLES` — pairing a resume with its matching job
```python
ROLE_SAMPLES = {
    role: {
        "resume": SAMPLE_RESUMES[role],
        "job_description": SAMPLE_JOB_DESCRIPTIONS[role],
    }
    for role in SAMPLE_RESUMES
}
```
This is a **dictionary comprehension**: for each role, store its resume and job
together. The app's "Load by role" demo button uses this to fill both boxes at
once.

**How it connects:** `analyzer.py` imports `SKILL_DATABASE`; `app.py` imports
`SAMPLE_RESUMES`, `SAMPLE_JOB_DESCRIPTIONS`, `ROLE_SAMPLES`, and `SKILL_DATABASE`.

**Beginner mistake to avoid:** editing a skill to UPPERCASE here would break
matching, because the engine compares against lowercase text.

---

## 3.2 `analyzer.py` — the engine (the most important file)

It has **15 numbered sections**. We cover each. Remember: this file never
imports Streamlit, so it can be tested on its own.

```python
import io
import re
from sample_data import SKILL_DATABASE
```
- `io` → used to treat uploaded file **bytes** as a readable stream.
- `re` → regular expressions, used all over.
- `SKILL_DATABASE` → the skill list, used as the default for matching.

### Section 1 — `preprocess_text(text)` (lines 44–77)

**Purpose:** Clean raw text so matching is reliable.
**Input:** any text (or even `None`/non-text). **Output:** a cleaned, lowercased,
single-spaced string.

```python
if not text or not isinstance(text, str):
    return ""                                    # (1) safety for empty/bad input
text = text.lower()                              # (2) lowercase everything
text = re.sub(r"[^a-z0-9+#./\-\s]", " ", text)   # (3) keep letters/digits/tech symbols; rest -> space
text = re.sub(r"\s+", " ", text).strip()         # (4) squeeze all spaces to one; trim ends
return text
```
- **(1)** If the input is empty or not a string, return `""` instead of crashing.
- **(2)** `"Python"` becomes `"python"`.
- **(3)** The pattern `[^a-z0-9+#./\-\s]` means "any character that is **not** a
  lowercase letter, digit, whitespace, or one of `+ # . / -`". Those become a
  space. **Keeping `+ # . / -`** is the clever part: it protects `c++`, `c#`,
  `.net`, `node.js`, `ci/cd`.
- **(4)** Turns runs of spaces/newlines into a single space, then trims.

**Example:** `preprocess_text("C++, Python!\n\nSQL")` → `"c++ python sql"`.

**Remove this and...** every later step gets confused by capital letters and
punctuation, so matching would badly under-count.

### Section 2 — Skill matching helpers (lines 102–188)

This section solves the hardest problem: matching a skill as a **whole word**
without wrong matches.

**`_build_skill_pattern(skill)` (lines 106–129)** — builds a regex for one skill
and **caches** it (so each pattern is compiled only once):
```python
if any(ch in _SPECIAL_SKILL_CHARS for ch in skill):     # has + # . / - ?
    boundary = r"[a-z0-9+#]"
    pattern = r"(?<!{b}){s}(?!{b})".format(b=boundary, s=escaped)  # look-arounds
else:
    pattern = r"\b{s}\b".format(s=escaped)              # normal word boundaries
```
- **Normal skills** (letters only, like `python`, `r`) use `\b...\b`. The `\b`
  (word boundary) is why `r` matches the language *R* but **not** the `r` inside
  `react` (because inside `react`, `r` is touching the letter `e`, so there is
  no boundary).
- **Special skills** (`c++`, `c#`, `.net`, ...) **cannot** use `\b`, because `+`
  and `#` are not "word" characters. Instead we say: "not touching a letter,
  digit, `+` or `#` on either side" using **look-behind** `(?<!...)` and
  **look-ahead** `(?!...)`. This matches `c++` but not `c+++` or `ac++`.

**`skill_in_text(skill, cleaned_text)` (lines 132–137):** returns `True`/`False`
by searching the compiled pattern in the already-cleaned text.

**`extract_skills(text, skill_database)` (lines 140–167):** the main one.
```python
cleaned = preprocess_text(text)              # clean once
found = {}
for category, skills in skill_database.items():   # each category
    matches = []
    for skill in skills:                     # each skill in that category
        if skill_in_text(skill, cleaned) and skill not in matches:
            matches.append(skill)
    if matches:
        found[category] = matches            # only keep non-empty categories
return found
```
**Output:** a dictionary like `{"Programming Languages": ["python"], ...}`.

**`flatten_skills(skills_by_category)` (lines 170–179):** merges all the
category lists into **one set** (no duplicates) — ready for set maths.

**`skill_category_lookup(...)` (lines 182–188):** builds the reverse map
`{skill: category}`, used to label rows in the skill-gap table.

**Example:**
```python
extract_skills("I use Python and C++")
# {'Programming Languages': ['python', 'c++']}
flatten_skills(_)        # {'python', 'c++'}
```

### Section 3 — `count_resume_statistics(text)` (lines 195–236)

**Purpose:** basic numbers about the resume. **Input:** raw text. **Output:**
a dict with `word_count`, `character_count`, `line_count`, `sentence_count`,
`average_word_length`.
- `word_count = len(text.split())` → words = pieces separated by whitespace.
- `character_count = len(text)` → every character, spaces included.
- `line_count` → counts only **non-empty** lines (via a list comprehension).
- `sentence_count = len(re.findall(r"[.!?]+", text))` → counts groups of
  `. ! ?`. If there is text but no such mark, it is set to `1`.
- `average_word_length` → total letters ÷ number of words, rounded to 2 dp; if
  there are no words it is `0.0` (so there is **no divide-by-zero**).

### Section 4 — `detect_contact_information(text)` (lines 246–304)

**Purpose:** find contact details by **pattern**. Uses compiled regexes:
- Email: `[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}` → "stuff @ stuff . 2+
  letters".
- Phone: a loose digit pattern, then it **keeps only** candidates with 10–15
  digits (to avoid random long numbers).
- LinkedIn / GitHub: look for `linkedin.com/...` / `github.com/...`.
- Portfolio: any other website-looking URL.

**Output:** a dict of `{"found": bool, "count": int}` style entries. It also
returns the raw `emails` list **for internal use only** — the UI never displays
personal details.

**Honest note (say this in viva):** this is pattern-based, so it can miss odd
formats or occasionally over-match. The code comments say so.

### Section 5 — `detect_resume_sections(text)` (lines 312–353)

**Purpose:** guess which resume sections are present. `SECTION_KEYWORDS` maps a
canonical name (e.g. `"Work Experience"`) to **alternative headings** (e.g.
`"employment history"`, `"work history"`). For each section it checks whether
**any** heading variant appears (as a whole word). **Output:** `detected`
(name→bool), `present` (list), and `missing` (list — described as *possibly*
missing, since a resume might use an unusual heading).

### Section 6 — Job keywords + `calculate_keyword_match(...)` (lines 360–411) ⭐

This is the core scoring.

`extract_job_keywords(jd)` = the **set** of recognised skills in the job
description (reuses `extract_skills` + `flatten_skills`).

`calculate_keyword_match(resume_text, job_description)`:
```python
resume_skills = extract_job_keywords(resume_text)   # a set
job_skills    = extract_job_keywords(job_description) # a set

matched = resume_skills.intersection(job_skills)   # in BOTH
missing = job_skills.difference(resume_skills)     # job needs, resume lacks
extra   = resume_skills.difference(job_skills)     # bonus

total = len(job_skills)
if total > 0:
    match_percentage = round(len(matched) / total * 100, 2)
else:
    match_percentage = 0.0        # no keywords in JD -> 0%, no crash
```
**Output dict:** sorted `matched`/`missing`/`extra` lists, the counts, and
`match_percentage`. The `if total > 0` check is what prevents a
**divide-by-zero** when the job description has no recognised skills.

### Section 7 — `detect_experience_education(text)` (lines 425–458)

Finds **approximate** signals: years of experience (`(\d+)\+?\s*years?`), degree
keywords (from `_DEGREE_KEYWORDS`), graduation years (`1950`–`2099`), and
booleans for internship/projects/certifications. **Honest note:** approximate,
never invents qualifications.

### Section 8 — Quality checks (lines 465–530)

`has_excessive_whitespace(text)` → `True` if there are many blank lines or long
runs of spaces. `resume_quality_checks(...)` → a list of
`{"label", "passed", "note"}` items (email present? skills section present?
reasonable length? etc.). These are **heuristics**, clearly labelled — a failing
check is a hint to review, not a penalty.

### Section 9 — `calculate_readiness_score(...)` (lines 549–622) ⭐

**Purpose:** a broader 0–100 score. The weights are documented and **sum to
100**:
```python
DEFAULT_WEIGHTS = {"keyword_coverage": 60, "sections": 20,
                   "contact": 10, "readability": 10}
```
Each component is turned into a 0–100 percentage, then:
`contribution = score_pct / 100 * weight`, and the total is the sum, **clamped**
to 0–100 (`round(max(0.0, min(100.0, total)), 2)`).
- **keyword_coverage** = the match percentage from Section 6.
- **sections** = fraction of 4 important sections present × 100.
- **contact** = 50 for an email + 50 for a phone.
- **readability** = starts at 100; −50 if very short (<80 words); −30 if
  cluttered whitespace.

**Output:** `{"components": {...per-component numbers...}, "total": number}` so
the UI can show exactly how the total was built.

### Section 10 — `analyze_skill_gaps(resume_skills, job_skills)` (lines 629–663)

Builds **one row per required skill**: `skill`, `category`, `in_resume` (bool),
`required_by_job` (always True here), and an honest `recommendation`. If the
skill is missing, the recommendation says *"if you genuinely have it, add it;
otherwise learn it"* — it **never** tells anyone to lie.

### Section 11 — Strengths & suggestions (lines 670–747)

`generate_resume_strengths(analysis)` → evidence-backed positives (e.g. "Matched
5 of 7 keywords"). Every strength is tied to something actually detected.

`generate_improvement_suggestions(analysis)` → `if/else` rules producing tips
(no email? add one. missing keywords? review them honestly. too short? add
detail.). Each tip is linked to a real detected condition, so tips never
contradict the analysis.

### Section 12 — `analyze_resume(...)` (lines 754–809) ⭐ the conductor

**Purpose:** run the **whole pipeline** and return one big results dictionary.
This is the function the UI and the compare/batch features all call, so the
matching logic lives in exactly one place.
```python
statistics   = count_resume_statistics(resume_text)
contact      = detect_contact_information(resume_text)
sections     = detect_resume_sections(resume_text)
exp_edu      = detect_experience_education(resume_text)
resume_skills = extract_skills(resume_text)
job_skills    = extract_skills(job_description)
...
keyword_match = calculate_keyword_match(resume_text, job_description)
skill_gap     = analyze_skill_gaps(resume_skills_flat, job_skills_flat)
readiness     = calculate_readiness_score(keyword_match, sections, contact, statistics, resume_text)
quality       = resume_quality_checks(...)
analysis = { ...all of the above... }
analysis["strengths"]   = generate_resume_strengths(analysis)
analysis["suggestions"] = generate_improvement_suggestions(analysis)
return analysis
```
**Output:** a dictionary with keys like `statistics`, `contact`, `sections`,
`keyword_match`, `skill_gap`, `readiness`, `strengths`, `suggestions`,
`raw_text`, `job_title`. Everything the UI needs is in this one object.

### Section 13 — Compare & batch (lines 816–896)

`compare_resumes(resume_a, resume_b, job_description, ...)` → runs
`analyze_resume` on both and returns a tidy side-by-side `summary` list.

`analyze_multiple_resumes(resumes, job_description, max_files=10)` → screens a
list of resumes. Each item can be plain text or `(name, text)`. Each is wrapped
in `try/except`, so **one broken file does not stop the batch** (the failure is
recorded in an `error` field). `max_files` caps how many are processed.

### Section 14 — `extract_text_from_file(uploaded_file)` (lines 903–970)

**Purpose:** turn an uploaded `.txt/.pdf/.docx` into text.
- Reads the raw bytes with `.read()`.
- `.txt` → `raw.decode("utf-8")`.
- `.pdf` → uses `pypdf`'s `PdfReader`, joins each page's `extract_text()`. If the
  result is empty it raises a friendly `ValueError` explaining it may be a
  scanned/image PDF (needs OCR, out of scope).
- `.docx` → uses `python-docx` to join paragraph text.
- Any other extension → a friendly `ValueError`.

### Section 15 — Reports: `create_analysis_report` & `create_analysis_pdf`

`create_analysis_report(analysis)` (lines 977–1054) → builds a **Markdown**
string (used for the on-screen preview).

`_pdf_safe(text)` (lines 1057–1063) → replaces characters the basic PDF font
cannot draw, so PDF generation never crashes.

`create_analysis_pdf(analysis)` (lines 1066–1170) → builds a **PDF** with
`fpdf2` and returns it as `bytes` for the download button. It mirrors the
Markdown report so the preview and the PDF stay consistent. (Note the little
`write()` helper passes `new_x="LMARGIN", new_y="NEXT"` — this is required by
fpdf2 so each line starts at the left margin; without it fpdf2 errors.)

---

## 3.3 `app.py` — the web page (the UI layer)

**Purpose:** everything the user sees and clicks. It imports the engine and the
data:
```python
import analyzer
from sample_data import (ROLE_SAMPLES, SAMPLE_JOB_DESCRIPTIONS,
                         SAMPLE_RESUMES, SKILL_DATABASE)
```

### Page setup & disclaimer (lines 34–48)
`st.set_page_config(...)` sets the tab title, icon and wide layout. A `DISCLAIMER`
string is shown on the main pages to keep the tool honest.

### Chart helpers (lines 51–113)
- `gauge_chart(value, title)` → a 0–100 dial (used for Match % and Readiness).
- `matched_missing_bar(keyword_match)` → a green/red bar of matched vs missing.
- `category_coverage_chart(resume_skills, job_skills)` → grouped bars comparing,
  per category, how many skills the resume has vs the job wants.

### The session_state pattern (lines ~100–145) — important!
Because Streamlit **reruns the whole script** on every click, the text boxes
store their content in `st.session_state` under keys like `"resume_area"` and
`"job_area"`. Small **callback** functions fill those boxes safely:
- `_load_sample_resume()` / `_load_sample_job()` / `_load_role_demo()` → put
  sample text into the boxes **before** the widgets are drawn.
- `_reset_all()` → clears the boxes and the stored analysis.

> **The bug this fixed (great viva story):** originally the text area used both
> `value=...` and `key="resume_area"`. Streamlit **ignores `value=`** once a
> widget has a key, so an uploaded resume appeared to extract successfully but
> the box stayed empty. The fix: stop using `value=`, and write directly to the
> widget's `session_state` key (via callbacks or before the widget is created).

### `resume_input_block()` (lines 180–223)
Draws the resume input: a radio to choose *Paste / Upload / Use a sample*. For
uploads it calls `analyzer.extract_text_from_file(...)` and only extracts **once
per new file** (tracked by name+size) so your edits are not wiped on every
rerun. The editable text area (`key="resume_area"`) is the **single source of
truth** that gets analysed.

### `job_input_block()` (lines 225–252)
Same idea for the job description, plus an optional job-title box and a
"Load by role" demo button.

### `page_analyze()` (lines 254–285)
The main page. It shows the two input blocks, an **Analyze** button and a
**Reset** button. **Validation:** if the resume or job text is empty it shows an
error and stops. Otherwise it calls `analyzer.analyze_resume(...)` and stores the
result in `st.session_state["analysis"]`, then calls `render_dashboard`.

### `render_dashboard(analysis)` (lines 287–447)
Shows the results. Top row = four `st.metric` cards (Match %, Readiness, Matched,
Missing). Then `st.tabs([...])` creates seven tabs:
1. **Overview** — the two gauges, the matched/missing bar, the readiness
   breakdown table, statistics, contact categories, sections.
2. **Skills** — the category-coverage chart and the skill lists.
3. **Skill Gap** — the per-skill table + a **Download CSV** button.
4. **Quality Checks** — the heuristic checklist + approximate exp/education.
5. **Strengths & Suggestions** — two columns.
6. **Raw vs Clean** — shows the text before and after `preprocess_text`, so you
   can *see* preprocessing working.
7. **Report** — the Markdown preview + a **Download PDF** button
   (`analyzer.create_analysis_pdf`).

### `page_compare()` (lines 449–489)
Pick two sample resumes + one job; calls `analyzer.compare_resumes(...)`; shows a
side-by-side table and a comparison bar chart.

### `page_batch()` (lines 492–550)
Upload up to 10 resumes (or use the 5 samples); each is turned into `(name,
text)` — **the file name is used as the label** — then `analyzer.analyze_
multiple_resumes(...)` screens them. Shows a sorted table and a **Download CSV**
button. The "Resume" column and the CSV use the real file names.

### `page_methodology()` and `page_about()` (lines 553–614)
Static explanation pages (the algorithm; limitations and responsible use).

### Sidebar navigation (lines 616–632)
```python
PAGES = { "🏠 Home": page_home, "🔍 Analyze Resume": page_analyze, ... }
selection = st.sidebar.radio("Navigate", list(PAGES.keys()))
PAGES[selection]()     # call the chosen page's function
```
`PAGES` is a dictionary whose **values are functions**. The radio returns the
chosen label; `PAGES[selection]()` then **calls** that page's function. This is a
clean, simple router.

---

## 3.4 `tests/test_analyzer.py` — the tests

**Purpose:** automatically prove the engine is correct. Uses Python's built-in
`unittest`. Tests are grouped into classes like `TestKeywordMatch`,
`TestSkillMatching`, `TestContactDetection`, etc. Each method is one test.

**Example test (the famous "R" case):**
```python
def test_single_letter_r_matches_only_as_word(self):
    self.assertTrue(analyzer.skill_in_text("r", analyzer.preprocess_text("skills: python, r, sql")))
    self.assertFalse(analyzer.skill_in_text("r", analyzer.preprocess_text("react and recruiting")))
```
- `assertTrue(...)` → the test passes only if the value is `True`.
- `assertFalse(...)` → passes only if `False`.
- So this proves `r` matches the standalone language but **not** inside `react`.

There are **31 tests** in total, covering good matches, no matches, empty inputs,
empty job descriptions (no divide-by-zero), mixed case, `c++`/`c#`/`.net`/
`node.js`, the `r` case, multiple emails, alternate headings, duplicate skills,
whitespace, comparison ordering, batch robustness, and PDF generation. How to run
them is in Chapter 5.

---

## 3.5 Files-explained checklist

- [x] `sample_data.py` — fully explained.
- [x] `analyzer.py` — all 15 sections explained.
- [x] `app.py` — all pages and the session_state pattern explained.
- [x] `tests/test_analyzer.py` — purpose and structure explained.
- [x] `requirements.txt`, `README.md`, `PROJECT_REPORT.md`, `VIVA_GUIDE.md`,
      `.gitignore` — described in Chapter 1 (no complex logic to walk through).

**Nothing important remains unexplained.** The only files not walked through
line-by-line are plain documentation and the auto-generated `__pycache__` /
`venv` folders, which contain no project logic.

➡️ **Next:** Chapter 4 traces exactly what happens when you click **Analyze**,
and explains the key algorithms with worked examples.
