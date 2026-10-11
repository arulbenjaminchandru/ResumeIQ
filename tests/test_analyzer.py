"""
tests/test_analyzer.py
======================

Automated tests for the analysis engine using Python's built-in `unittest`.

Run from the project root with:
    python -m unittest discover -s tests

These tests cover the scenarios required by the project specification,
including tricky cases such as C++/C#/.NET, the single-letter skill "R",
empty inputs (no division-by-zero), and score bounds (always 0..100).
"""

import os
import sys
import unittest

# Make the project root importable when running `python -m unittest`.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import analyzer  # noqa: E402
from sample_data import SAMPLE_RESUMES, SAMPLE_JOB_DESCRIPTIONS  # noqa: E402


class TestPreprocessing(unittest.TestCase):
    def test_lowercases_and_trims(self):
        self.assertEqual(analyzer.preprocess_text("  Hello   WORLD \n"), "hello world")

    def test_preserves_tech_terms(self):
        cleaned = analyzer.preprocess_text("C++, C#, .NET and Node.js!")
        self.assertIn("c++", cleaned)
        self.assertIn("c#", cleaned)
        self.assertIn(".net", cleaned)
        self.assertIn("node.js", cleaned)

    def test_handles_none_and_non_string(self):
        self.assertEqual(analyzer.preprocess_text(None), "")
        self.assertEqual(analyzer.preprocess_text(123), "")

    def test_collapses_repeated_whitespace(self):
        messy = "line1\n\n\n\n    line2      end"
        self.assertEqual(analyzer.preprocess_text(messy), "line1 line2 end")


class TestSkillMatching(unittest.TestCase):
    def test_special_characters(self):
        text = "Experienced in C++, C#, .NET and Node.js development."
        skills = analyzer.flatten_skills(analyzer.extract_skills(text))
        self.assertIn("c++", skills)
        self.assertIn("c#", skills)
        self.assertIn(".net", skills)
        self.assertIn("node.js", skills)

    def test_single_letter_r_matches_only_as_word(self):
        # "R" as a standalone language should match.
        self.assertTrue(analyzer.skill_in_text("r", analyzer.preprocess_text("skills: python, r, sql")))
        # "R" must NOT match inside unrelated words.
        self.assertFalse(analyzer.skill_in_text("r", analyzer.preprocess_text("react and recruiting")))
        self.assertFalse(analyzer.skill_in_text("r", analyzer.preprocess_text("years of experience")))

    def test_case_insensitive(self):
        text = "PYTHON and Pandas and SQL"
        skills = analyzer.flatten_skills(analyzer.extract_skills(text))
        self.assertIn("python", skills)
        self.assertIn("pandas", skills)
        self.assertIn("sql", skills)

    def test_multiword_skill(self):
        skills = analyzer.flatten_skills(analyzer.extract_skills("I use Machine Learning daily"))
        self.assertIn("machine learning", skills)

    def test_duplicate_skills_counted_once(self):
        text = "python python python and more python"
        extracted = analyzer.extract_skills(text)
        python_hits = [s for cat in extracted.values() for s in cat if s == "python"]
        self.assertEqual(len(python_hits), 1)


class TestKeywordMatch(unittest.TestCase):
    def test_good_match(self):
        result = analyzer.calculate_keyword_match(
            SAMPLE_RESUMES["Python Developer"],
            SAMPLE_JOB_DESCRIPTIONS["Python Developer"],
        )
        self.assertGreater(result["match_percentage"], 50)
        self.assertGreaterEqual(result["matched_count"], 1)

    def test_no_matching_skills(self):
        resume = "I enjoy painting, gardening and cooking."
        jd = SAMPLE_JOB_DESCRIPTIONS["Python Developer"]
        result = analyzer.calculate_keyword_match(resume, jd)
        self.assertEqual(result["matched_count"], 0)
        self.assertEqual(result["match_percentage"], 0.0)

    def test_empty_resume(self):
        result = analyzer.calculate_keyword_match("", SAMPLE_JOB_DESCRIPTIONS["Data Analyst"])
        self.assertEqual(result["matched_count"], 0)
        self.assertEqual(result["match_percentage"], 0.0)

    def test_empty_job_description_no_divide_by_zero(self):
        result = analyzer.calculate_keyword_match(SAMPLE_RESUMES["Java Developer"], "")
        self.assertEqual(result["total_job_keywords"], 0)
        self.assertEqual(result["match_percentage"], 0.0)

    def test_jd_with_no_identifiable_keywords(self):
        jd = "We want a friendly, motivated, hardworking team player."
        result = analyzer.calculate_keyword_match(SAMPLE_RESUMES["Java Developer"], jd)
        self.assertEqual(result["total_job_keywords"], 0)
        self.assertEqual(result["match_percentage"], 0.0)

    def test_missing_keywords_correct(self):
        resume = "python and sql"
        jd = "python, sql, docker, aws"
        result = analyzer.calculate_keyword_match(resume, jd)
        self.assertIn("docker", result["missing"])
        self.assertIn("aws", result["missing"])
        self.assertNotIn("python", result["missing"])


