# Chapter 1 — Project Overview

> **How to read this chapter:** Start here. It explains *what* the project is,
> *why* it exists, and *how its pieces fit together*, all in plain English. You
> do not need to understand any code yet.

---

## 1.1 What is this project? (in one simple sentence)

**ResumeIQ** is a small website (that runs on your own computer) which reads a
**resume** and a **job description**, then tells you **how well they match** by
looking for important **skills** (like *Python*, *SQL*, *Excel*) in both.

That is the whole idea. Everything else in the code is just doing that job
carefully and showing the result nicely.

---

## 1.2 Important words, explained before we use them

| Word | Simple meaning |
|------|----------------|
| **Resume** | A document describing a person's skills, education and experience. |
| **Job description (JD)** | A document from a company listing what skills a job needs. |
| **Skill / keyword** | An important word we look for, e.g. `python`, `sql`, `aws`. |
| **Match** | A skill that appears in **both** the resume and the job description. |
| **Score** | A number (0 to 100) showing how many required skills the resume has. |
| **Streamlit** | A free Python tool that turns a Python script into a web page. |
| **Rule-based** | The program follows simple, fixed rules we wrote — it does **not** use AI. |
| **Embedded strings** | Example text (sample resumes, jobs, skills) written **directly inside the code**. |

> ⚠️ **"Embedded strings" does NOT mean AI "embeddings".** In this project it
> simply means *text typed directly into the Python files* using triple quotes
> (`""" ... """`). There is no machine learning anywhere in this project.

---

## 1.3 The real-world problem it solves

- **For a student / job seeker:** "Does my resume contain the skills this job is
  asking for? What am I missing?"
- **For a recruiter:** "Out of many resumes, which ones mention the required
  skills?" (a quick first filter).
- **For a teacher / examiner:** a clear, honest example of Python text
  processing that a student can fully explain.

Doing this by hand is slow and easy to get wrong. ResumeIQ does it in seconds
and **shows exactly why** it gave each number.

---

## 1.4 Who uses it?

Students, job seekers, recruiters (for a first pass only), and faculty
evaluating the mini-project. The web page is simple enough for someone with
**no programming knowledge** to use.

---

## 1.5 What it does NOT do (be honest in your viva!)

The code itself is honest about its limits, and you should be too:

- It **matches words**, it does **not understand meaning**. If a resume says
  *"built ML models"* but never writes *"machine learning"*, the tool may miss
  it. (This is called a **false negative**.)
- It **cannot** judge how *good* a candidate is, or their real experience level.
- It **cannot** guarantee it will pass a company's real ATS (Applicant Tracking
  System).
- It **never** guesses personal things like age, gender or religion.

This honesty is written directly in the code and on the "About & Limitations"
page of the app.

---

## 1.6 The technology used (and why)

| Technology | What it is | Why this project uses it |
|------------|-----------|--------------------------|
| **Python 3** | The programming language. | Easy to read; great at text handling. |
| **Streamlit** | Turns a Python file into a web app. | Build a web page with charts using only Python — no HTML/JavaScript. |
| **pandas** | Works with tables of data. | To show results as neat tables and make CSV files. |
| **Plotly** | Draws interactive charts. | For the gauges and bar charts. |
| **pypdf** | Reads text out of PDF files. | So users can upload a `.pdf` resume. |
| **python-docx** | Reads text out of Word files. | So users can upload a `.docx` resume. |
| **fpdf2** | Creates PDF files. | To let users download a PDF report. |
| **re** (built-in) | Python's "regular expressions". | To find emails, phones and skills by pattern. |
| **unittest** (built-in) | Python's testing tool. | To automatically check the logic is correct. |

**Built-in vs installed:** `re` and `unittest` come *with* Python — you do not
install them. The others (Streamlit, pandas, Plotly, pypdf, python-docx, fpdf2)
are **external packages** you install with `pip` (see Chapter 5).

---

## 1.7 The files in the project

This is the real folder layout (ignoring auto-generated caches and the
`venv/` virtual environment folder):

```
Resume Analyzer/
|
├── app.py                 <- The web page: buttons, charts, uploads (Streamlit)
├── analyzer.py            <- The "brain": all the analysis logic
├── sample_data.py         <- Embedded samples: resumes, jobs, and the skill list
├── requirements.txt       <- The list of packages to install
├── README.md              <- Beginner install & run guide
├── PROJECT_REPORT.md      <- The formal academic report
├── VIVA_GUIDE.md          <- A short viva guide (this learning guide is bigger)
├── .gitignore             <- Tells Git which files to ignore
│
├── tests/
│   └── test_analyzer.py   <- 31 automatic tests for analyzer.py
│
└── project_learning_guide/  <- (NEW) this beginner learning guide
    ├── README.md
    ├── 01_Project_Overview.md
    ├── 02_Python_and_Technology_Basics.md
    ├── 03_File_by_File_Code_Explanation.md
    ├── 04_Execution_Flow_and_Algorithms.md
    ├── 05_Installation_Testing_and_Troubleshooting.md
    ├── 06_College_Viva_Preparation.md
    ├── 07_Glossary_and_Revision_Notes.md
    └── Complete_Project_Explanation.pdf
```

