from typing import TypedDict, List, Optional

class ResumeState(TypedDict):
    """The shared state object that passes data between agents."""
    resume_raw: str            # The original text
    resume_data: dict          # Structured data extracted by the LLM
    jd_text: str               # The target job description
    similarity_score: float    # Result from the math engine
    insight: str               # Final generated feedback
    matched_skills: List[str]  # Keywords identified