"""
sample_data.py
==============

This module stores all the EMBEDDED STRINGS used by the Resume Analyzer.

"Embedded strings" means predefined multiline text literals written directly
inside the Python source code using triple-quoted strings (\"\"\" ... \"\"\").
They are NOT machine-learning embeddings / vectors. They are simply plain text
that ships with the program so the application works instantly without needing
any external files, database, or internet connection.

What lives here:
  * SKILL_DATABASE        -> a dictionary of lists (skills grouped by category)
  * SAMPLE_RESUMES        -> five realistic resumes stored as triple-quoted text
  * SAMPLE_JOB_DESCRIPTIONS -> five matching job descriptions
  * ROLE_SAMPLES          -> links each job role to a resume + job description

Python concepts demonstrated in this file:
  * Triple-quoted (multiline) string literals
  * Dictionaries  { key: value }
  * Lists         [ item, item, ... ]
  * Dictionary of lists (SKILL_DATABASE)
"""

# ---------------------------------------------------------------------------
# SKILL DATABASE
# ---------------------------------------------------------------------------
# This is a "dictionary of lists".
#   - The KEY   is a skill category (a string).
#   - The VALUE is a list of lowercase skill keywords belonging to that category.
#
# We store everything in lowercase so that matching can be done in a
# case-insensitive way (we lowercase the resume text too, then compare).
#
# Multiword skills such as "machine learning", "spring boot" and "power bi"
# are intentionally included to demonstrate multiword keyword matching.
SKILL_DATABASE = {
    "Programming Languages": [
        "python", "java", "c++", "c#", "javascript", "typescript",
        "go", "r", "ruby", "php", "scala", "kotlin", ".net",
    ],
    "Web Development": [
        "streamlit", "flask", "django", "fastapi", "react", "angular",
        "vue", "node.js", "spring boot", "html", "css", "express",
    ],
    "Databases": [
        "sql", "mysql", "postgresql", "mongodb", "oracle",
        "redis", "sqlite", "cassandra",
    ],
    "Data Engineering": [
        "spark", "hadoop", "kafka", "airflow", "etl",
        "data engineering", "snowflake", "databricks",
    ],
    "Cloud Computing": [
        "aws", "azure", "gcp", "lambda", "ec2", "s3", "cloud computing",
    ],
    "DevOps": [
        "git", "docker", "kubernetes", "jenkins", "ci/cd",
        "terraform", "ansible", "linux",
    ],
    "AI and Machine Learning": [
        "machine learning", "deep learning", "nlp", "scikit-learn",
        "tensorflow", "pytorch", "keras", "computer vision",
    ],
    "Data Analysis": [
        "pandas", "numpy", "excel", "statistics", "power bi",
        "tableau", "matplotlib", "data analysis", "data visualization",
    ],
    "Testing and Quality Assurance": [
        "selenium", "pytest", "junit", "unit testing", "qa",
    ],
    "Tools and Platforms": [
        "github", "jira", "confluence", "postman", "vs code",
    ],
}


# ---------------------------------------------------------------------------
# SAMPLE RESUMES (embedded multiline strings)
# ---------------------------------------------------------------------------
# Each resume is written as a triple-quoted string. The students can edit these
# in the user interface before analyzing them.

RESUME_PYTHON_DEVELOPER = """
John Mathew
Email: john.mathew@example.com | Phone: +91 98765 43210
LinkedIn: linkedin.com/in/johnmathew | GitHub: github.com/johnmathew

Professional Summary
Python Developer with 3 years of experience building web applications and
automation scripts. Strong background in Python programming, SQL and data
analysis. Comfortable working with Git in a collaborative team environment.

Technical Skills
Python, SQL, Flask, Streamlit, pandas, NumPy, Git, Docker, REST APIs, Linux

Work Experience
Software Engineer, Brightsoft Solutions (2021 - Present)
- Developed internal dashboards using Streamlit and pandas.
- Built REST APIs with Flask and integrated PostgreSQL databases.
- Automated reporting tasks, reducing manual effort by several hours per week.

Projects
Resume Analyzer - A text-processing tool built with Python and Streamlit.
Inventory Tracker - A Flask web application backed by a SQL database.

Education
B.E. Computer Science, Anna University, 2021

Certifications
Python for Everybody (Coursera)
"""

RESUME_DATA_ANALYST = """
Priya Sharma
priya.sharma@example.com  |  +91 91234 56789
LinkedIn: linkedin.com/in/priyasharma

Career Objective
Detail-oriented Data Analyst seeking to apply strong data analysis and
visualization skills to support business decisions.

Skills
Excel, SQL, Python, pandas, NumPy, Power BI, Tableau, Statistics,
Data Visualization, Data Analysis

Employment History
Data Analyst, MarketEdge Analytics (2020 - Present)
- Built interactive Power BI dashboards for sales teams.
- Wrote SQL queries to extract and clean large datasets.
- Performed statistical analysis to identify trends.

Education
M.Sc. Statistics, Delhi University, 2020
B.Sc. Mathematics, Delhi University, 2018

Achievements
Employee of the Month for improving reporting accuracy.
"""

RESUME_JAVA_DEVELOPER = """
Arun Kumar
arun.kumar@example.com | 9876501234
GitHub: github.com/arunkumar

Summary
Java Developer with experience designing scalable backend services using
Java and Spring Boot. Familiar with microservices and REST APIs.

Technical Skills
Java, Spring Boot, SQL, MySQL, Git, Docker, Kubernetes, Jenkins, Linux, JUnit

Professional Experience
Backend Developer, Nexus Technologies (2019 - Present)
- Designed and maintained microservices using Java and Spring Boot.
- Managed CI/CD pipelines with Jenkins and Docker.
- Deployed services to Kubernetes clusters.

Projects
Payment Gateway Service - A Spring Boot microservice handling transactions.

Education
B.Tech Information Technology, VIT, 2019

Certifications
Oracle Certified Java Programmer
"""

