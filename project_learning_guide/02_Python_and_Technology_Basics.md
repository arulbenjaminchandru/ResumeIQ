# Chapter 2 — Python & Technology Basics (Prerequisites)

> **How to read this chapter:** These are the building blocks used in the
> project. Each topic has: a **simple definition**, a **real-world analogy**, a
> **tiny example**, a **line-by-line explanation**, **where it appears in our
> project**, and **why the project needs it**. Read them in order — each one
> builds on the last.
>
> We assume you already know: variables, numbers/strings/booleans, `if/else`,
> `for` loops, functions (basic), lists, and dictionaries. Everything below is
> treated as new.

**Learning order (easiest → hardest):**
1. Modules & imports → 2. Functions (params, return, defaults) →
3. Strings & string methods → 4. Lists & comprehensions → 5. Dictionaries (and
dictionary-of-lists) → 6. **Sets & set operations** → 7. f-strings →
8. Truthiness → 9. **Regular expressions** → 10. Exceptions (try/except) →
11. Files & bytes → 12. Classes (just enough for the tests) →
13. Streamlit → 14. pandas → 15. Plotly → 16. Virtual environments & pip.

---

## 2.1 Modules and imports

**Definition:** A **module** is just a Python file (e.g. `analyzer.py`).
**Importing** means "let me use the code written in another file".

**Analogy:** A module is a toolbox. `import` is you borrowing a specific tool
from it instead of making your own.

**Tiny example:**
```python
import re                       # borrow Python's regular-expression toolbox
from sample_data import SKILL_DATABASE   # borrow ONE thing from our own file
```
- Line 1: load the whole `re` module; use it as `re.something()`.
- Line 2: reach into `sample_data.py` and take just the `SKILL_DATABASE`
  variable, so we can write `SKILL_DATABASE` directly.

**Where in our project:** top of `analyzer.py` (lines 34–37) and top of
`app.py` (it imports `analyzer` and several items from `sample_data`).

**Why needed:** It lets the three layers (UI, logic, data) live in separate
files but still work together.

---

## 2.2 Functions — parameters, return values, and defaults

**Definition:** A **function** is a named block of code that takes **inputs**
(parameters), does something, and usually gives back an **output** (`return`).
A **default value** lets a parameter be optional.

**Analogy:** A coffee machine. You put in inputs (water, beans), press start,
and it returns coffee. A default is "if you don't choose a size, you get medium".

**Tiny example:**
```python
def greet(name, greeting="Hello"):
    return greeting + ", " + name + "!"

print(greet("Arul"))            # Hello, Arul!
print(greet("Arul", "Welcome")) # Welcome, Arul!
```
- `name` is required; `greeting="Hello"` is **optional** (has a default).
- `return` hands the finished string back to whoever called `greet`.

**Where in our project:** everywhere. For example `extract_skills(text,
skill_database=SKILL_DATABASE)` in `analyzer.py` (line 140) — `skill_database`
has a **default**, so you can call `extract_skills(text)` and it automatically
uses the project's skill list.

**Why needed:** Functions let us name each step (`preprocess_text`,
`calculate_keyword_match`) and reuse it without copying code.

---

## 2.3 Strings and string methods

**Definition:** A **string** is text. A **method** is a function attached to a
value, called with a dot: `text.lower()`.

**Analogy:** If a string is a sentence written on paper, methods are actions you
can do to it: make it lowercase, cut it into words, trim the edges.

**The string methods this project uses the most:**
```python
s = "  Hello WORLD\nPython  "
s.lower()        # '  hello world\npython  '   (make lowercase)
s.strip()        # 'Hello WORLD\nPython'       (remove edge whitespace)
s.split()        # ['Hello', 'WORLD', 'Python'] (cut into words on whitespace)
s.splitlines()   # ['  Hello WORLD', 'Python  '] (cut into lines)
```
- `.lower()` → used so `"Python"` and `"python"` are treated the same.
- `.split()` → with no argument, splits on **any** whitespace and drops blanks;
  used to **count words**.
- `.splitlines()` → breaks text into lines; used to **count non-empty lines**.

**Where in our project:** `preprocess_text()` (`analyzer.py` line 44) uses
`.lower()`; `count_resume_statistics()` (line 195) uses `.split()` and
`.splitlines()`.

**Why needed:** The whole project is about processing text, so these are the
core tools.

---

## 2.4 Lists and list comprehensions

