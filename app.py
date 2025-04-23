from flask import Flask, render_template, request, send_from_directory
from researcher import ResearchAssistant
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        if not topic:
            return render_template("index.html", error="Please enter a topic.")
        
        assistant = ResearchAssistant(topic)
        paths = assistant.run()

        return render_template("result.html", topic=topic, summary=paths['summary'], 
                               json_path=paths['json'], pdf_path=paths['pdf'])

    return render_template("index.html")

@app.route("/download/<path:filename>")
def download_file(filename):
    directory = os.path.dirname(filename)
    name = os.path.basename(filename)
    return send_from_directory(directory, name, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
