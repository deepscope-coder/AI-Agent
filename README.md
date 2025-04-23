# 🧠 AI-Agent – Automated Research Assistant

**AI-Agent** is your intelligent research companion. Just enter a topic, and it’ll:
- 🔎 Search the web
- 📄 Extract relevant content
- 🧠 Summarize it using LLM (via Ollama + LLaMA2)
- 📂 Export clean reports (PDF & JSON)

Perfect for quick knowledge gathering, report generation, or automating repetitive research tasks.

---

## 🚀 Features

- 🌐 Web search powered by DuckDuckGo
- 🧠 LLM summarization (LLaMA2 via Ollama)
- 🧾 Auto-generated PDF and JSON reports
- ⚡ Flask-based web interface – easy to use
- 🎨 Clean and minimal design

---

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/AI-Agent.git
   cd AI-Agent


Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate


Install dependencies
pip install -r requirements.txt

Run Ollama (if not running already)
ollama run llama2

Start the Flask app
python app.py

