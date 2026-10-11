"""
analyzer.py
===========

The ANALYSIS ENGINE of the Resume Analyzer.

This module contains all of the reusable logic (text preprocessing, keyword
matching, scoring, section detection, recommendations). It deliberately knows
NOTHING about Streamlit, so it can be imported and unit-tested on its own.

Core idea of the whole project
------------------------------
A resume and a job description are just TEXT. By applying simple, transparent
Python string-processing techniques (lowercasing, cleaning, regular
expressions, set operations) we can:
  * find skills in each document,
  * compare the two sets of skills,
  * and produce an explainable match score.

IMPORTANT (academic honesty): this is RULE-BASED KEYWORD MATCHING. It does not
"understand" the resume. Every number it produces is an educational, heuristic
indicator - never a prediction of hiring success or a guarantee of ATS
(Applicant Tracking System) compatibility.

Python concepts demonstrated
----------------------------
  * String methods (.lower(), .split(), .strip())
  * Regular expressions (the `re` module)
  * Sets and set operations (intersection, difference)
  * Dictionaries and lists
  * Functions, loops and conditionals
"""

import io
import re

from sample_data import SKILL_DATABASE


# ===========================================================================
# 1. TEXT PREPROCESSING
# ===========================================================================

def preprocess_text(text):
    """Clean raw resume / job-description text so it is easy to match.

    What it does (each step is kept deliberately simple):
      1. Handle a non-string / None input safely.
      2. Convert everything to lowercase (so "Python" == "python").
      3. Normalise line breaks and collapse repeated whitespace.
      4. Replace "noise" punctuation (commas, brackets, pipes, etc.) with a
         space, BUT keep the characters that matter for technology names:
         +  #  .  /  -   so that terms like c++, c#, .net, node.js and ci/cd
         survive intact.

    Input : text (str)  - the raw text.
    Output: (str)       - cleaned, lowercased, single-spaced text.

    Why it is needed: matching "Python," or "PYTHON" or "python" should all
    succeed. Cleaning the text first makes later matching reliable.
    """
    if not text or not isinstance(text, str):
        return ""

    # Step 1: lowercase.
    text = text.lower()

    # Step 2: turn any character that is NOT a letter, digit, whitespace or an
    # important tech symbol (+ # . / -) into a single space. Everything else
    # (commas, parentheses, pipes, colons, ...) becomes a separator.
    text = re.sub(r"[^a-z0-9+#./\-\s]", " ", text)

    # Step 3: collapse all runs of whitespace (spaces, tabs, newlines) into a
    # single space and trim the ends.
    text = re.sub(r"\s+", " ", text).strip()

    return text


def tokenize(text):
    """Split cleaned text into a list of word tokens.

    Input : text (str) - ideally already preprocessed.
    Output: list[str]  - individual tokens.

    Demonstrates the simplest possible tokenizer: Python's str.split().
    """
    return preprocess_text(text).split()


# ===========================================================================
# 2. SKILL MATCHING (the shared matching helper used everywhere)
# ===========================================================================
#
# The trickiest part of keyword matching is avoiding WRONG matches:
#   * the skill "r" must NOT match the "r" inside "react" or "year".
#   * the skill "c++" must match "c++" but not "c" or "c+++".
#
# We solve this with carefully built regular expressions and cache them so we
# only compile each pattern once.

_SPECIAL_SKILL_CHARS = set("+#./-")
_skill_pattern_cache = {}


def _build_skill_pattern(skill):
    """Build (and cache) a compiled regex that matches a single skill safely.

    * Plain skills (letters/digits only, e.g. "python", "r", "machine
      learning") use \\b word boundaries. \\b already prevents "r" from
      matching inside "react".
    * Skills containing special symbols (c++, c#, .net, node.js, ci/cd,
      scikit-learn) cannot use \\b (because + # . are not "word"
      characters), so we use custom look-around boundaries that forbid an
      adjacent letter, digit, + or #.
    """
    if skill in _skill_pattern_cache:
        return _skill_pattern_cache[skill]

    escaped = re.escape(skill)
    if any(ch in _SPECIAL_SKILL_CHARS for ch in skill):
        boundary = r"[a-z0-9+#]"
        pattern = r"(?<!{b}){s}(?!{b})".format(b=boundary, s=escaped)
    else:
        pattern = r"\b{s}\b".format(s=escaped)

    compiled = re.compile(pattern, re.IGNORECASE)
    _skill_pattern_cache[skill] = compiled
    return compiled


def skill_in_text(skill, cleaned_text):
    """Return True if `skill` appears as a whole token in `cleaned_text`.

    `cleaned_text` must already be preprocessed (lowercased, cleaned).
    """
    return bool(_build_skill_pattern(skill.lower()).search(cleaned_text))


