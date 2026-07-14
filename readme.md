# ⚙️ TalentGraph AI: Asynchronous Multi-Agent Resume Screening System

TalentGraph AI is an enterprise-grade, cloud-integrated AI screening system built to optimize talent acquisition and candidate feedback loops. The system leverages **LangGraph** to coordinate specialized AI agent nodes, utilizing mathematical multi-dimensional vector embeddings and **Llama 3.3** to rank and evaluate resumes against target job descriptions in real-time.

---

## 🚀 Key Features

* **Dual-Target Architecture:** * **👤 Candidate Mode (In-Memory Evaluation):** Designed for job seekers to upload a single resume (PDF/TXT) and receive brutally honest, structured critique and actionable bullet-point upgrades to optimize their profile.
  * **💼 HR / Recruiter Mode (Cloud Batch Screening):** Connected directly to an **AWS S3 data lake** to download, evaluate, and output a mathematically sorted leaderboard ranking hundreds of candidates against a dynamic Job Description.
* **State-Driven Multi-Agent Flow:** Orchestrated using a cyclic state-machine to manage shared memory states between specialized parser and evaluator agents.
* **Hybrid Scoring Engine:** Combines dense semantic similarity scores using **Sentence-Transformer embeddings** with traditional, deterministic token keyword tracking.
* **Cloud-Native Decoupling:** Decouples compute from storage by leveraging **AWS S3** for secure, in-memory stream processing.

---

## 🛠️ Technical Stack

* **Frontend:** Streamlit, PyPDF (`pypdf`)
* **AI Orchestration:** LangGraph, LangChain Core
* **Core LLM:** Llama 3.3 (via Groq Cloud API)
* **Math Matching:** Sentence-Transformers (Hugging Face Hub), Cosine Similarity Math
* **Cloud Storage:** AWS S3, Boto3 (Python SDK)
* **Environment Security:** Python-Dotenv

---

## ⚙️ Installation & Local Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/Arish010/talentgraph-ai.git](https://github.com/Arish010/talentgraph-ai.git)
cd talentgraph-ai
```

### 2. Configure Environment Secrets
Create an uncommitted file named strictly .env in the root directory to store your private developer console access keys:
GROQ_API_KEY=your_groq_api_key_here
AWS_ACCESS_KEY_ID=your_aws_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
AWS_DEFAULT_REGION=eu-west-2

### 3. Initialize and Launch the Application
Install all frozen core pipeline dependencies and spin up the local web deployment application container:

Bash
pip install -r requirements.txt
streamlit run app.py


## Creator
## Designed, Engineered, and Maintained by 
# Arish Abdulgani Shaikh
