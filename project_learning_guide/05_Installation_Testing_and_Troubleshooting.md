# Chapter 5 — Installation, Testing & Troubleshooting

> **How to read this chapter:** Follow it top to bottom the first time. It gets
> the project running, shows how to test it, and lists fixes for common
> problems. Commands are given for **Windows** and **macOS/Linux**.

---

## 5.1 Prerequisites

| You need | Why | How to check |
|----------|-----|--------------|
| **Python 3.11 or newer** | to run the code | `python --version` |
| **pip** | to install packages (comes with Python) | `pip --version` |
| A web browser | to view the app | already on your computer |
| (Recommended) **VS Code** | a friendly code editor | see the project's main `README.md` |

> **Verified:** this project was developed and its tests were run successfully on
> **Python 3.14.6** on Windows. Any Python 3.11+ should work.

---

## 5.2 Step-by-step setup

Open a terminal **inside the project folder** (`Resume Analyzer/`).

### Windows (PowerShell)
```bash
python -m venv venv
```
```bash
venv\Scripts\activate
```
```bash
pip install -r requirements.txt
```
```bash
streamlit run app.py
```

### macOS / Linux
```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```
```bash
pip install -r requirements.txt
```
```bash
streamlit run app.py
```

**What each command does:**
1. `python -m venv venv` → creates a private package box named `venv/`.
2. `activate` → steps into that box (your prompt shows `(venv)`).
3. `pip install -r requirements.txt` → installs the 6 packages the project needs
   (streamlit, pandas, plotly, pypdf, python-docx, fpdf2).
4. `streamlit run app.py` → starts the app.

---

## 5.3 What you should see when it works

- The terminal prints something like:
  ```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  ```
- Your browser opens automatically to that address and shows **ResumeIQ** with a
  sidebar on the left.
- If the browser does not open by itself, open it and visit
  **http://localhost:8501** manually.

> **Honesty note:** these are the *expected* messages. Always confirm on your own
> machine — do not assume success without seeing the app in the browser.

---

## 5.4 Configuration & environment variables

**There are none.** This project has **no API keys, no passwords, no database
connection strings, and no `.env` file**. Nothing secret is stored or needed.
That is a genuine strength: there is nothing to leak and nothing to configure.
Everything it needs (sample data, the skill list) is embedded in `sample_data.py`.

---

## 5.5 Trying the main feature (manual test)

1. In the sidebar, click **🔍 Analyze Resume**.
2. For the job description method, choose **Load by role** and pick
   **Python Developer**, then click **Load resume + job for this role**.
3. Click **🚀 Analyze**.
4. You should see **Keyword Match ≈ 100%** and a high **Readiness Score**.
5. Open the **Raw vs Clean** tab to watch preprocessing in action.
6. Open the **Report** tab and click **Download PDF**.

**To see a lower, different score (good for demos):** load the **Data Analyst**
sample resume but keep the **Python Developer** job description, then Analyze —
the score drops because skills like `flask`, `streamlit`, `docker` are missing.

---

## 5.6 Running the automated tests

From the project folder (with the virtual environment active):

```bash
python -m unittest discover -s tests
```

**Expected output (last lines):**
```
Ran 31 tests in 0.8s
OK
```

> **Verified result:** when these documents were prepared, the command above was
> run and reported **`Ran 31 tests ... OK`** (all 31 passed) on Python 3.14.6.
> Re-run it on your machine and capture a screenshot for your report.

**Run a single test class** (handy when demonstrating one idea):
```bash
python -m unittest tests.test_analyzer.TestSkillMatching
```

