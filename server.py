from flask import Flask, request, render_template, send_file
import subprocess
import os
import tempfile
import uuid 

app = Flask(__name__, template_folder="app/templates")

# Define the name of the cookie file
COOKIES_FILE = "youtube_cookies.txt"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    if not url:
        return "No URL provided", 400

    # 1. Define a temporary file path with a unique name
    unique_filename = f"video_{uuid.uuid4()}.mp4"
    temp_filepath = os.path.join(tempfile.gettempdir(), unique_filename) 

    # Placeholder for the final filename that the user sees
    attachment_filename = "downloaded_video.mp4" 

    try:
        # 2. Run yt-dlp to download the file to the temp path
        subprocess.run(
            [
                "yt-dlp",
                "--no-playlist",
                # Pass the cookies file to bypass sign-in and rate limits
                "--cookies", COOKIES_FILE, 
                "-o", temp_filepath, # Output to the temporary path
                url
            ],
            check=True, 
            capture_output=True,
            text=True
        )

        # 3. Serve the file to the browser
        response = send_file(
            temp_filepath,
            as_attachment=True,
            download_name=attachment_filename,
            mimetype="video/mp4" 
        )
        
        return response

    except subprocess.CalledProcessError as e:
        error_output = e.stderr or "No error details available."
        print(f"yt-dlp failed: {error_output}")
        # Return only the relevant error details to the frontend
        return f"Download failed. Error: {error_output.strip()}", 500
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"An unexpected server error occurred: {e}", 500

    finally:
        # 5. Cleanup: Delete the file from the container's disk
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            print(f"Cleaned up temporary file: {temp_filepath}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)