import os
import re
from typing import List, Dict, Any, Set

DEFAULT_SKILLS_DICTIONARY = [
    "Python", "JavaScript", "TypeScript", "HTML", "CSS", "React", "Vue", "Angular",
    "Node.js", "Express", "Flask", "Django", "FastAPI", "SQL", "MySQL", "PostgreSQL",
    "MongoDB", "SQLite", "Redis", "Docker", "Kubernetes", "AWS", "Azure", "GCP",
    "Git", "GitHub", "CI/CD", "Linux", "REST API", "GraphQL", "Machine Learning",
    "Deep Learning", "NLP", "Data Science", "Pandas", "NumPy", "Scikit-Learn",
    "TensorFlow", "PyTorch", "OpenCV", "Statistics", "Data Analysis", "Microservices",
    "Java", "C++", "C#", "Go", "Rust", "PHP", "Laravel", "Spring Boot",
    "Agile", "Scrum", "Jira", "Unit Testing", "TDD", "System Design",
    "Communication", "Leadership", "Problem Solving", "Teamwork", "Time Management"
]


def extract_text_from_file(file_path: str) -> str:
    """
    Extract raw text from PDF, DOCX, or TXT files.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _extract_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return _extract_from_docx(file_path)
    elif ext in [".txt", ".md"]:
        return _extract_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def _extract_from_pdf(file_path: str) -> str:
    text = ""
    try:
        import PyPDF2
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        # Fallback basic binary text extraction if PyPDF2 fails
        with open(file_path, "rb") as f:
            raw = f.read()
            text = re.sub(r'[^\x20-\x7E\n\r\t]', ' ', raw.decode('latin-1', errors='ignore'))
    return text.strip()


def _extract_from_docx(file_path: str) -> str:
    try:
        import docx
        doc = docx.Document(file_path)
        full_text = [para.text for para in doc.paragraphs]
        return "\n".join(full_text).strip()
    except Exception as e:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()


def _extract_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()


def extract_skills_from_text(text: str, custom_skills: List[str] = None) -> Dict[str, Any]:
    """
    NLP & Keyword skill extraction engine.
    Matches extracted text against master skill vocabulary and returns structured results.
    """
    if not text:
        return {"skills": [], "skill_count": 0, "raw_text_length": 0}

    skill_vocabulary = set(DEFAULT_SKILLS_DICTIONARY)
    if custom_skills:
        skill_vocabulary.update(custom_skills)

    found_skills: Set[str] = set()

    # Preprocess text
    normalized_text = " " + re.sub(r'[^\w\s\+\#\/\.\-]', ' ', text.lower()) + " "

    for skill in skill_vocabulary:
        skill_clean = skill.lower().strip()
        if not skill_clean:
            continue

        # Regex matching with word boundaries
        pattern = r'(?<=[\s,./\(\)\[\]])' + re.escape(skill_clean) + r'(?=[\s,./\(\)\[\]]|$)'
        
        # Simple string check as first fast pass
        if skill_clean in normalized_text:
            if re.search(pattern, normalized_text) or len(skill_clean) > 3:
                found_skills.add(skill)

    # Format result list sorted alphabetically
    sorted_skills = sorted(list(found_skills), key=lambda s: s.lower())

    return {
        "skills": sorted_skills,
        "skill_count": len(sorted_skills),
        "raw_text_length": len(text)
    }