**Definition:** A **list** is an ordered collection in square brackets:
`[1, 2, 3]`. A **list comprehension** is a short way to build a new list with a
loop inside brackets.

**Analogy:** A list is a shopping list. A comprehension is "write down every
fruit from the basket that is ripe" — in one line.

**Tiny example:**
```python
numbers = [1, 2, 3, 4]
evens = [n for n in numbers if n % 2 == 0]   # [2, 4]
```
Read it as: *"collect `n`, for each `n` in numbers, if `n` is even."*

**Where in our project:** `count_resume_statistics()` line 216:
```python
line_count = len([ln for ln in text.splitlines() if ln.strip()])
```
This builds a list of only the **non-empty** lines, then `len(...)` counts them.

**Why needed:** Comprehensions make the code short and readable when filtering
or transforming lists.

---

## 2.5 Dictionaries and the "dictionary of lists"

**Definition:** A **dictionary** stores `key: value` pairs in curly braces:
`{"name": "Arul"}`. A **dictionary of lists** has lists as its values.

**Analogy:** A dictionary is a real dictionary — you look up a *word* (key) to
get its *meaning* (value). A dictionary of lists is like a filing cabinet:
each labelled drawer (key) holds many papers (a list).

**Tiny example (exactly the shape our project uses):**
```python
skills = {
    "Programming Languages": ["python", "java", "c++"],
    "Databases": ["sql", "mysql"],
}
skills["Databases"]          # ['sql', 'mysql']
for category, items in skills.items():   # loop over key AND value together
    print(category, "has", len(items), "skills")
```
- `skills["Databases"]` looks up one drawer.
- `.items()` gives you both the key and the value each loop — used constantly.

**Where in our project:** `SKILL_DATABASE` in `sample_data.py` is a dictionary
of lists (10 categories, each a list of skill words). `extract_skills()` loops
over it with `for category, skills in skill_database.items():` (line 160).

**Why needed:** It keeps skills **organised by category**, which is used for the
category-coverage chart and the skill-gap table.

---

## 2.6 Sets and set operations ⭐ (the heart of the scoring)

**Definition:** A **set** is an **unordered** collection with **no duplicates**,
written with curly braces: `{1, 2, 3}`. Sets support **maths operations**:
- **intersection** (`&` or `.intersection()`) → items in **both** sets.
- **difference** (`-` or `.difference()`) → items in the first but **not** the
  second.

**Analogy:** Two circles overlapping (a Venn diagram). The overlap is the
intersection; the part of circle A outside B is the difference A − B.

**Tiny example:**
```python
resume = {"python", "sql", "git"}
job    = {"python", "sql", "docker", "aws"}

matched = resume.intersection(job)   # {'python', 'sql'}   -> in BOTH
missing = job.difference(resume)     # {'docker', 'aws'}   -> job needs, resume lacks
extra   = resume.difference(job)     # {'git'}             -> bonus skills
```

**Where in our project:** `calculate_keyword_match()` (`analyzer.py` lines
392–394) — this is **exactly** how the match is computed:
```python
matched = resume_skills.intersection(job_skills)
missing = job_skills.difference(resume_skills)
extra   = resume_skills.difference(job_skills)
```

