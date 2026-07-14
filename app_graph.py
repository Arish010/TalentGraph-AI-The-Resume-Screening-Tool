from langgraph.graph import StateGraph, END
from graph_state import ResumeState
from agents import AgenticNodes
from embedding_engine import EmbeddingEngine
from data_processor import DataProcessor

def create_resume_screening_graph():
    nodes = AgenticNodes()
    math_engine = EmbeddingEngine()
    processor = DataProcessor()

    workflow = StateGraph(ResumeState)

    workflow.add_node("extractor", nodes.extraction_agent)

    def compute_math_score(state: ResumeState) -> dict:
        print("[MATH ENGINE] Mapping multi-dimensional vector spaces...")
        cleaned_jd = processor.clean_text(state["jd_text"])
        cleaned_resume = processor.clean_text(state["resume_raw"])
        
        jd_vector = math_engine.generate_embedding(cleaned_jd)
        res_vector = math_engine.generate_embedding(cleaned_resume)
        
        score = math_engine.calculate_similarity(res_vector, jd_vector)
        return {"similarity_score": round(score * 100, 2)}

    workflow.add_node("math_scorer", compute_math_score)

    workflow.add_node("explainer", nodes.explainer_agent)

    workflow.set_entry_point("extractor")
    workflow.add_edge("extractor", "math_scorer")
    workflow.add_edge("math_scorer", "explainer")
    workflow.add_edge("explainer", END)

    return workflow.compile()

if __name__ == "__main__":
    app = create_resume_screening_graph()
    print("[SUCCESS] LangGraph Multi-Agent framework compiled successfully with zero syntax errors!")
