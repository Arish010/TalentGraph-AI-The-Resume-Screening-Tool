import os
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from graph_state import ResumeState

class AgenticNodes:
    def __init__(self):
        if not os.getenv("GROQ_API_KEY"):
            raise ValueError("CRITICAL: GROQ_API_KEY environment variable is not set.")
            
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("GROQ_API_KEY"),
            openai_api_base="https://api.groq.com/openai/v1",
            model="llama-3.3-70b-versatile",
            temperature=0.3  
        )

    def _execute_with_retry(self, chain, input_data, description="LLM Node"):
        """Simple execution handler wrapper to safeguard pipeline streaming."""
        try:
            return chain.invoke(input_data)
        except Exception as e:
            print(f"\n[ERROR] Execution failed at {description}: {str(e)}")
            raise e

    def extraction_agent(self, state: ResumeState) -> dict:
        """Parses raw text and extracts clean structural data points."""
        print("[AGENT] Extraction Specialist is scanning profile details...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an elite AI HR parsing system. Your task is to extract core structural data points from the provided unstructured resume text into a clean summary."),
            ("user", "Extract the Name, Education, Professional Summary, and explicit Hard Skills from this resume:\n\n{resume_raw}")
        ])
        
        chain = prompt | self.llm
        response = self._execute_with_retry(chain, {"resume_raw": state["resume_raw"]}, "Extraction Specialist")
        
        return {
            "resume_data": {"extracted_summary": response.content},
            "matched_skills": [skill for skill in ["Python", "SQL", "PyTorch", "Scikit-learn", "Java", "Docker"] if skill.lower() in state["resume_raw"].lower()]
        }

    def explainer_agent(self, state: ResumeState) -> dict:
        """Evaluates similarity and writes a detailed, brutally honest career-coach critique."""
        print("[AGENT] Career Coach / Insight Specialist is drafting evaluation metrics...")

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are a brutally honest, highly experienced Technical Recruiter and AI Career Coach. "
                "Your job is to evaluate a candidate's profile against target job requirements and write a detailed, "
                "direct, and constructive critique. Do not sugarcoat things, but remain professional and encouraging.\n\n"
                "Format your response beautifully using the following markdown structure:\n"
                "### ⚖️ The Honest Verdict\n"
                "[Provide a realistic assessment of how they stack up. Address their experience tier and overall fit directly.]\n\n"
                "### 🛑 Critical Missing Gaps\n"
                "[Point out the exact skills, tools, methodologies, or structural details from the job description that are completely missing from their resume.]\n\n"
                "### 🛠️ Actionable Upgrades\n"
                "[Give 2-3 highly specific bullet points explaining exactly what projects they should add, phrasing they should change, or tools they must learn to bridge this gap.]"
            )),
            ("user", (
                "Target Job Requirements:\n{jd_text}\n\n"
                "Candidate Extracted Data:\n{extracted_summary}\n\n"
                "Calculated Mathematical Match Score: {score}%\n\n"
                "Please generate the detailed, structured critique:"
            ))
        ])

        chain = prompt | self.llm
        response = self._execute_with_retry(chain, {
            "jd_text": state["jd_text"],
            "extracted_summary": state["resume_data"]["extracted_summary"],
            "score": state["similarity_score"]
        }, "Insight Specialist")

        return {"insight": response.content}