**Why needed:** Sets make the comparison **fast**, **duplicate-free**, and
**easy to explain** ("matched = overlap; missing = what the job has that the
resume doesn't"). This is the single most important concept to master for the
viva.

---

## 2.7 f-strings (formatted strings)

**Definition:** An **f-string** lets you drop variables straight into text by
putting an `f` before the quotes and `{variable}` inside.

**Tiny example:**
```python
count = 5
print(f"You matched {count} skills.")   # You matched 5 skills.
```

**Where in our project:** everywhere a message or report line is built, e.g.
`f"Matched {km['matched_count']} of {km['total_job_keywords']} ..."`
(`analyzer.py` line 688).

**Why needed:** Clean, readable way to build the report text and UI messages.

---

## 2.8 Truthiness (empty things are "False")

**Definition:** In an `if`, Python treats some values as False even though they
are not literally `False`: empty string `""`, empty list `[]`, `0`, and `None`
are all "falsy". Non-empty values are "truthy".

**Tiny example:**
```python
text = ""
if not text:
    print("the text is empty")   # this runs
```

**Where in our project:** `preprocess_text()` line 62 `if not text or not
isinstance(text, str): return ""` — safely handles empty or non-text input.
Also `", ".join(km["missing"]) or "None"` shows the word `"None"` when the list
is empty.

**Why needed:** It guards against empty inputs so the app never crashes.

---

## 2.9 Regular expressions (the `re` module) ⭐

**Definition:** A **regular expression** (regex) is a mini-language for
describing **patterns** in text, so you can find things like "an email" or "a
whole word". Python's `re` module runs them.

**Analogy:** A very smart "Find" box. Instead of searching for one exact word,
you search for a *shape*, e.g. "some letters, then `@`, then more letters, then
a dot".

**The regex pieces used in this project:**

| Piece | Meaning | Example |
|-------|---------|---------|
| `\d` | any digit 0–9 | `\d\d` matches `42` |
| `\s` | any whitespace | spaces, tabs, newlines |
| `[...]` | any one character from a set | `[a-z]` = one lowercase letter |
| `[^...]` | any character **not** in the set | `[^a-z]` = not a lowercase letter |
| `+` | "one or more of the previous" | `\d+` = one or more digits |
| `\b` | a **word boundary** (edge of a word) | `\bcat\b` matches `cat` but not `category` |
| `(?<!x)` | **negative look-behind**: "not preceded by x" | used for `c++` |
| `(?!x)` | **negative look-ahead**: "not followed by x" | used for `c++` |

**Tiny example:**
```python
import re
re.findall(r"\d+", "I have 3 cats and 12 fish")   # ['3', '12']  (all digit runs)
re.sub(r"[^a-z ]", " ", "Hi, THERE!")             # 'hi there '   (depends on lowercase)
re.search(r"\bpython\b", "i love python")         # a match object (found!)
```
- `findall` → return **all** matches as a list.
- `sub` → **substitute** (replace) matches with something else.
- `search` → find the **first** match (or `None`).

**Where in our project:**
- `preprocess_text()` uses `re.sub` to clean text (lines 71, 75).
- Contact detection uses compiled patterns for email/phone/LinkedIn
  (`analyzer.py` lines 246–250).
- Skill matching uses `\b` for normal skills and look-arounds for `c++`/`c#`
  (`_build_skill_pattern`, lines 106–129).

**Why needed:** Regex is how the project finds emails, phone numbers, and
whole-word skills safely (so `r` doesn't match inside `react`).

---

## 2.10 Exception handling (try / except)

**Definition:** Code can fail (e.g. a broken file). `try` runs risky code;
`except` catches the error so the program keeps going instead of crashing.
`raise` deliberately creates an error with a clear message.

**Analogy:** A safety net under a trapeze artist. If they fall (error), the net
catches them (except) instead of disaster (crash).

**Tiny example:**
```python
try:
    number = int("hello")      # this fails
except ValueError:
    number = 0                 # we handle it calmly
print(number)                  # 0
```

**Where in our project:**
- `extract_text_from_file()` wraps PDF/DOCX reading in `try/except` and
  `raise ValueError("friendly message")` on failure (`analyzer.py` 941–966).
- `analyze_multiple_resumes()` wraps each resume in `try/except` so one bad file
  does not stop the whole batch (lines 874–895).
- In `app.py`, the Report tab wraps PDF creation in `try/except` to show a
  friendly error.

**Why needed:** Real users upload messy files. Exception handling keeps the app
stable and the messages friendly.

---

## 2.11 Files and bytes (reading an uploaded file)

**Definition:** Computers store files as **bytes** (raw numbers). Text must be
**decoded** from bytes using an encoding like UTF-8. A **file-like object** is
anything you can call `.read()` on.

**Analogy:** Bytes are a sealed parcel; `.decode("utf-8")` is opening it to read
the letter inside.

**Tiny example:**
```python
raw = b"Hello"            # bytes (note the b)
text = raw.decode("utf-8") # 'Hello' (a normal string)
```

**Where in our project:** `extract_text_from_file()` (`analyzer.py` 903–970)
reads the uploaded file's bytes with `uploaded_file.read()`, then decodes `.txt`
directly, or uses `pypdf` / `python-docx` for `.pdf` / `.docx`.

**Why needed:** Uploaded resumes arrive as bytes; we must turn them into text
before we can analyse them.

---

## 2.12 Classes and objects (just enough for the tests)

**Definition:** A **class** is a blueprint; an **object** is a thing built from
it. A **method** is a function that belongs to the object.

**Analogy:** A class is the blueprint for a car; each actual car is an object.

**Where in our project:** We barely use classes in the main code (it is mostly
simple functions — a deliberate, beginner-friendly choice). Classes appear in
**two places**:
1. The tests: `class TestKeywordMatch(unittest.TestCase):` — each test is a
   method inside a class that inherits from `unittest.TestCase`.
2. The PDF report briefly uses `FPDF()` (an object from the fpdf2 library).

**Why needed:** `unittest` organises tests into classes. You only need to
recognise the pattern, not write complex classes yourself.

---

## 2.13 Streamlit (turning Python into a web page)

**Definition:** **Streamlit** runs your Python script top-to-bottom and turns
each `st.something(...)` call into a piece of a web page.

**Key idea — "rerun":** Every time you click a button or change a box, Streamlit
**runs the whole script again** from the top. To remember things between reruns
it uses **`st.session_state`** (a dictionary that survives reruns).

**Analogy:** Streamlit is like a whiteboard that gets wiped and redrawn every
time you interact. `st.session_state` is a sticky note that stays on the board.

**The Streamlit tools this project uses:**

| Call | What it draws / does |
|------|----------------------|
| `st.set_page_config(...)` | Sets the browser tab title and layout (must be first). |
| `st.sidebar.radio(...)` | The left-hand menu to switch pages. |
| `st.text_area(...)` | The big box to paste a resume. |
| `st.file_uploader(...)` | The upload button for `.pdf/.docx/.txt`. |
| `st.button(...)` | A clickable button (e.g. "Analyze"). |
| `st.metric(...)` | A big number card (e.g. "Match 100%"). |
| `st.tabs([...])` | The result tabs (Overview, Skills, ...). |
| `st.dataframe(...)` | Shows a pandas table. |
| `st.plotly_chart(...)` | Shows a Plotly chart. |
| `st.download_button(...)` | Lets the user download the PDF/CSV. |
| `st.session_state` | Remembers the resume text and results across reruns. |

**Where in our project:** all of `app.py`.

**Why needed:** It gives a clean, interactive web page using only Python — no
need to learn HTML, CSS or JavaScript. (See Chapter 3 for a deeper look at the
rerun/`session_state` rule, which caused and fixed a real bug in this project.)

---

## 2.14 pandas (tables of data)

**Definition:** **pandas** gives a `DataFrame`, which is a table (rows and
columns) you can display and export.

**Tiny example:**
```python
import pandas as pd
df = pd.DataFrame([{"Skill": "python", "In Resume": True}])
csv_text = df.to_csv(index=False)   # turn the table into CSV text
```

**Where in our project:** `app.py` builds `DataFrame`s for the skill-gap table,
the comparison table, and the batch results, and calls `.to_csv(...)` to make
the downloadable CSV.

**Why needed:** Easy, neat tables and one-line CSV export.

---

## 2.15 Plotly (charts)

**Definition:** **Plotly** draws interactive charts (you can hover over them).

**Where in our project:** `gauge_chart`, `matched_missing_bar`,
`category_coverage_chart` in `app.py` (lines 51–113) build Plotly figures that
`st.plotly_chart` then displays.

**Why needed:** Charts make the match result and skill gaps easy to *see*, not
just read.

---

## 2.16 Virtual environments & pip (setting up)

**Definition:** **pip** installs external packages. A **virtual environment**
(`venv`) is a private box of packages for **this project only**, so it does not
clash with other projects.

**Analogy:** A separate pencil case for each subject, so your maths pens don't
mix with your art pens.

**The commands (full details in Chapter 5):**
```bash
python -m venv venv        # create the private box
venv\Scripts\activate      # (Windows) step into the box
pip install -r requirements.txt   # install the project's packages
```

**Why needed:** It guarantees the exact packages the project needs are present,
without breaking anything else on the computer.

---

## 2.17 Checklist for this chapter

- [ ] I can explain a dictionary-of-lists using `SKILL_DATABASE`.
- [ ] I can compute `intersection` and `difference` by hand on two small sets.
- [ ] I know what `\b` does and why `r` won't match inside `react`.
- [ ] I can read a list comprehension out loud.
- [ ] I know why Streamlit "reruns" and what `st.session_state` is for.
- [ ] I can explain `try/except` with the uploaded-file example.

➡️ **Next:** Chapter 3 walks through every important file and function, using
the real code.