class TestContactDetection(unittest.TestCase):
    def test_multiple_emails(self):
        text = "Reach me at a@example.com or b@example.org"
        contact = analyzer.detect_contact_information(text)
        self.assertTrue(contact["email"]["found"])
        self.assertGreaterEqual(contact["email"]["count"], 2)

    def test_missing_contact(self):
        contact = analyzer.detect_contact_information("No contact details here.")
        self.assertFalse(contact["email"]["found"])
        self.assertFalse(contact["phone"]["found"])

    def test_phone_detected(self):
        contact = analyzer.detect_contact_information("Call +91 98765 43210 today")
        self.assertTrue(contact["phone"]["found"])


class TestSections(unittest.TestCase):
    def test_alternate_headings(self):
        resume = """
        Profile
        A motivated engineer.

        Employment History
        Worked at a company.

        Academic Background
        Studied engineering.
        """
        sections = analyzer.detect_resume_sections(resume)
        self.assertTrue(sections["detected"]["Professional Summary"])   # "profile"
        self.assertTrue(sections["detected"]["Work Experience"])        # "employment history"

    def test_detects_standard_sections(self):
        sections = analyzer.detect_resume_sections(SAMPLE_RESUMES["Python Developer"])
        self.assertTrue(sections["detected"]["Technical Skills"])
        self.assertTrue(sections["detected"]["Education"])


class TestStatistics(unittest.TestCase):
    def test_empty_text(self):
        stats = analyzer.count_resume_statistics("")
        self.assertEqual(stats["word_count"], 0)
        self.assertEqual(stats["average_word_length"], 0.0)

    def test_whitespace_only_lines(self):
        stats = analyzer.count_resume_statistics("hello world\n\n\n   \nagain")
        self.assertEqual(stats["word_count"], 3)
        self.assertEqual(stats["line_count"], 2)

    def test_excessive_whitespace_flag(self):
        self.assertTrue(analyzer.has_excessive_whitespace("a\n\n\n\n\n\nb"))
        self.assertFalse(analyzer.has_excessive_whitespace("a\nb\nc"))


class TestReadinessScore(unittest.TestCase):
    def test_score_within_bounds_for_all_samples(self):
        for role in SAMPLE_RESUMES:
            ana = analyzer.analyze_resume(
                SAMPLE_RESUMES[role], SAMPLE_JOB_DESCRIPTIONS[role]
            )
            total = ana["readiness"]["total"]
            self.assertGreaterEqual(total, 0)
            self.assertLessEqual(total, 100)

    def test_weights_sum_to_100(self):
        self.assertEqual(sum(analyzer.DEFAULT_WEIGHTS.values()), 100)

    def test_empty_inputs_score_zero_no_crash(self):
        ana = analyzer.analyze_resume("", "")
        self.assertGreaterEqual(ana["readiness"]["total"], 0)
        self.assertLessEqual(ana["readiness"]["total"], 100)


class TestComparisonAndBatch(unittest.TestCase):
    def test_compare_two_resumes(self):
        result = analyzer.compare_resumes(
            SAMPLE_RESUMES["Python Developer"],
            SAMPLE_RESUMES["Data Analyst"],
            SAMPLE_JOB_DESCRIPTIONS["Python Developer"],
            "Candidate 1", "Candidate 2",
        )
        self.assertEqual(len(result["summary"]), 2)
        # Python resume should match a Python job better than a data analyst one.
        py = result["summary"][0]["match_percentage"]
        da = result["summary"][1]["match_percentage"]
        self.assertGreaterEqual(py, da)

    def test_batch_handles_mixed_items_and_failures(self):
        resumes = [
            ("Candidate 1", SAMPLE_RESUMES["Java Developer"]),
            SAMPLE_RESUMES["Cloud Engineer"],   # plain string -> auto-named
            ("Broken", 12345),                  # invalid text type -> captured error? no, int
        ]
        jd = SAMPLE_JOB_DESCRIPTIONS["Java Developer"]
        rows = analyzer.analyze_multiple_resumes(resumes, jd, max_files=10)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1]["identifier"], "Candidate 2")

    def test_batch_respects_max_files(self):
        resumes = ["python"] * 20
        rows = analyzer.analyze_multiple_resumes(resumes, "python", max_files=5)
        self.assertEqual(len(rows), 5)


class TestReport(unittest.TestCase):
    def test_report_contains_scores(self):
        ana = analyzer.analyze_resume(
            SAMPLE_RESUMES["AI/ML Engineer"], SAMPLE_JOB_DESCRIPTIONS["AI/ML Engineer"]
        )
        report = analyzer.create_analysis_report(ana)
        self.assertIn("Resume Analysis Report", report)
        self.assertIn("Keyword match score", report)
        self.assertIn("readiness", report.lower())

    def test_pdf_report_is_valid_bytes(self):
        ana = analyzer.analyze_resume(
            SAMPLE_RESUMES["Cloud Engineer"], SAMPLE_JOB_DESCRIPTIONS["Cloud Engineer"]
        )
        pdf_bytes = analyzer.create_analysis_pdf(ana)
        self.assertIsInstance(pdf_bytes, bytes)
        # Every real PDF file begins with the "%PDF" magic header.
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertGreater(len(pdf_bytes), 500)


if __name__ == "__main__":
    unittest.main(verbosity=2)
