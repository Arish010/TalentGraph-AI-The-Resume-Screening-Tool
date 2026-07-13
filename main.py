import os
import time
from app_graph import create_resume_screening_graph
from s3_service import S3Service

# CRITICAL: Replace this with your exact S3 bucket name
BUCKET_NAME = "resume-screening-system-arish"

def run_agentic_pipeline():
    print("="*60)
    print("   INITIALIZING CLOUD-INTEGRATED AGENT SCREENING ENGINE   ")
    print("="*60)
    
    # 1. Initialize S3 Service and compile LangGraph state machine
    s3 = S3Service(BUCKET_NAME)
    app = create_resume_screening_graph()
    
    # 2. Download the Job Description directly from S3
    try:
        job_description = s3.download_file_to_string("job_description.txt")
    except Exception as e:
        print(f"[CRITICAL ERROR] Could not retrieve job_description.txt from S3: {e}")
        return

    # 3. Retrieve all file keys from S3 root
    all_s3_keys = s3.list_resume_keys("")
    
    # Filter: Grab only candidate files, ignore the job description file itself
    resume_keys = [
        key for key in all_s3_keys 
        if key.endswith(".txt") and key != "job_description.txt"
    ]
    
    if not resume_keys:
        print("[WARNING] No candidate profiles found in your S3 bucket root.")
        return

    final_leaderboard_data = []

    print(f"\n[ORCHESTRATOR] Dispatched agents across {len(resume_keys)} AWS cloud streams...\n")

    for index, file_key in enumerate(resume_keys):
        print("-" * 50)
        print(f"[STREAMING] Fetching and evaluating S3 file: {file_key}")
        
        # Download the raw candidate text from S3 directly into memory (no local file writing needed!)
        raw_resume_text = s3.download_file_to_string(file_key)
        
        initial_state = {
            "resume_raw": raw_resume_text,
            "resume_data": {},
            "jd_text": job_description,
            "similarity_score": 0.0,
            "insight": "",
            "matched_skills": []
        }

        # Invoke our agentic state graph
        final_state = app.invoke(initial_state)

        # Build leaderboard data (clean up file names for display)
        display_name = file_key.replace(".txt", "").title().replace("Candidate_", "").replace("_", " ")
        final_leaderboard_data.append({
            "candidate": display_name,
            "score": final_state["similarity_score"],
            "skills": final_state["matched_skills"],
            "insight": final_state["insight"].strip()
        })

        # Keep a small 1-second pause just to keep the console output neat
        if index < len(resume_keys) - 1:
            print("[ORCHESTRATOR] Initializing next S3 evaluation stream...")
            time.sleep(1) 

    # Rank candidates by vector math similarity score
    ranked_leaderboard = sorted(final_leaderboard_data, key=lambda x: x["score"], reverse=True)

    # Output the live Cloud Leaderboard Dashboard
    print("\n" + "="*70)
    print("         AWS CLOUD-INTEGRATED AGENT CANDIDATE LEADERBOARD       ")
    print("="*70)
    for rank, candidate_node in enumerate(ranked_leaderboard, 1):
        print(f"Rank {rank}: {candidate_node['candidate']}")
        print(f" -> Mathematical Match Score: {candidate_node['score']}%")
        print(f" -> Identified Skills: {', '.join(candidate_node['skills']) if candidate_node['skills'] else 'None detected'}")
        print(f" -> Live Agent Recommendation:\n    \"{candidate_node['insight']}\"")
        print("-" * 70)

if __name__ == "__main__":
    run_agentic_pipeline()