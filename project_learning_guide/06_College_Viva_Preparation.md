# Chapter 6 — College Viva Preparation

> **How to use this chapter:** Read the three explanations aloud until they feel
> natural (don't memorise word-for-word — understand them). Practise the demo
> script on the running app. Then go through the questions and make sure you can
> *explain* each answer, not just recite it.

---

## 6.1 Explain the project in three lengths

### A. The 30-second version
> "ResumeIQ is a Python and Streamlit web app that checks how well a resume
> matches a job description. It cleans both texts, looks for known skills in
> each, and uses set maths — the overlap — to give a match score and a list of
> missing skills. It's fully rule-based and offline, so every number can be
> explained."

### B. The 2-minute version
> "The problem I'm solving is that comparing a resume to a job by hand is slow
> and inconsistent. ResumeIQ automates the first-pass keyword screen.
>
> It has three layers. `sample_data.py` holds the data — a skill dictionary and
> some sample resumes and jobs, all as embedded strings. `analyzer.py` is the
> engine: it cleans text with `preprocess_text`, finds skills with regular
> expressions, and compares them. `app.py` is the Streamlit web page with the
> buttons, charts, and downloads.
>
> The core is set theory. I put the resume's skills in one set and the job's
> skills in another. The intersection is the matched skills; the difference
> (job minus resume) is the missing skills. The match percentage is matched
> divided by total job skills, times 100. I also build a readiness score out of
> four weighted parts — keywords 60%, sections 20%, contact 10%, readability
> 10% — which always add up to 100.
>
> It's tested with 31 automated unittest cases, and it's honest about its
> limits: it matches keywords, it doesn't understand meaning."

### C. The 5-minute version (add these points to B)
- **Why Streamlit, not Flask:** Streamlit builds an interactive data app with
  charts in pure Python — no HTML/JavaScript — which suits a single-developer
  academic project.
- **The clever matching:** `\b` word boundaries stop `r` matching inside
  `react`; special look-arounds handle `c++`, `c#`, `.net`, `node.js`, `ci/cd`
  which `\b` can't. Patterns are compiled once and cached.
- **The conductor function:** `analyze_resume()` runs every step and returns one
  dictionary, so the UI, the compare feature, and the batch feature all reuse
  the same logic — no duplicated matching code.
- **Extra features:** upload `.pdf/.docx/.txt` (via pypdf / python-docx), compare
  two resumes, batch-screen many, download a PDF report (fpdf2) and CSV exports.
- **Safety & honesty:** no divide-by-zero (guarded), scores clamped 0–100, files
  processed in memory, no secrets, no AI over-claims.
- **A real engineering moment:** I hit and fixed a Streamlit `session_state` bug
  where a text area with both `value=` and a `key=` ignored the uploaded text;
  the fix was to use callbacks and write to the widget's session-state key.

---

## 6.2 Demonstration script (step-by-step)

| # | Do this | Say this |
|---|---------|----------|
| 1 | `streamlit run app.py`; show the Home page | "This runs entirely offline on my machine." |
| 2 | Open **Methodology**, expand the skill database | "These embedded strings are my skill vocabulary." |
| 3 | On **Analyze**, choose **Load by role → Python Developer** | "Embedded samples let it work instantly." |
| 4 | Click **Analyze**; show the metric cards | "Match % and readiness, computed by rules." |
| 5 | Open **Raw vs Clean** | "Here's preprocessing: lowercased and cleaned, but `c++`/`node.js` survive." |
| 6 | Open **Skills**; show matched vs missing | "Matched is the set intersection; missing is the set difference." |
| 7 | Open **Overview** gauges; expand readiness breakdown | "The four weights add up to 100 — nothing hidden." |
| 8 | Open **Skill Gap**; download CSV | "One honest recommendation per required skill." |
| 9 | Open **Report**; download PDF | "A shareable PDF report." |
| 10 | Switch to **Data Analyst** resume vs the same Python job | "A lower score, because skills are missing — the tool is discriminating, not random." |
| 11 | Open **About & Limitations** | "It matches words, not meaning — a human must stay in the loop." |
| 12 | In the terminal, run the tests | "`Ran 31 tests ... OK` — the logic is verified." |

---

## 6.3 Fifty+ viva questions with answers

### Objectives & problem statement
1. **What does your project do?** It compares a resume to a job description and
   reports a keyword match score, missing skills, and improvement tips.
2. **What problem does it solve?** It automates the slow, inconsistent first-pass
   keyword screening of resumes and gives transparent feedback.
3. **Who is it for?** Students/job seekers, recruiters (first pass), and faculty
   evaluating the project.
4. **Why is it "academically defensible"?** Every number comes from a documented
   formula; the code is simple, tested, and honest about limits.
5. **Is it AI?** No. It is **rule-based** string processing — no machine learning,
   no external AI service.

### Embedded strings & data
6. **What are embedded strings here?** Sample resumes, job descriptions, and the
   skill list written directly into `sample_data.py` using triple quotes.
7. **Why triple-quoted strings?** They let a whole multi-line resume be one
   string literal, keeping line breaks.
8. **What is `SKILL_DATABASE`?** A dictionary whose keys are categories and whose
   values are lists of skill words — a "dictionary of lists".
9. **Why store skills in lowercase?** Because the engine lowercases the resume
   too, so matching is case-insensitive and reliable.
10. **Why no database?** The data is tiny and static, and user resumes are not
    stored (for privacy), so a database would add complexity with no benefit.

### Architecture & files
11. **Describe the architecture.** Three layers: `app.py` (UI), `analyzer.py`
    (logic), `sample_data.py` (data), plus `tests/`.
12. **Why separate the layers?** Separation of concerns — each is simple,
    testable, and replaceable on its own.
13. **Which file is the entry point?** `app.py`, run via `streamlit run app.py`.
14. **Why can the tests run without Streamlit?** Because `analyzer.py` never
    imports Streamlit; the tests import only the engine.
15. **What does `analyze_resume()` do?** It runs the whole pipeline and returns
    one results dictionary used by the UI, compare, and batch features.

### Python concepts
16. **Difference between a list and a set?** A list is ordered and allows
    duplicates; a set is unordered, unique, and supports `intersection`/
    `difference`.
17. **Why use sets for matching?** They remove duplicates and give the overlap
    and difference directly and fast.
18. **What is `intersection`?** Items present in **both** sets — the matched
    skills.
19. **What is `difference`?** Items in the first set but not the second — e.g.
    `job − resume` = missing skills.
20. **What is a dictionary?** A collection of `key: value` pairs; used for
    `SKILL_DATABASE` and the big results dictionary.
21. **What is a list comprehension?** A one-line way to build a list with a loop,
    e.g. counting non-empty lines.
22. **What is an f-string?** A string with `{variables}` inside, prefixed with
    `f`, used to build messages and report lines.
23. **What is truthiness?** Empty values (`""`, `[]`, `0`, `None`) act as `False`
    in an `if`; used to guard empty inputs.

### Regular expressions & matching
24. **What is a regular expression?** A pattern language for finding shapes in
    text; Python's `re` module runs them.
25. **What does `\b` do?** Matches a word boundary (the edge of a word), so
    `\br\b` matches a standalone `r`.
26. **Why doesn't `r` match in `react`?** Because inside `react` the `r` touches
    `e`, so there is no word boundary after it.
27. **How do you match `c++`?** With look-arounds `(?<![a-z0-9+#])c\+\+
    (?![a-z0-9+#])`, because `\b` doesn't work with `+`.
28. **Why cache compiled patterns?** So each skill's regex is built once, making
    repeated matching faster.
29. **How are multiword skills like "machine learning" matched?** After
    whitespace is collapsed to single spaces, the exact phrase is matched with
    `\b`.
30. **What is a false positive / false negative?** False positive = flagging
    something that isn't really there; false negative = missing something that
    is there.

### Scoring
31. **How is the keyword match score calculated?** `matched ÷ total_job_keywords
    × 100`.
32. **What if the job description has no keywords?** `total = 0`, so the code
    returns 0% without dividing by zero.
33. **What are the readiness weights?** Keywords 60, sections 20, contact 10,
    readability 10 — they sum to 100.
34. **How do you stop the score going above 100 or below 0?** It is clamped with
    `max(0, min(100, total))`.
35. **Why show each component's contribution?** For transparency — the user sees
    exactly how the total was built.

### Text processing & statistics
36. **What does `preprocess_text` do?** Lowercases, replaces noise punctuation
    with spaces (keeping `+ # . / -`), and collapses whitespace.
37. **Why keep `+ # . /`?** To protect tech names like `c++`, `c#`, `.net`,
    `node.js`, `ci/cd`.
38. **How do you count words?** `len(text.split())`.
39. **How do you count sentences?** Count groups of `. ! ?` with a regex (set to
    1 if there is text but no terminator).
40. **How is average word length computed, safely?** Total letters ÷ word count;
    if there are no words it returns `0.0` to avoid divide-by-zero.

### Files, libraries, testing
41. **How are PDF/DOCX read?** `pypdf` extracts PDF page text; `python-docx`
    reads Word paragraphs; `.txt` is decoded directly.
42. **Why can scanned PDFs fail?** They are images with no selectable text;
    extraction returns nothing, so a clear error is raised (OCR is out of scope).
43. **Why pandas?** To show neat tables and export CSV with one line.
44. **Why Plotly?** For interactive gauges and bar charts.
45. **Why fpdf2?** To create the downloadable PDF report in pure Python, no
    system dependencies.
46. **How is the project tested?** 31 `unittest` cases in `tests/test_analyzer
    .py`, run with `python -m unittest discover -s tests`.
47. **Did the tests pass?** Yes — `Ran 31 tests ... OK` (verified on Python
    3.14.6).
48. **How is personal data protected?** Resumes are processed in memory, not
    stored; contact details are detected but not displayed in summaries.

### Limitations & future work
49. **Biggest limitation?** It matches keywords, not meaning, so synonyms are
    missed.
50. **Can it guarantee ATS compatibility?** No — it is a heuristic indicator, not
    an ATS.
51. **How would you improve it?** Add semantic matching (embeddings/NLP models),
    OCR for scanned PDFs, learned skill weights, and optional storage — all
    listed as *future* work, not implemented.
52. **Why keep it rule-based for now?** So it stays fully explainable, offline,
    and suitable for a mini-project viva.

---

## 6.4 Code-specific questions (based on the real files)

1. **Why does `extract_skills` take `skill_database=SKILL_DATABASE` as a default
   parameter?** So you can call it with just text in normal use, but still pass a
   different skill set in tests.
2. **In `calculate_keyword_match`, what does `job_skills.difference(resume_
   skills)` contain?** The missing skills — those the job needs that the resume
   lacks.
3. **What happens in `preprocess_text("")`?** The `if not text` guard returns
   `""` immediately.
4. **What would break if you removed the `if total > 0` check in
   `calculate_keyword_match`?** A job description with no skills would cause a
   divide-by-zero crash.
5. **What does the `try/except` in `analyze_multiple_resumes` protect against?**
   One unreadable/odd resume crashing the entire batch; the error is recorded
   per row instead.
6. **Why is `resume_area` used as the text area's `key`?** So its content
   survives Streamlit reruns and is the single source of truth for analysis.
7. **What does `PAGES[selection]()` do?** Looks up the chosen page's function in
   the `PAGES` dictionary and calls it.
8. **What does `flatten_skills` return and why a set?** One set of all skills; a
   set removes duplicates and enables set maths.
9. **If you changed `DEFAULT_WEIGHTS` to `{"keyword_coverage": 100}` only, what
   happens?** Readiness would equal the keyword match %; the code still clamps
   0–100. (You'd want the weights to sum to 100 to keep it meaningful.)
10. **Why does `create_analysis_pdf` return `bytes`?** Because
    `st.download_button` needs bytes (or text) as the file data.

---

## 6.5 Explain it to different audiences

- **To a 12-year-old (30s):** "It reads your CV and a job advert, and tells you
  which important words match and which are missing — like a spell-checker, but
  for job skills."
- **To a classmate (2 min):** use section 6.1.B.
- **To an examiner (5 min):** use section 6.1.C, then offer to show the code for
  `calculate_keyword_match` and run the tests.

➡️ **Next:** Chapter 7 — glossary, a one-page revision sheet, and a final
self-assessment checklist.