### What each important file is responsible for

| File | Responsibility |
|------|----------------|
| `sample_data.py` | Stores the data: `SKILL_DATABASE` (skills by category), 5 sample resumes, 5 sample job descriptions. It has **no logic** — just data. |
| `analyzer.py` | The engine. Cleans text, finds skills, compares them with set maths, calculates scores, writes reports. It knows **nothing** about the web page, so it can be tested on its own. |
| `app.py` | The face of the app. Draws the pages, takes user input, calls `analyzer.py`, and shows the results as metrics, tables and charts. |
| `tests/test_analyzer.py` | Checks that `analyzer.py` behaves correctly for many situations (empty inputs, tricky skills like `c++`, etc.). |

---

## 1.8 The three-layer architecture (text diagram)

The project is built in **three layers**. Think of a restaurant:
the **waiter** (UI) takes your order, the **kitchen** (logic) cooks it, and the
**pantry** (data) stores the ingredients.

```
          ┌──────────────────────────────────────────────┐
          │                 app.py                        │
 USER  →  │   (Streamlit UI = the "waiter")               │
 (you) ←  │   pages, buttons, file upload, charts,        │
          │   download report / CSV                       │
          └───────────────┬───────────────────────────────┘
                          │ calls functions in
                          ▼
          ┌──────────────────────────────────────────────┐
          │                analyzer.py                    │
          │   (the "kitchen" = all the thinking)          │
          │   preprocess_text(), extract_skills(),        │
          │   calculate_keyword_match(),                  │
          │   calculate_readiness_score(),                │
          │   analyze_resume() ...                        │
          └───────────────┬───────────────────────────────┘
                          │ reads data from
                          ▼
          ┌──────────────────────────────────────────────┐
          │               sample_data.py                  │
          │   (the "pantry" = the ingredients)            │
          │   SKILL_DATABASE, SAMPLE_RESUMES,             │
          │   SAMPLE_JOB_DESCRIPTIONS                      │
          └──────────────────────────────────────────────┘

          ┌──────────────────────────────────────────────┐
          │           tests/test_analyzer.py              │
          │   imports and checks analyzer.py directly     │
          │   (does NOT need the web page to run)         │
          └──────────────────────────────────────────────┘
```

### Explaining each arrow

- **USER → app.py:** You type/paste/upload a resume and job description and
  click a button.
- **app.py → analyzer.py:** The web page hands the text to the engine by
  calling a function like `analyze_resume(resume_text, job_text)`.
- **analyzer.py → sample_data.py:** The engine reads the list of known skills
  (`SKILL_DATABASE`) to know what to look for.
- **analyzer.py → app.py:** The engine returns one big dictionary of results.
- **app.py → USER:** The page turns that dictionary into numbers, tables and
  charts you can see, plus downloadable files.
- **tests → analyzer.py:** The tests call the engine directly to confirm it is
  correct — they never open the web page.

**Why split into three layers?** So each part is simple and can be understood,
changed, and tested on its own. This is called **separation of concerns**, and
it is one of the strongest things you can say about this project in your viva.

---

## 1.9 A realistic example (what actually happens)

1. You open the app and choose the **"Python Developer"** sample (resume + job).
2. The resume mentions: `python, sql, flask, streamlit, pandas, git, docker`...
3. The job asks for: `python, sql, flask, streamlit, pandas, git, docker`...
4. The engine finds the skills in both, compares them, and reports:
   - **Keyword match: 100%** (every required skill is present)
   - **Missing skills: none**
   - A **Readiness score** out of 100 and a downloadable **PDF report**.
5. If instead you test the **Data Analyst** resume against the **Python
   Developer** job, the score is **lower**, because that resume is missing
   skills like `flask`, `streamlit`, `docker`. This visible difference is great
   for a demo.

*(These outcomes are produced by the real code; see Chapter 4 for the exact
step-by-step trace.)*

---

## 1.10 Checklist for this chapter

- [ ] I can say in one sentence what ResumeIQ does.
- [ ] I can explain "embedded strings" and why it is **not** AI.
- [ ] I can name the three layers (UI / logic / data) and the file for each.
- [ ] I can state two honest limitations of the tool.
- [ ] I can draw the three-layer diagram from memory.

➡️ **Next:** Chapter 2 teaches the Python ideas you need before reading the code.
