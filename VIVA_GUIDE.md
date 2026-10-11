# ResumeIQ — Viva Guide

A preparation guide for the Master of Engineering mini-project viva. It contains
**40 conceptual questions with concise answers** followed by **10 code-explain /
modify tasks**, plus a **demonstration script**.

---

## Part A — 40 Conceptual Questions & Answers

**1. What is Python string manipulation?**
Using Python's built-in operations (slicing, `.lower()`, `.split()`, `.strip()`,
replacement, regex) to transform and analyse text. It is the core of this project.

**2. What are embedded strings (in this project)?**
Predefined multiline text literals written directly in the source using
triple quotes (`""" ... """`) — our sample resumes, job descriptions, and skill
data. They are *not* machine-learning "embeddings"/vectors.

**3. Why are triple-quoted strings used?**
They let us store multiline text (whole resumes) as a single literal, preserving
line breaks, without escaping newlines.

**4. What is Streamlit?**
An open-source Python framework for building data/web apps with pure Python —
widgets, charts, and layout without HTML/JS.

**5. Why Streamlit instead of Flask?**
Flask needs routes, templates, and separate frontend code. Streamlit gives
interactive widgets and charts in a few lines of Python — ideal for a data app.

**6. What is a regular expression?**
A pattern language for matching text. We use it to clean text, find emails/phones,
and match skills safely.

**7. What is a dictionary in Python?**
An unordered collection of `key: value` pairs. `SKILL_DATABASE` maps a category
to a list of skills.

**8. Why is a skill dictionary used?**
It is our controlled vocabulary of recognised skills, grouped by category, which
makes extraction and reporting structured and meaningful.

**9. What is case-insensitive matching?**
Treating "Python", "PYTHON", "python" as the same. We lowercase the text before
matching.

**10. Why are sets useful for comparing keywords?**
Sets remove duplicates and support direct operations: `∩` (intersection) for
matched skills, `−` (difference) for missing skills.

**11. Difference between a list and a set?**
A list is ordered and allows duplicates; a set is unordered, unique, and supports
fast membership and set algebra.

**12. How is the keyword match score calculated?**
`matched ÷ total_job_keywords × 100`, where keywords are recognised skills found
in the job description. If there are no job keywords, the score is 0 (no crash).

**13. How are missing skills identified?**
`missing = job_skills.difference(resume_skills)` — skills the job needs that the
resume does not mention.

**14. Why is preprocessing required?**
So that "Python," / "PYTHON" / "python" all match, whitespace is normalised, and
tech symbols (`c++`, `.net`) survive. It makes matching reliable.

**15. How are PDF and DOCX files processed?**
`pypdf` extracts text from PDF pages; `python-docx` reads paragraphs from DOCX.
TXT is decoded directly. See `extract_text_from_file()`.

**16. Why can scanned PDFs fail?**
A scanned PDF is an image of text — there is no selectable text to extract. It
would need OCR, which is out of scope.

**17. How is the readiness score calculated?**
A weighted blend: keywords 60% + sections 20% + contact 10% + readability 10%
(weights sum to 100). The per-component contribution is shown in the UI.

**18. What are false positives and false negatives?**
False positive: detecting something that is not really there (e.g. a number that
looks like a phone). False negative: missing something real (e.g. ML skills
described without the exact keyword).

**19. What are the limitations of string matching?**
It matches surface keywords, not meaning; synonyms and paraphrases are missed,
and proficiency cannot be judged.

**20. How could the app be improved using NLP?**
Use embeddings / transformer models to capture meaning and synonyms, so
"built ML models" matches "machine learning".

**21. Difference between keyword matching and semantic similarity?**
Keyword matching checks exact token overlap; semantic similarity compares meaning
using vector representations, catching synonyms and paraphrases.

**22. Why is a database not required?**
Reference data is small and static (embedded in code), and user resumes are not
persisted for privacy. A DB would add complexity with no benefit here.

**23. How does Streamlit display charts?**
We build a Plotly figure and pass it to `st.plotly_chart(fig)`.

**24. How does the download functionality work?**
`st.download_button` takes the report/CSV string (encoded to bytes), a filename,
and a MIME type, and serves it to the browser.

**25. How is the application tested?**
With Python's `unittest`: `python -m unittest discover -s tests` runs 30 tests on
`analyzer.py` (all passing).

**26. How is personal information protected?**
Resumes are processed in memory and not stored; contact details are detected but
not shown in summaries; no data is sent to external services.

**27. Can this system guarantee ATS compatibility?**
No. It is a heuristic keyword indicator, not an ATS, and cannot guarantee how any
real ATS will parse a file.