def extract_skills(text, skill_database=SKILL_DATABASE):
    """Find every known skill that appears in the given text.

    Input :
        text (str)          - raw resume or job-description text.
        skill_database      - dict {category: [skills]} (defaults to the
                              embedded SKILL_DATABASE).
    Output:
        dict {category: [found_skills]} - only categories with at least one
        match are returned, and duplicate skills are removed automatically.

    Processing steps:
        1. Preprocess the text once.
        2. For every category, test each skill with skill_in_text().
        3. Collect the matches per category.

    Python concept: dictionary-of-lists building + case-insensitive matching.
    """
    cleaned = preprocess_text(text)
    found = {}
    for category, skills in skill_database.items():
        matches = []
        for skill in skills:
            if skill_in_text(skill, cleaned) and skill not in matches:
                matches.append(skill)
        if matches:
            found[category] = matches
    return found


def flatten_skills(skills_by_category):
    """Turn a {category: [skills]} dict into a single set of skills.

    Using a SET removes duplicates and makes comparisons (intersection /
    difference) easy and fast.
    """
    flat = set()
    for skills in skills_by_category.values():
        flat.update(skills)
    return flat


def skill_category_lookup(skill_database=SKILL_DATABASE):
    """Return a reverse map {skill: category} for building reports/tables."""
    lookup = {}
    for category, skills in skill_database.items():
        for skill in skills:
            lookup.setdefault(skill, category)
    return lookup


# ===========================================================================
# 3. RESUME STATISTICS
# ===========================================================================

def count_resume_statistics(text):
    """Compute basic readability statistics from the RAW resume text.

    Output dict keys:
        word_count        - number of whitespace-separated words.
        character_count   - total characters (including spaces).
        line_count        - number of non-empty lines.
        sentence_count    - approximate, counted by . ! ? terminators.
        average_word_length - mean word length, rounded to 2 decimals.

    How each value is calculated is intentionally explicit so a student can
    explain it line by line.
    """
    text = text or ""

    words = text.split()                       # split on any whitespace
    word_count = len(words)

    character_count = len(text)

    # A "non-empty line" is a line that still has content after stripping.
    line_count = len([ln for ln in text.splitlines() if ln.strip()])

    # Approximate sentence count: how many . ! ? groups appear.
    sentence_count = len(re.findall(r"[.!?]+", text))
    if sentence_count == 0 and word_count > 0:
        sentence_count = 1

    if word_count > 0:
        average_word_length = round(
            sum(len(w) for w in words) / word_count, 2
        )
    else:
        average_word_length = 0.0

    return {
        "word_count": word_count,
        "character_count": character_count,
        "line_count": line_count,
        "sentence_count": sentence_count,
        "average_word_length": average_word_length,
    }


# ===========================================================================
# 4. CONTACT INFORMATION DETECTION
# ===========================================================================

# Regular expressions used for detection. They are PATTERN-BASED, so they may
# produce occasional false positives or miss unusual formats - this is stated
# clearly to the user.
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(r"\+?\d[\d\s().\-]{8,}\d")
_LINKEDIN_RE = re.compile(r"linkedin\.com/[A-Za-z0-9_\-/]+", re.IGNORECASE)
_GITHUB_RE = re.compile(r"github\.com/[A-Za-z0-9_\-/]+", re.IGNORECASE)
_URL_RE = re.compile(r"\b(?:https?://)?[A-Za-z0-9\-]+\.[A-Za-z]{2,}(?:/\S*)?")


def detect_contact_information(text):
    """Detect contact details using simple regular expressions.

    Output dict:
        email     -> {"found": bool, "count": int}
        phone     -> {"found": bool, "count": int}
        linkedin  -> {"found": bool}
        github    -> {"found": bool}
        portfolio -> {"found": bool}
        emails    -> list of the raw matched e-mail strings (used internally;
                     the UI deliberately does NOT display personal details).

    Note: detection is pattern-based. It can miss unusual formats and may
    occasionally flag something that only looks like a phone number.
    """
    text = text or ""

    emails = _EMAIL_RE.findall(text)

    # For phones, keep only candidates that contain a sensible number of digits
    # (10 to 15) so random long digit runs are less likely to be counted.
    phone_candidates = _PHONE_RE.findall(text)
    phones = []
    for cand in phone_candidates:
        digits = re.sub(r"\D", "", cand)
        if 10 <= len(digits) <= 15:
            phones.append(cand.strip())

    linkedin = bool(_LINKEDIN_RE.search(text))
    github = bool(_GITHUB_RE.search(text))

    # "Portfolio": any website-looking URL that is not linkedin / github / an
    # e-mail domain. This is a heuristic.
    portfolio = False
    for match in _URL_RE.findall(text):
        low = match.lower()
        if "linkedin.com" in low or "github.com" in low:
            continue
        if "@" in match:
            continue
        # Ignore plain e-mail domains already captured above.
        portfolio = True
        break

    return {
        "email": {"found": len(emails) > 0, "count": len(emails)},
        "phone": {"found": len(phones) > 0, "count": len(phones)},
        "linkedin": {"found": linkedin},
        "github": {"found": github},
        "portfolio": {"found": portfolio},
        "emails": emails,
    }