### What the tests check (grouped)
| Test group | Proves |
|------------|--------|
| `TestPreprocessing` | lowercasing, trimming, keeping `c++`/`node.js`, handling `None`. |
| `TestSkillMatching` | `c++`/`c#`/`.net`/`node.js` match; `r` matches only as a word; duplicates counted once. |
| `TestKeywordMatch` | good match >50%; no-match = 0%; empty resume/JD safe; missing list correct. |
| `TestContactDetection` | multiple emails; missing contact; phone found. |
| `TestSections` | alternate headings map to canonical sections. |
| `TestStatistics` | empty text safe; blank lines ignored; whitespace flag. |
| `TestReadinessScore` | score always 0–100; weights sum to 100; empty inputs safe. |
| `TestComparisonAndBatch` | comparison ordering; batch survives a bad item; `max_files` respected. |
| `TestReport` | Markdown report has the scores; PDF starts with `%PDF`. |

---

## 5.7 Stopping the app

- Click the terminal, then press **Ctrl + C** (Windows/Linux) or
  **Control + C** (macOS). The server stops.
- To leave the virtual environment later, type `deactivate`.

---

## 5.8 Troubleshooting (common errors & fixes)

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `python is not recognized` (Windows) | Python not on PATH | Reinstall Python and tick **"Add python.exe to PATH"**. |
| `pip is not recognized` | virtual env not active | Run `venv\Scripts\activate` (Win) or `source venv/bin/activate` (Mac) first. |
| `streamlit: command not found` | packages not installed | Re-run `pip install -r requirements.txt` with the env active. |
| `ModuleNotFoundError: No module named 'fpdf'` | fpdf2 missing | `pip install fpdf2` (or reinstall requirements). |
| Uploaded PDF box is empty / "No selectable text" | scanned/image-only PDF | Use a `.docx` or `.txt`, or a text-based PDF (OCR is out of scope). |
| Port 8501 already in use | another app is running on it | `streamlit run app.py --server.port 8502` then open `localhost:8502`. |
| Charts do not appear | Plotly not installed or stale browser | reinstall requirements; refresh the page. |
| App shows "Please provide resume text" | input box empty | paste/upload/load a sample before clicking Analyze. |

---

## 5.9 How to debug (for a beginner)

1. **Read the red error box** in the app or the **traceback** in the terminal —
   the **last line** names the error type and message.
2. **Find the file and line number** in the traceback; open that spot.
3. **Add a temporary `print(...)`** just before the failing line to see the
   values (e.g. `print("resume words:", len(resume_text.split()))`).
4. **Re-run** and read the printed value — it usually reveals the problem (often
   an empty or unexpected input).
5. Remove the `print` once fixed.
6. For logic questions, **run the tests** — a failing test points straight at the
   function that misbehaves.

---

## 5.10 Edge cases that matter (and are handled)

- **Empty resume or empty job description** → scores become 0, no crash.
- **Job description with no recognised skills** → `total = 0`, match % = 0 (the
  `if total > 0` guard prevents divide-by-zero).
- **Tricky skills** `c++`, `c#`, `.net`, `node.js`, `ci/cd` → matched correctly.
- **Single-letter skill `r`** → not matched inside `react`/`year`.
- **A broken file in a batch** → caught; that row shows an error, the rest
  continue.

---

## 5.11 Known limitations (be honest in the viva)

- **Keyword matching, not meaning:** misses synonyms/paraphrases (false
  negatives).
- **Cannot judge real skill level** or seniority.
- **No ATS guarantee.**
- **Contact/section detection is pattern-based** and can misfire.
- **No OCR:** scanned/image PDFs are not supported.
- **Privacy:** files are processed in memory and not stored, but the batch table
  (by your request) shows the uploaded **file names**, which may contain personal
  names — mention this if asked.

---

## 5.12 Checklist for this chapter

- [ ] I can set up and run the app from scratch on my OS.
- [ ] I know there are no secrets/config to worry about.
- [ ] I can run the tests and read the `OK` / failure output.
- [ ] I can stop the app and deactivate the environment.
- [ ] I can fix the three most common errors without help.

➡️ **Next:** Chapter 6 is full viva preparation — explanations at three lengths,
a demo script, and 50+ questions with answers.
