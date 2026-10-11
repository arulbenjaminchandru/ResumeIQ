# ResumeIQ — Smart Resume Analyzer

## 📖 About this project (in simple words)

ResumeIQ is a small web app that reads a **resume** and a **job description**
and tells you how well they match.

It looks for important **skills** (like Python, SQL, Excel) in both texts, then
shows you:

- a **match score** (how many required skills the resume has),
- the skills that are **missing**, and
- simple **tips** to improve the resume.

It is built with **Python** and **Streamlit**, runs on your own computer, needs
no internet, and every score is explained — perfect for a student project.

> ⚠️ **Note:** The score is just a helpful guide for learning. It is **not** a
> real hiring decision and does not guarantee you will get a job.

---

## 🧰 What you need to install (just 2 things)

1. **Python** — the programming language that runs the app.
2. **VS Code** — a free program (a "code editor") where you open the project
   and press buttons to run it.

Follow the steps for **your** computer below. Do them **in order**. 🙂

---

## 🪟 PART A — Windows (step by step)

### Step 1 — Install Python

1. Open your web browser and go to **https://www.python.org/downloads/**
2. Click the big yellow button **"Download Python"**.
3. Open the file you just downloaded.
4. **VERY IMPORTANT:** On the first screen, tick the box at the bottom that says
   **"Add python.exe to PATH"** ✅ (this one step saves a lot of trouble).
5. Click **"Install Now"** and wait until it says *Setup was successful*. Click **Close**.

### Step 2 — Install VS Code

1. Go to **https://code.visualstudio.com/**
2. Click **"Download for Windows"**.
3. Open the downloaded file, keep clicking **Next** (accept the agreement), then
   **Install**, then **Finish**. VS Code will open.

### Step 3 — Open the project in VS Code

1. In VS Code, click the top menu **File → Open Folder…**
2. Find and select the **`Resume Analyzer`** folder, then click **Select Folder**.
3. If VS Code asks *"Do you trust the authors?"*, click **Yes, I trust the authors**.

### Step 4 — Open the Terminal (where you type commands)

1. In VS Code, click the top menu **Terminal → New Terminal**.
2. A box opens at the bottom. This is where you will type the commands below.

### Step 5 — Set up and run the app

Type each command below and press **Enter** after each one. (You can also copy
and paste them one at a time.)

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

✅ Your web browser will open automatically and show the app! If it doesn't,
open your browser and go to **http://localhost:8501**.

**To stop the app:** click the Terminal and press **Ctrl + C**.

---

## 🍎 PART B — macOS (step by step)

### Step 1 — Install Python

1. Open your browser and go to **https://www.python.org/downloads/**
2. Click the big button **"Download Python"**.
3. Open the downloaded `.pkg` file and keep clicking **Continue → Agree →
   Install**. Type your Mac password if asked. Click **Close** when done.

### Step 2 — Install VS Code

1. Go to **https://code.visualstudio.com/**
2. Click **"Download for macOS"**.
3. Open the downloaded file. Drag the **Visual Studio Code** icon into the
   **Applications** folder.
4. Open **Launchpad** (or Applications) and click **Visual Studio Code** to start it.

### Step 3 — Open the project in VS Code

1. In VS Code, click the top menu **File → Open Folder…**
2. Find and select the **`Resume Analyzer`** folder, then click **Open**.
3. If it asks whether you trust the folder, click **Yes, I trust the authors**.

### Step 4 — Open the Terminal

1. In VS Code, click the top menu **Terminal → New Terminal**.
2. A box opens at the bottom for typing commands.

### Step 5 — Set up and run the app

Type each command and press **Enter** after each one:

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

✅ Your browser will open the app automatically! If not, go to
**http://localhost:8501**.

**To stop the app:** click the Terminal and press **Control + C**.

---

## ▶️ Running it again next time

You only install things **once**. The next time, just:

1. Open the folder in VS Code.
2. Open a new Terminal.
3. Turn on the environment, then start the app:

| Windows | macOS |
|---------|-------|
| `venv\Scripts\activate` | `source venv/bin/activate` |
| `streamlit run app.py`  | `streamlit run app.py` |

---

## 🖱️ How to use the app

1. Click **🔍 Analyze Resume** in the left sidebar.
2. Give it a resume: **paste** it, **upload** a file (`.pdf`, `.docx`, `.txt`),
   or pick a ready-made **sample**.
3. Give it a job description the same way.
4. Click **🚀 Analyze**.
5. Look at the score, charts, and tips. You can **download a PDF report**.

Tip: Choose **"Load by role"** to fill in a matching sample resume **and** job
description instantly — great for a quick demo.

---

## ✅ Running the tests (optional)

To check everything works correctly, run this in the Terminal:

```bash
python -m unittest discover -s tests
```

You should see `Ran 31 tests ... OK`.

---

## 🛟 If something goes wrong

| Problem | What to do |
|---------|-----------|
| `python is not recognized` (Windows) | You missed ticking **"Add python.exe to PATH"**. Re-install Python and tick that box. |
| `pip is not recognized` | Make sure the environment is on: run `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac) first. |
| `streamlit: command not found` | Run `pip install -r requirements.txt` again (with the environment on). |
| The uploaded PDF looks empty | It may be a **scanned/photo** PDF (just a picture, no real text). Try a `.docx` or `.txt` instead. |
| Port 8501 is busy | Run `streamlit run app.py --server.port 8502` and open `http://localhost:8502`. |

---

## 📂 What's inside this project

| File | What it does |
|------|--------------|
| `app.py` | The app's screens and buttons (the part you see). |
| `analyzer.py` | The "brain" — all the matching and scoring logic. |
| `sample_data.py` | Ready-made sample resumes, jobs, and the list of skills. |
| `requirements.txt` | The list of tools Python needs to install. |
| `tests/test_analyzer.py` | Automatic checks that the brain works correctly. |
| `PROJECT_REPORT.md` | The full academic project report. |
| `VIVA_GUIDE.md` | Viva questions, answers, and a demo script. |

---

*ResumeIQ is an academic demonstration project. All scores are simple, rule-based
indicators for learning — always use your own judgement.*