# ===========================================================================
# 5. SECTION DETECTION
# ===========================================================================

# Canonical section -> list of heading variants / alternative wordings.
SECTION_KEYWORDS = {
    "Professional Summary": ["professional summary", "summary", "profile", "about me"],
    "Career Objective": ["career objective", "objective"],
    "Education": ["education", "academic", "academics", "qualification", "qualifications"],
    "Work Experience": [
        "work experience", "professional experience", "experience",
        "employment history", "employment", "work history",
    ],
    "Technical Skills": ["technical skills", "skills", "core competencies", "skill set"],
    "Projects": ["projects", "academic projects", "personal projects"],
    "Certifications": ["certifications", "certification", "certificate", "certificates"],
    "Achievements": ["achievements", "accomplishments", "awards"],
    "Publications": ["publications", "publication", "papers"],
    "Internships": ["internships", "internship"],
}


def detect_resume_sections(text):
    """Detect which common resume sections appear to be present.

    Output dict:
        detected -> {canonical_section: bool}
        present  -> [sections that were found]
        missing  -> [sections that were NOT found - described as POSSIBLY
                    missing, because the resume might use an unfamiliar heading]

    Matching is case-insensitive and allows for common alternative headings.
    """
    cleaned = preprocess_text(text)
    detected = {}
    for section, variants in SECTION_KEYWORDS.items():
        found = False
        for variant in variants:
            # \b boundaries keep "skills" from matching inside another word.
            if re.search(r"\b" + re.escape(variant) + r"\b", cleaned):
                found = True
                break
        detected[section] = found

    present = [s for s, ok in detected.items() if ok]
    missing = [s for s, ok in detected.items() if not ok]
    return {"detected": detected, "present": present, "missing": missing}


# ===========================================================================
# 6. JOB-DESCRIPTION KEYWORDS + KEYWORD MATCHING
# ===========================================================================

def extract_job_keywords(job_description, skill_database=SKILL_DATABASE):
    """Return the set of recognised skills mentioned in a job description.

    We treat the known skills from SKILL_DATABASE as the "important keywords".
    This keeps matching meaningful (we compare like-for-like skills) and avoids
    noise from ordinary English words.

    Output: a set() of skill strings.
    """
    return flatten_skills(extract_skills(job_description, skill_database))


def calculate_keyword_match(resume_text, job_description,
                            skill_database=SKILL_DATABASE):
    """Compare resume skills against job-description skills using SET logic.

    Processing steps (fully transparent):
        resume_skills = skills found in the resume
        job_skills    = skills found in the job description
        matched  = resume_skills INTERSECTION job_skills  (present in both)
        missing  = job_skills   MINUS         resume_skills (required, absent)
        extra    = resume_skills MINUS        job_skills   (bonus skills)
        match %  = matched / total_job_skills * 100  (0 if no job skills)

    Output dict:
        matched, missing, extra           -> sorted lists
        total_job_keywords, matched_count, missing_count
        match_percentage                  -> float 0..100 (never divides by 0)
    """
    resume_skills = extract_job_keywords(resume_text, skill_database)
    job_skills = extract_job_keywords(job_description, skill_database)

    matched = resume_skills.intersection(job_skills)
    missing = job_skills.difference(resume_skills)
    extra = resume_skills.difference(job_skills)

    total = len(job_skills)
    if total > 0:
        match_percentage = round(len(matched) / total * 100, 2)
    else:
        # No recognised keywords in the job description -> 0%, no crash.
        match_percentage = 0.0

    return {
        "matched": sorted(matched),
        "missing": sorted(missing),
        "extra": sorted(extra),
        "total_job_keywords": total,
        "matched_count": len(matched),
        "missing_count": len(missing),
        "match_percentage": match_percentage,
    }


# ===========================================================================
# 7. EXPERIENCE / EDUCATION KEYWORD DETECTION (approximate)
# ===========================================================================

_DEGREE_KEYWORDS = [
    "b.e", "be", "b.tech", "btech", "b.sc", "bsc", "bca", "b.com",
    "m.e", "me", "m.tech", "mtech", "m.sc", "msc", "mca", "mba",
    "bachelor", "master", "phd", "doctorate", "diploma",
]


def detect_experience_education(text):
    """Approximately detect experience/education signals in the resume.

    Output dict:
        years_of_experience -> list of snippets like "3 years"
        degrees             -> list of detected degree keywords
        graduation_years    -> list of 4-digit years 1950-2099
        has_internship      -> bool
        has_projects        -> bool
        has_certifications  -> bool

    These detections are APPROXIMATE and are not a substitute for reading the
    resume. We never invent a candidate's qualifications or experience.
    """
    cleaned = preprocess_text(text)

    years = re.findall(r"(\d+)\+?\s*years?", cleaned)
    years_of_experience = [f"{y} years" for y in years]

    degrees = []
    for kw in _DEGREE_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", cleaned) and kw not in degrees:
            degrees.append(kw)

    graduation_years = re.findall(r"\b(?:19[5-9]\d|20\d\d)\b", cleaned)

    return {
        "years_of_experience": years_of_experience,
        "degrees": degrees,
        "graduation_years": sorted(set(graduation_years)),
        "has_internship": bool(re.search(r"\binternship", cleaned)),
        "has_projects": bool(re.search(r"\bprojects?\b", cleaned)),
        "has_certifications": bool(re.search(r"\bcertificat", cleaned)),
    }