**28. Can it understand a candidate's actual proficiency?**
No. It only detects keywords; it cannot measure depth, quality, or experience.

**29. What are the current algorithm's limitations?**
No semantics/synonyms, pattern-based detection can misfire, single language, and
no OCR.

**30. What future improvements suit a research project?**
Semantic matching, learned skill weights, bias auditing, explainable ranking, and
OCR integration.

**31. Why keep logic in `analyzer.py` separate from `app.py`?**
Separation of concerns: the engine can be unit-tested and reused without the UI.

**32. How do you avoid the skill "R" matching inside "react"?**
`\b` word boundaries: `\br\b` requires non-word characters on both sides, so the
"r" in "react" (followed by "e") does not match.

**33. How do you match `c++` which `\b` can't handle?**
With custom look-arounds: `(?<![a-z0-9+#])c\+\+(?![a-z0-9+#])`, because `+` is not
a word character.

**34. What does `preprocess_text` keep and remove?**
It lowercases, collapses whitespace, and keeps `+ # . / -` (tech symbols) while
turning other punctuation into spaces.

**35. How are multiword skills like "machine learning" matched?**
After whitespace is collapsed to single spaces, we match the exact phrase with
`\bmachine learning\b`.

**36. What does `analyze_resume()` return?**
A single dictionary with statistics, contact, sections, skills, keyword_match,
skill_gap, readiness, quality_checks, strengths, and suggestions.

**37. How is batch screening kept robust?**
Each resume is analysed in a `try/except`; a failure is recorded as an `error`
field so one bad file never crashes the batch.

**38. How are neutral identifiers used in batch mode?**
Candidates are labelled "Candidate 1", "Candidate 2", … so no sensitive or
personal identifiers drive ranking.

**39. What validation prevents bad runs?**
The UI blocks analysis when the resume or job description is empty and shows a
clear error message.

**40. Why is the project "academically defensible"?**
Every number is traceable to a documented formula, the code is simple and tested,
and the limitations are stated honestly rather than overclaiming accuracy.

---

## Part B — 10 Code-Explain / Modify Tasks

1. **Explain** `_build_skill_pattern()` and why special-character skills use a
   different regex than plain skills.
2. **Modify** `SKILL_DATABASE` to add a new category "Mobile" with `android`,
   `ios`, `flutter`, then show it being matched.
3. **Explain** the three lines in `calculate_keyword_match()` that compute
   `matched`, `missing`, and `extra`.
4. **Modify** `DEFAULT_WEIGHTS` so keywords are 70% and readability 0%, and show
   the weights still sum to 100.
5. **Explain** how `preprocess_text()` preserves `node.js` but removes commas.
6. **Modify** `detect_resume_sections()` to add a new section "Languages" with
   headings `["languages", "spoken languages"]`.
7. **Explain** why `count_resume_statistics("")` does not raise a
   ZeroDivisionError.
8. **Modify** `create_analysis_report()` to add a line showing the number of
   detected skills.
9. **Explain** how `analyze_multiple_resumes()` keeps running when one resume
   fails.
10. **Modify** the phone regex in `analyzer.py` to accept only 10-digit numbers
    and discuss the trade-off (fewer false positives, more false negatives).

---

## Part C — Demonstration Script (7–10 minutes)

| Step | You click / do | Expected output | You say |
|------|----------------|-----------------|---------|
| 1 | Open the Home page | Title + metric cards | "This is a rule-based resume analyzer built with Python strings." |
| 2 | Open **Methodology**, expand the skill DB | Skill categories listed | "These embedded triple-quoted strings are our skill vocabulary." |
| 3 | On **Analyze**, *Load by role → Python Developer* | Resume + job fill in | "Embedded samples let it work instantly, offline." |
| 4 | Open **Raw vs Clean** tab after Analyze | Raw vs cleaned text | "Preprocessing lowercases and cleans text but keeps `c++`, `node.js`." |
| 5 | Open **Skills** tab | Category coverage chart | "Skills are extracted from both documents using safe regex matching." |
| 6 | Look at matched/missing | Lists + bar chart | "Matched = intersection, Missing = difference — pure set theory." |
| 7 | Overview tab gauges | Match % and readiness | "The match % is matched ÷ total × 100; readiness is a 60/20/10/10 blend." |
| 8 | **Skill Gap** tab | Gap table | "Each required skill gets an honest recommendation." |
| 9 | **Report** tab → download | `.md` report downloads | "A full report can be exported for the candidate." |
| 10 | Open **About & Limitations** | Limitations list | "It matches keywords, not meaning — a human must stay in the loop." |

Use the *Python Developer* sample for a high score and the *Data Analyst* resume
against the *Python Developer* job to show a visibly lower, different score.