RESUME_AIML_ENGINEER = """
Sneha Reddy
sneha.reddy@example.com | +91 90000 11111
LinkedIn: linkedin.com/in/snehareddy | GitHub: github.com/snehareddy
Portfolio: snehareddy.dev

Professional Summary
Machine Learning Engineer with 2 years of experience developing and deploying
models for classification and natural language processing tasks.

Technical Skills
Python, Machine Learning, Deep Learning, NLP, scikit-learn, TensorFlow,
PyTorch, pandas, NumPy, SQL, Git, AWS

Work Experience
Machine Learning Engineer, DataMind Labs (2022 - Present)
- Built NLP models for text classification using scikit-learn and PyTorch.
- Developed deep learning pipelines with TensorFlow.
- Deployed models to AWS using Docker containers.

Projects
Sentiment Analysis Engine - An NLP project using Python and scikit-learn.
Image Classifier - A deep learning model built with TensorFlow.

Education
M.Tech Artificial Intelligence, IIIT Hyderabad, 2022

Publications
Published a paper on text classification at a student research symposium.
"""

RESUME_CLOUD_ENGINEER = """
Mohammed Ali
mohammed.ali@example.com | +91 98111 22333
LinkedIn: linkedin.com/in/mohammedali

Summary
Cloud Engineer experienced in designing and maintaining cloud infrastructure
on AWS and Azure with a strong focus on automation and reliability.

Technical Skills
AWS, Azure, Docker, Kubernetes, Terraform, Ansible, Jenkins, CI/CD,
Linux, Python, Git

Employment History
Cloud Engineer, SkyScale Systems (2019 - Present)
- Managed AWS infrastructure using Terraform and Ansible.
- Built CI/CD pipelines with Jenkins and Docker.
- Orchestrated containers using Kubernetes.

Projects
Infrastructure Automation - Automated AWS provisioning using Terraform.

Education
B.E. Electronics and Communication, NIT, 2018

Certifications
AWS Certified Solutions Architect
"""


# A dictionary that maps a friendly resume name -> the embedded resume text.
SAMPLE_RESUMES = {
    "Python Developer": RESUME_PYTHON_DEVELOPER,
    "Data Analyst": RESUME_DATA_ANALYST,
    "Java Developer": RESUME_JAVA_DEVELOPER,
    "AI/ML Engineer": RESUME_AIML_ENGINEER,
    "Cloud Engineer": RESUME_CLOUD_ENGINEER,
}


# ---------------------------------------------------------------------------
# SAMPLE JOB DESCRIPTIONS (embedded multiline strings)
# ---------------------------------------------------------------------------

JD_PYTHON_DEVELOPER = """
We are seeking a Python Developer to join our engineering team.

Responsibilities and Requirements:
- Strong experience in Python programming.
- Experience with SQL databases such as PostgreSQL.
- Familiarity with web frameworks like Flask or Streamlit.
- Experience using pandas for data analysis.
- Version control using Git.
- Knowledge of Docker and Linux is a plus.
- Good problem-solving and software development skills.
"""

JD_DATA_ANALYST = """
We are hiring a Data Analyst to support our business intelligence team.

Requirements:
- Strong skills in SQL and Excel.
- Experience with data analysis and data visualization.
- Hands-on experience with Power BI or Tableau.
- Knowledge of Python and pandas is preferred.
- Understanding of statistics.
- Ability to communicate insights clearly.
"""

JD_JAVA_DEVELOPER = """
We are looking for a Java Developer to build backend services.

Requirements:
- Solid experience with Java and Spring Boot.
- Experience designing REST APIs and microservices.
- Familiarity with SQL databases such as MySQL.
- Experience with Docker, Kubernetes and Jenkins.
- Knowledge of CI/CD pipelines.
- Experience with JUnit for testing.
"""

JD_AIML_ENGINEER = """
We are seeking an AI/ML Engineer to build and deploy machine learning models.

Requirements:
- Strong Python programming skills.
- Experience with machine learning and deep learning.
- Hands-on experience with scikit-learn, TensorFlow or PyTorch.
- Knowledge of NLP techniques.
- Experience with pandas and NumPy.
- Familiarity with deploying models on AWS.
- Version control using Git.
"""

JD_CLOUD_ENGINEER = """
We are hiring a Cloud Engineer to manage our cloud infrastructure.

Requirements:
- Strong experience with AWS and Azure.
- Experience with Docker and Kubernetes.
- Infrastructure as code using Terraform and Ansible.
- Building CI/CD pipelines with Jenkins.
- Comfortable working with Linux.
- Scripting experience with Python.
"""


SAMPLE_JOB_DESCRIPTIONS = {
    "Python Developer": JD_PYTHON_DEVELOPER,
    "Data Analyst": JD_DATA_ANALYST,
    "Java Developer": JD_JAVA_DEVELOPER,
    "AI/ML Engineer": JD_AIML_ENGINEER,
    "Cloud Engineer": JD_CLOUD_ENGINEER,
}


# ---------------------------------------------------------------------------
# ROLE SAMPLES
# ---------------------------------------------------------------------------
# A convenient mapping so the interface can load a matching resume + job
# description for a chosen role in one step (the "demo mode").
ROLE_SAMPLES = {
    role: {
        "resume": SAMPLE_RESUMES[role],
        "job_description": SAMPLE_JOB_DESCRIPTIONS[role],
    }
    for role in SAMPLE_RESUMES
}