# ===========================================================================
# 8. QUALITY CHECKS (heuristics, not absolute rules)
# ===========================================================================

def has_excessive_whitespace(text):
    """Heuristic: True if the resume has many blank lines or long space runs."""
    if not text:
        return False
    many_blank_lines = bool(re.search(r"(?:\r?\n\s*){4,}\r?\n", text))
    long_space_runs = bool(re.search(r" {5,}", text))
    return many_blank_lines or long_space_runs


def resume_quality_checks(text, contact, sections, statistics, exp_edu):
    """Build a list of transparent, heuristic quality checks.

    Each item: {"label": str, "passed": bool, "note": str}

    These are HEURISTIC checks, not absolute rules. A failing check does not
    mean the resume is bad - it only flags something a human may want to review.
    We never automatically penalise a candidate for format or experience.
    """
    checks = [
        {
            "label": "Email address detected",
            "passed": contact["email"]["found"],
            "note": "An e-mail address helps recruiters contact the candidate.",
        },
        {
            "label": "Phone number detected",
            "passed": contact["phone"]["found"],
            "note": "A phone number was matched by a pattern (may be approximate).",
        },
        {
            "label": "Education mentioned",
            "passed": sections["detected"].get("Education", False),
            "note": "An education section helps show background.",
        },
        {
            "label": "Work experience mentioned",
            "passed": sections["detected"].get("Work Experience", False),
            "note": "Experience is often expected (not required for freshers).",
        },
        {
            "label": "Skills section mentioned",
            "passed": sections["detected"].get("Technical Skills", False),
            "note": "A clearly labelled skills section improves keyword matching.",
        },
        {
            "label": "Projects mentioned",
            "passed": sections["detected"].get("Projects", False) or exp_edu["has_projects"],
            "note": "Projects demonstrate practical ability.",
        },
        {
            "label": "Certifications mentioned",
            "passed": sections["detected"].get("Certifications", False) or exp_edu["has_certifications"],
            "note": "Certifications are optional and not required.",
        },
        {
            "label": "Reasonable length (not too short)",
            "passed": statistics["word_count"] >= 80,
            "note": "Very short resumes may be missing useful detail.",
        },
        {
            "label": "No excessive repeated whitespace",
            "passed": not has_excessive_whitespace(text),
            "note": "Lots of blank space can indicate formatting issues.",
        },
    ]
    return checks


# ===========================================================================
# 9. READINESS SCORE (weighted, fully documented)
# ===========================================================================
#
# The MAIN score is the keyword match percentage (Feature 6). On top of that we
# build a broader, OPTIONAL "Resume Readiness Score" from four clearly defined
# components whose weights sum to exactly 100%:
#
#     Job keyword coverage ........ 60%
#     Detected resume sections .... 20%
#     Contact completeness ........ 10%
#     Readability indicators ...... 10%
#
# Every weight is documented and the per-component contribution is returned so
# the user can see exactly how the total was built.

DEFAULT_WEIGHTS = {
    "keyword_coverage": 60,
    "sections": 20,
    "contact": 10,
    "readability": 10,
}

# Sections that matter most for the "sections" component.
_IMPORTANT_SECTIONS = [
    "Work Experience", "Education", "Technical Skills", "Projects",
]


