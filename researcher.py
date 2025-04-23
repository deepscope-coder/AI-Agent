import os
import re
import json
import urllib.parse
from pathlib import Path
from typing import List
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from pydantic import BaseModel
import ollama

# --- Configs ---
FONT_PATH = "DejaVuSans.ttf"
MODEL_NAME = "llama2:latest"

# --- Utilities ---
def sanitize_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def duckduckgo_web_search(query: str, max_results: int = 5) -> List[str]:
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f"https://lite.duckduckgo.com/lite/?q={urllib.parse.quote(query)}"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = [a['href'] for a in soup.find_all("a", href=True)
                   if a['href'].startswith("http") and "duckduckgo.com" not in a['href']]
        return results[:max_results]
    except Exception as e:
        print(f"[!] Search error: {e}")
        return []

def extract_content(url: str) -> str:
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'aside']):
            element.decompose()
        return re.sub(r'\s+', ' ', ' '.join(soup.stripped_strings))[:50000]
    except Exception as e:
        print(f"[!] Extraction error: {e}")
        return ""

def summarize_text(text: str) -> str:
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": f"Summarize this:\n\n{text}"}]
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"[!] Summarization error: {e}")
        return ""

def save_to_pdf(text: str, path: Path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf.output(str(path))
    print(f"✅ PDF saved to {path}")

# --- Data Class ---
class ResearchResult(BaseModel):
    topic: str
    summary: str
    sources: List[str]
    documents: List[str]
    timestamp: str

# --- Main Class ---
class ResearchAssistant:
    def __init__(self, topic: str):
        self.topic = topic
        self.sanitized = sanitize_filename(topic)
        self.base_dir = Path("research") / self.sanitized
        self.docs_dir = self.base_dir / "documents"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(exist_ok=True)
        self.result = ResearchResult(topic=topic, summary="", sources=[], documents=[], timestamp=str(datetime.now()))

    def run(self):
        print(f"🔎 Searching for: {self.topic}")
        urls = duckduckgo_web_search(self.topic, max_results=10)
        self.result.sources.extend(urls)

        for url in urls:
            content = extract_content(url)
            if content:
                domain = urllib.parse.urlparse(url).netloc
                filename = f"{sanitize_filename(domain)}_{datetime.now().strftime('%Y%m%d')}.txt"
                path = self.docs_dir / filename
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.result.documents.append(str(path))

        combined_text = ""
        for doc in self.result.documents:
            with open(doc, 'r', encoding='utf-8') as f:
                combined_text += f.read(10000) + "\n"

        print("🧠 Summarizing extracted content...")
        self.result.summary = summarize_text(combined_text)

        return self._export()

    def _export(self):
        json_path = self.base_dir / f"{self.sanitized}_report.json"
        pdf_path = self.base_dir / f"{self.sanitized}_report.pdf"

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.result.dict(), f, indent=2)
        print(f"✅ JSON saved at: {json_path}")

        pdf_text = f"Research Topic: {self.topic}\n\nSummary:\n{self.result.summary}\n\nSources:\n" + \
                   "\n".join(self.result.sources)
        save_to_pdf(pdf_text, pdf_path)

        return {
            "json": str(json_path),
            "pdf": str(pdf_path),
            "summary": self.result.summary
        }
