# ResumeIQ — Beginner's Project Learning Guide

Welcome! This folder is a complete, beginner-friendly guide to the **ResumeIQ —
Smart Resume Analyzer** project. It is written for a first-year student who knows
only basic Python (variables, loops, functions, lists, dictionaries). Everything
else is explained from zero.

> This guide is **documentation only**. It does not change any application code.

---

## 📚 How to read this guide (in order)

| # | File | What you'll learn | Read if you want to... |
|---|------|-------------------|------------------------|
| 1 | [01_Project_Overview.md](01_Project_Overview.md) | What the project is, why it exists, the 3-layer design | understand the big picture |
| 2 | [02_Python_and_Technology_Basics.md](02_Python_and_Technology_Basics.md) | Every Python/tech concept the project uses | fill gaps before reading code |
| 3 | [03_File_by_File_Code_Explanation.md](03_File_by_File_Code_Explanation.md) | Every important file & function, with real code | understand the actual code |
| 4 | [04_Execution_Flow_and_Algorithms.md](04_Execution_Flow_and_Algorithms.md) | What happens when you click Analyze; the 4 key algorithms with worked examples | trace the program & the maths |
| 5 | [05_Installation_Testing_and_Troubleshooting.md](05_Installation_Testing_and_Troubleshooting.md) | Install, run, test, debug, fix errors | get it running yourself |
| 6 | [06_College_Viva_Preparation.md](06_College_Viva_Preparation.md) | 30s/2min/5min pitches, demo script, 50+ Q&A | prepare for the viva |
| 7 | [07_Glossary_and_Revision_Notes.md](07_Glossary_and_Revision_Notes.md) | Glossary, 1-page revision sheet, self-assessment | revise the night before |

**All-in-one PDF:** [Complete_Project_Explanation.pdf](Complete_Project_Explanation.pdf)
combines all seven chapters into one printable document with a title page, table
of contents, and page numbers.

---

## 🧭 Suggested paths

- **"I have my viva tomorrow":** Chapter 7 (revision) → Chapter 6 (Q&A) →
  skim Chapter 4 (be able to compute a match % by hand).
- **"I want to truly understand the code":** Chapters 1 → 2 → 3 → 4 in order.
- **"I just need to run it":** Chapter 5.

---

## ⚡ The project in one paragraph

ResumeIQ reads a **resume** and a **job description**, cleans both texts, finds
known **skills** in each using regular expressions, and compares them with Python
**set** operations (intersection = matched, difference = missing) to produce a
transparent **match score** and a list of missing skills. It is built with
**Python** and **Streamlit**, runs offline, uses no AI and no database, and every
number it shows can be explained from a documented formula. It ships with 31
passing automated tests.

> ⚠️ All scores are **rule-based, educational indicators** — not a prediction of
> hiring success and not a guarantee of ATS compatibility.

---

## 📌 Notes

- This guide was written from the **actual source code** in this repository
  (`app.py`, `analyzer.py`, `sample_data.py`, `tests/test_analyzer.py`).
- No secrets, passwords, or API keys appear anywhere (the project has none).
- If a code line number ever looks off after future edits, trust the **function
  name** — those are stable.
