# Real-Time-Narratives-Automated-Recaps
# Real-Time Football Narratives & Automated Recaps Engine

An AI-powered real-time sports commentary and post-match automated recap engine. This project bypasses cloud-heavy infrastructure (like Azure) in favor of a fast, lightweight Python stack suitable for Innovation Studios and local sandboxes.

## 🛠️ Tech Stack
- **Frontend/Dashboard:** Streamlit (Local Web UI)
- **Orchestration:** LangChain
- **LLM Engine:** OpenAI GPT-4o (or local Ollama/Llama3)
- **Data Engine:** Python Pandas (Simulating live Opta/StatsBomb match feeds)

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd football-narratives-engine
   ```

2. **Install Dependencies:**
   ```bash
   pip install streamlit langchain-openai pandas
   ```

3. **Configure Environment Variables:**
   ```bash
   # On macOS/Linux
   export OPENAI_API_KEY="your-api-key-here"

   # On Windows (CMD)
   set OPENAI_API_KEY="your-api-key-here"
   ```

## 🏃 How to Run Locally
Execute the Streamlit application:
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser to interact with the real-time simulation feed.