def calculate_readiness_score(keyword_match, sections, contact, statistics,
                              text="", weights=None):
    """Compute the weighted Resume Readiness Score (0-100).

    Inputs are the already-computed sub-results. Returns a dict:
        components -> {name: {"score_pct": 0..100,
                              "weight": w,
                              "contribution": score_pct/100 * w}}
        total      -> rounded sum of contributions, clamped to 0..100.

    The score is a RULE-BASED educational indicator only.
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    # --- Component 1: keyword coverage (0..100) ---
    keyword_pct = keyword_match["match_percentage"]

    # --- Component 2: sections (fraction of important sections present) ---
    present_important = sum(
        1 for s in _IMPORTANT_SECTIONS if sections["detected"].get(s, False)
    )
    sections_pct = (present_important / len(_IMPORTANT_SECTIONS)) * 100

    # --- Component 3: contact completeness (email + phone, 50% each) ---
    contact_pct = 0.0
    if contact["email"]["found"]:
        contact_pct += 50
    if contact["phone"]["found"]:
        contact_pct += 50

    # --- Component 4: readability (length in a sensible range, no clutter) ---
    readability_pct = 100.0
    wc = statistics["word_count"]
    if wc < 80:
        readability_pct -= 50          # too short
    if has_excessive_whitespace(text):
        readability_pct -= 30          # cluttered formatting
    readability_pct = max(0.0, readability_pct)

    raw = {
        "keyword_coverage": keyword_pct,
        "sections": sections_pct,
        "contact": contact_pct,
        "readability": readability_pct,
    }

    components = {}
    total = 0.0
    for name, weight in weights.items():
        score_pct = round(raw.get(name, 0.0), 2)
        contribution = round(score_pct / 100 * weight, 2)
        components[name] = {
            "score_pct": score_pct,
            "weight": weight,
            "contribution": contribution,
        }
        total += contribution

    total = round(max(0.0, min(100.0, total)), 2)
    return {"components": components, "total": total}


# ===========================================================================
# 10. SKILL GAP ANALYSIS
# ===========================================================================

def analyze_skill_gaps(resume_skills, job_skills,
                       skill_database=SKILL_DATABASE):
    """Build a row-per-skill comparison for every skill the job requires.

    Inputs:
        resume_skills - set/list of skills found in the resume.
        job_skills    - set/list of skills required by the job description.
    Output: list of dicts with keys:
        skill, category, in_resume (bool), required_by_job (True),
        recommendation (str)

    We only recommend genuinely learning missing skills - we NEVER suggest
    falsely claiming a skill.
    """
    resume_set = set(resume_skills)
    lookup = skill_category_lookup(skill_database)

    rows = []
    for skill in sorted(set(job_skills)):
        in_resume = skill in resume_set
        if in_resume:
            recommendation = "Already present - keep it clearly listed."
        else:
            recommendation = (
                f"Gap: if you genuinely have '{skill}', add it; "
                f"otherwise consider learning it through a course or project."
            )
        rows.append({
            "skill": skill,
            "category": lookup.get(skill, "Other"),
            "in_resume": in_resume,
            "required_by_job": True,
            "recommendation": recommendation,
        })
    return rows


# ===========================================================================
# 11. STRENGTHS + IMPROVEMENT SUGGESTIONS (rule-based)
# ===========================================================================

def generate_resume_strengths(analysis):
    """Return a list of evidence-backed strength statements.

    Every strength is linked to something actually detected in the text. We
    never infer seniority, achievements or qualifications that are not present.
    """
    strengths = []
    km = analysis["keyword_match"]
    contact = analysis["contact"]
    sections = analysis["sections"]
    skills_flat = analysis["resume_skills_flat"]

    if len(skills_flat) >= 6:
        strengths.append(
            f"Strong technical breadth: {len(skills_flat)} recognised skills detected."
        )
    if km["matched_count"] >= 1 and km["total_job_keywords"] > 0:
        strengths.append(
            f"Matched {km['matched_count']} of {km['total_job_keywords']} "
            f"required job keywords ({km['match_percentage']}%)."
        )
    if sections["detected"].get("Projects", False):
        strengths.append("A Projects section was detected, showing practical work.")
    if sections["detected"].get("Education", False):
        strengths.append("An Education section was detected.")
    if contact["email"]["found"] and contact["phone"]["found"]:
        strengths.append("Both an e-mail address and a phone number were detected.")
    if sections["detected"].get("Certifications", False):
        strengths.append("Certifications were mentioned.")

    if not strengths:
        strengths.append("No clear strengths were detected from the text yet.")
    return strengths


def generate_improvement_suggestions(analysis):
    """Return a list of actionable suggestions, each tied to a detected condition.

    Uses simple if/else rules. Suggestions never contradict the analysis and
    never encourage dishonesty.
    """
    suggestions = []
    km = analysis["keyword_match"]
    contact = analysis["contact"]
    sections = analysis["sections"]
    stats = analysis["statistics"]

    if not contact["email"]["found"]:
        suggestions.append("No e-mail detected - check that your contact section includes one.")
    if not contact["phone"]["found"]:
        suggestions.append("No phone number detected - add a reachable number if appropriate.")
    if not sections["detected"].get("Technical Skills", False):
        suggestions.append("Add a clearly labelled 'Technical Skills' section to improve matching.")
    if not sections["detected"].get("Work Experience", False):
        suggestions.append("Consider adding a Work Experience or Internship section if applicable.")
    if not sections["detected"].get("Projects", False):
        suggestions.append("Add relevant projects where applicable - they demonstrate ability.")

    if km["missing"]:
        preview = ", ".join(km["missing"][:8])
        suggestions.append(
            "Required keywords not detected: "
            f"{preview}. Review whether you genuinely have these skills and, "
            "if so, add them honestly."
        )

    if stats["word_count"] < 80:
        suggestions.append(
            "The resume is quite short - consider adding education, experience "
            "or project details."
        )

    if has_excessive_whitespace(analysis.get("raw_text", "")):
        suggestions.append("Reduce large blank areas / repeated spaces for a cleaner layout.")

    if not suggestions:
        suggestions.append("No major issues detected - the resume aligns well with this job.")
    return suggestions


# ===========================================================================
# 12. THE MASTER ANALYSIS FUNCTION
# ===========================================================================

def analyze_resume(resume_text, job_description, job_title="",
                   skill_database=SKILL_DATABASE, weights=None):
    """Run the full analysis pipeline and return one results dictionary.

    This single function ties every feature together so the Streamlit app (and
    the comparison / batch features) can reuse exactly the same logic, avoiding
    duplicated matching code.

    Output: a dictionary containing statistics, contact, sections, skills,
    keyword_match, skill_gap, readiness, strengths, suggestions, etc.
    """
    resume_text = resume_text or ""
    job_description = job_description or ""

    statistics = count_resume_statistics(resume_text)
    contact = detect_contact_information(resume_text)
    sections = detect_resume_sections(resume_text)
    exp_edu = detect_experience_education(resume_text)

    resume_skills = extract_skills(resume_text, skill_database)
    job_skills = extract_skills(job_description, skill_database)
    resume_skills_flat = flatten_skills(resume_skills)
    job_skills_flat = flatten_skills(job_skills)

    keyword_match = calculate_keyword_match(
        resume_text, job_description, skill_database
    )
    skill_gap = analyze_skill_gaps(
        resume_skills_flat, job_skills_flat, skill_database
    )
    readiness = calculate_readiness_score(
        keyword_match, sections, contact, statistics, resume_text, weights
    )
    quality = resume_quality_checks(
        resume_text, contact, sections, statistics, exp_edu
    )

    analysis = {
        "job_title": job_title,
        "raw_text": resume_text,
        "statistics": statistics,
        "contact": contact,
        "sections": sections,
        "experience_education": exp_edu,
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "resume_skills_flat": resume_skills_flat,
        "job_skills_flat": job_skills_flat,
        "keyword_match": keyword_match,
        "skill_gap": skill_gap,
        "readiness": readiness,
        "quality_checks": quality,
    }
    analysis["strengths"] = generate_resume_strengths(analysis)
    analysis["suggestions"] = generate_improvement_suggestions(analysis)
    return analysis


# ===========================================================================
# 13. COMPARISON + BATCH SCREENING
# ===========================================================================

def compare_resumes(resume_a, resume_b, job_description,
                    name_a="Resume A", name_b="Resume B",
                    skill_database=SKILL_DATABASE):
    """Analyze two resumes against the SAME job description.

    Output dict with one entry per resume plus a tidy side-by-side summary.

    This measures TEXTUAL RELEVANCE to the given job description only. It is not
    an objective measure of candidate quality.
    """
    ana_a = analyze_resume(resume_a, job_description, skill_database=skill_database)
    ana_b = analyze_resume(resume_b, job_description, skill_database=skill_database)

    def summary(name, ana):
        return {
            "name": name,
            "match_percentage": ana["keyword_match"]["match_percentage"],
            "matched_count": ana["keyword_match"]["matched_count"],
            "missing_count": ana["keyword_match"]["missing_count"],
            "word_count": ana["statistics"]["word_count"],
            "sections_present": len(ana["sections"]["present"]),
            "contact_complete": (
                ana["contact"]["email"]["found"] and ana["contact"]["phone"]["found"]
            ),
            "readiness": ana["readiness"]["total"],
        }

    return {
        name_a: ana_a,
        name_b: ana_b,
        "summary": [summary(name_a, ana_a), summary(name_b, ana_b)],
    }


def analyze_multiple_resumes(resumes, job_description, max_files=10,
                             skill_database=SKILL_DATABASE):
    """Screen several resumes against one job description.

    Input:
        resumes - a list where each item is either:
                    * a plain string (the resume text), or
                    * a tuple (identifier, resume_text).
        job_description - the single job description to screen against.
        max_files - a configurable safety limit on how many to process.

    Output: list of row dicts. A failure in one resume is captured as an
    'error' field and does NOT stop the whole batch.

    Neutral identifiers (Candidate 1, Candidate 2, ...) are used unless a name
    is supplied. We never rank or reject based on sensitive attributes.
    """
    rows = []
    for index, item in enumerate(resumes[:max_files], start=1):
        if isinstance(item, (tuple, list)) and len(item) == 2:
            identifier, text = item
        else:
            identifier, text = f"Candidate {index}", item

        try:
            ana = analyze_resume(text, job_description, skill_database=skill_database)
            km = ana["keyword_match"]
            rows.append({
                "identifier": identifier,
                "match_percentage": km["match_percentage"],
                "matched_keywords": ", ".join(km["matched"]),
                "missing_keywords": ", ".join(km["missing"]),
                "word_count": ana["statistics"]["word_count"],
                "sections_present": len(ana["sections"]["present"]),
                "error": "",
            })
        except Exception as exc:  # noqa: BLE001 - keep the batch alive
            rows.append({
                "identifier": identifier,
                "match_percentage": 0.0,
                "matched_keywords": "",
                "missing_keywords": "",
                "word_count": 0,
                "sections_present": 0,
                "error": str(exc),
            })
    return rows


# ===========================================================================
# 14. FILE TEXT EXTRACTION
# ===========================================================================

def extract_text_from_file(uploaded_file):
    """Extract plain text from an uploaded TXT, PDF or DOCX file.

    `uploaded_file` is a file-like object (e.g. a Streamlit UploadedFile) that
    has a `.name` and can be read as bytes.

    Returns the extracted text (str). Raises ValueError with a friendly message
    on unsupported / unreadable files so the caller can show a clean error.

    Note: scanned / image-only PDFs contain no selectable text, so extraction
    will return little or nothing. Such files would need OCR, which is outside
    the scope of this project.
    """
    if uploaded_file is None:
        raise ValueError("No file was provided.")

    name = getattr(uploaded_file, "name", "uploaded")
    lower = name.lower()

    # Read raw bytes (Streamlit's UploadedFile supports .read()).
    raw = uploaded_file.read()
    if isinstance(raw, str):
        raw = raw.encode("utf-8", errors="ignore")

    if lower.endswith(".txt"):
        return raw.decode("utf-8", errors="ignore")

    if lower.endswith(".pdf"):
        try:
            from pypdf import PdfReader
        except ImportError:  # pragma: no cover - fallback for older installs
            try:
                from PyPDF2 import PdfReader
            except ImportError:
                raise ValueError(
                    "PDF support requires the 'pypdf' package. Install it with "
                    "'pip install pypdf'."
                )
        try:
            reader = PdfReader(io.BytesIO(raw))
            pages = [(page.extract_text() or "") for page in reader.pages]
        except Exception as exc:
            raise ValueError(f"Could not read the PDF file: {exc}")
        text = "\n".join(pages).strip()
        if not text:
            raise ValueError(
                "No selectable text was found. This may be a scanned/image-only "
                "PDF, which would require OCR (outside this project's scope)."
            )
        return text

    if lower.endswith(".docx"):
        try:
            import docx  # python-docx
        except ImportError:
            raise ValueError(
                "DOCX support requires the 'python-docx' package. Install it "
                "with 'pip install python-docx'."
            )
        try:
            document = docx.Document(io.BytesIO(raw))
        except Exception as exc:
            raise ValueError(f"Could not read the DOCX file: {exc}")
        return "\n".join(p.text for p in document.paragraphs).strip()

    raise ValueError(
        "Unsupported file type. Please upload a .txt, .pdf or .docx file."
    )


# ===========================================================================
# 15. REPORT GENERATION
# ===========================================================================

def create_analysis_report(analysis):
    """Build a downloadable Markdown/plain-text report from an analysis dict.

    Returns a single string suitable for a .md or .txt download.
    """
    km = analysis["keyword_match"]
    stats = analysis["statistics"]
    contact = analysis["contact"]
    sections = analysis["sections"]
    readiness = analysis["readiness"]

    lines = []
    lines.append("# Resume Analysis Report")
    lines.append("")
    if analysis.get("job_title"):
        lines.append(f"**Target role:** {analysis['job_title']}")
        lines.append("")
    lines.append("> This report is a rule-based, educational indicator of how "
                 "well a resume's keywords align with a job description. It is "
                 "NOT a prediction of hiring success or a guarantee of ATS "
                 "compatibility. Please use human judgement.")
    lines.append("")

    lines.append("## Overall Scores")
    lines.append(f"- Keyword match score: **{km['match_percentage']}%** "
                 f"({km['matched_count']} of {km['total_job_keywords']} keywords)")
    lines.append(f"- Resume readiness score: **{readiness['total']} / 100**")
    lines.append("")
    lines.append("### Readiness score breakdown")
    for name, comp in readiness["components"].items():
        lines.append(
            f"- {name.replace('_', ' ').title()}: {comp['score_pct']}% "
            f"x weight {comp['weight']}% = {comp['contribution']} points"
        )
    lines.append("")

    lines.append("## Resume Statistics")
    lines.append(f"- Words: {stats['word_count']}")
    lines.append(f"- Characters: {stats['character_count']}")
    lines.append(f"- Non-empty lines: {stats['line_count']}")
    lines.append(f"- Approx. sentences: {stats['sentence_count']}")
    lines.append(f"- Average word length: {stats['average_word_length']}")
    lines.append("")

    lines.append("## Contact Information (detected categories only)")
    lines.append(f"- Email: {'Yes' if contact['email']['found'] else 'No'}")
    lines.append(f"- Phone: {'Yes' if contact['phone']['found'] else 'No'}")
    lines.append(f"- LinkedIn: {'Yes' if contact['linkedin']['found'] else 'No'}")
    lines.append(f"- GitHub: {'Yes' if contact['github']['found'] else 'No'}")
    lines.append(f"- Portfolio/Website: {'Yes' if contact['portfolio']['found'] else 'No'}")
    lines.append("")

    lines.append("## Sections")
    lines.append(f"- Detected: {', '.join(sections['present']) or 'None'}")
    lines.append(f"- Possibly missing: {', '.join(sections['missing']) or 'None'}")
    lines.append("")

    lines.append("## Keyword Matching")
    lines.append(f"- Matched keywords ({km['matched_count']}): "
                 f"{', '.join(km['matched']) or 'None'}")
    lines.append(f"- Missing keywords ({km['missing_count']}): "
                 f"{', '.join(km['missing']) or 'None'}")
    lines.append(f"- Additional resume skills: {', '.join(km['extra']) or 'None'}")
    lines.append("")

    lines.append("## Strengths")
    for s in analysis.get("strengths", []):
        lines.append(f"- {s}")
    lines.append("")

    lines.append("## Improvement Suggestions")
    for s in analysis.get("suggestions", []):
        lines.append(f"- {s}")
    lines.append("")

    lines.append("---")
    lines.append("_Generated by ResumeIQ - an academic demonstration project._")
    return "\n".join(lines)


def _pdf_safe(text):
    """Make text safe for fpdf2's built-in (latin-1) font.

    Characters the core font cannot encode are replaced with '?'. This keeps
    the PDF generation dependency-free (no font files required).
    """
    return str(text).encode("latin-1", "replace").decode("latin-1")


def create_analysis_pdf(analysis):
    """Build a downloadable PDF report (bytes) from an analysis dict.

    Uses fpdf2 - a small, pure-Python PDF library, so no system packages or
    external services are needed. Returns the PDF as `bytes`, ready for
    Streamlit's st.download_button.

    The content mirrors create_analysis_report() so the Markdown preview and
    the downloaded PDF stay consistent.
    """
    from fpdf import FPDF  # imported lazily so tests that skip PDF stay light

    km = analysis["keyword_match"]
    stats = analysis["statistics"]
    contact = analysis["contact"]
    sections = analysis["sections"]
    readiness = analysis["readiness"]

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Each multi_cell moves the cursor back to the left margin and down a line
    # (fpdf2's default would otherwise leave the cursor at the cell's right
    # edge, causing a "not enough horizontal space" error on the next cell).
    def write(height, text):
        pdf.multi_cell(0, height, _pdf_safe(text),
                       new_x="LMARGIN", new_y="NEXT")

    def heading(text, size=12):
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", size)
        write(7, text)
        pdf.set_font("Helvetica", "", 11)

    def bullet(text):
        write(6, "- " + text)

    # --- Title ---
    pdf.set_font("Helvetica", "B", 18)
    write(10, "Resume Analysis Report")

    if analysis.get("job_title"):
        pdf.set_font("Helvetica", "I", 11)
        write(6, "Target role: " + analysis["job_title"])

    # --- Disclaimer ---
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(90, 90, 90)
    write(5,
          "This report is a rule-based, educational indicator of how well a "
          "resume's keywords align with a job description. It is NOT a prediction "
          "of hiring success or a guarantee of ATS compatibility. Please use "
          "human judgement.")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 11)

    heading("Overall Scores")
    bullet(f"Keyword match score: {km['match_percentage']}% "
           f"({km['matched_count']} of {km['total_job_keywords']} keywords)")
    bullet(f"Resume readiness score: {readiness['total']} / 100")

    heading("Readiness Score Breakdown")
    for name, comp in readiness["components"].items():
        bullet(f"{name.replace('_', ' ').title()}: {comp['score_pct']}% "
               f"x weight {comp['weight']}% = {comp['contribution']} points")

    heading("Resume Statistics")
    bullet(f"Words: {stats['word_count']}")
    bullet(f"Characters: {stats['character_count']}")
    bullet(f"Non-empty lines: {stats['line_count']}")
    bullet(f"Approx. sentences: {stats['sentence_count']}")
    bullet(f"Average word length: {stats['average_word_length']}")

    heading("Contact Information (detected categories only)")
    bullet("Email: " + ("Yes" if contact["email"]["found"] else "No"))
    bullet("Phone: " + ("Yes" if contact["phone"]["found"] else "No"))
    bullet("LinkedIn: " + ("Yes" if contact["linkedin"]["found"] else "No"))
    bullet("GitHub: " + ("Yes" if contact["github"]["found"] else "No"))
    bullet("Portfolio/Website: " + ("Yes" if contact["portfolio"]["found"] else "No"))

    heading("Sections")
    bullet("Detected: " + (", ".join(sections["present"]) or "None"))
    bullet("Possibly missing: " + (", ".join(sections["missing"]) or "None"))

    heading("Keyword Matching")
    bullet(f"Matched ({km['matched_count']}): " + (", ".join(km["matched"]) or "None"))
    bullet(f"Missing ({km['missing_count']}): " + (", ".join(km["missing"]) or "None"))
    bullet("Additional resume skills: " + (", ".join(km["extra"]) or "None"))

    heading("Strengths")
    for s in analysis.get("strengths", []):
        bullet(s)

    heading("Improvement Suggestions")
    for s in analysis.get("suggestions", []):
        bullet(s)

    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(90, 90, 90)
    write(5, "Generated by ResumeIQ - an academic demonstration project.")

    # fpdf2 returns a bytearray; convert to immutable bytes for Streamlit.
    return bytes(pdf.output())
