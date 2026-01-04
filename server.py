from flask import Flask, request, render_template, send_file
import subprocess
import os
import tempfile
import uuid # For generating a unique filename

app = Flask(__name__, template_folder="app/templates")

@app.route("/")
def index():
    # Make sure 'app/templates/index.html' exists
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    if not url:
        return "No URL provided", 400

    # 1. Define a temporary file path with a unique name
    # We use a unique ID to prevent conflicts if multiple users download at once
    unique_filename = f"video_{uuid.uuid4()}.mp4"
    # tempfile.gettempdir() finds the system's temporary directory (safe on Render)
    temp_filepath = os.path.join(tempfile.gettempdir(), unique_filename) 

    # We use a placeholder for the final filename that the user sees
    # yt-dlp's output name is hard to predict, so we use a generic name for now
    attachment_filename = "downloaded_video.mp4" 

    try:
        # 2. Run yt-dlp to download the file to the temp path
        # The check=True argument ensures an error is raised if yt-dlp fails (e.g., due to geo-blocking)
        subprocess.run(
            [
                "yt-dlp",
                "--no-playlist",
                "-o", temp_filepath, # Output to the temporary path
                url
            ],
            check=True, # Important: Check for non-zero exit code
            capture_output=True,
            text=True
        )

        # 3. Serve the file to the browser
        # as_attachment=True tells the browser to download the file
        # attachment_filename sets the name of the downloaded file on the user's machine
        response = send_file(
            temp_filepath,
            as_attachment=True,
            download_name=attachment_filename, # This sets the filename for the user
            mimetype="video/mp4" # Set the correct MIME type
        )
        
        # 4. Return the response object
        return response

    except subprocess.CalledProcessError as e:
        # Handle yt-dlp errors (like Geo-blocking, missing URL, etc.)
        error_output = e.stderr or "No error details available."
        print(f"yt-dlp failed: {error_output}")
        return f"Download failed. Please check the URL or try again later. Error detail: {error_output}", 500
        
    except Exception as e:
        # Handle unexpected errors (e.g., file system issue)
        print(f"An unexpected error occurred: {e}")
        return f"An unexpected server error occurred: {e}", 500

    finally:
        # 5. Cleanup: This block always executes, even if an error occurs.
        # This prevents the container's disk from filling up.
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            print(f"Cleaned up temporary file: {temp_filepath}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)