from flask import Flask, request, render_template
import subprocess
import os

app = Flask(__name__, template_folder="app/templates")

DOWNLOAD_DIR = "/downloads"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    if not url:
        return "No URL provided", 400

    subprocess.run([
    "yt-dlp",
    "--no-playlist",
    "-o", f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
    url
])

    return f"Download complete for: {url}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
