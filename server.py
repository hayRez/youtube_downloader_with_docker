from flask import Flask, request, render_template, send_file
import subprocess
import os
import tempfile
import uuid 
import glob # Used to find the file created by yt-dlp

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

    # 1. Define a temporary file name TEMPLATE using %(ext)s
    # We use a unique ID prefix (first 8 hex chars) for easy searching later.
    unique_id_prefix = uuid.uuid4().hex[:8]
    filename_template = os.path.join(tempfile.gettempdir(), f"{unique_id_prefix}_video.%(ext)s")
    
    # Placeholder for the final filename that the user sees in their browser
    attachment_filename = "downloaded_video.mp4" 
    
    # This variable will store the actual path to the file yt-dlp creates for cleanup
    actual_file_path = None 

    try:
        # 2. Run yt-dlp to download and explicitly mux (combine) streams
        # -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/best: Selects the best streams and merges them.
        # --merge-output-format mp4: Forces the final container format to be MP4.
        subprocess.run(
            [
                "yt-dlp",
                "--no-playlist",
                "--cookies", COOKIES_FILE,
                "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best", 
                "--merge-output-format", "mp4", 
                "-o", filename_template, # Use the template here
                url
            ],
            check=True, 
            capture_output=True,
            text=True
        )
        
        # 3. DISCOVERY: Find the actual file path created by yt-dlp
        # We search the /tmp directory for any file starting with our unique ID prefix.
        search_pattern = os.path.join(tempfile.gettempdir(), f"{unique_id_prefix}_video.*")
        found_files = glob.glob(search_pattern)
        
        if not found_files:
             # If yt-dlp exited successfully (return code 0) but no file was created.
             raise RuntimeError(
                 f"Download succeeded but no output file found. Check yt-dlp's exit logs for potential muxing warnings."
             )
        
        # Assume the first found file is the one we want
        actual_file_path = found_files[0]

        # 4. Serve the file to the browser
        response = send_file(
            actual_file_path,
            as_attachment=True,
            download_name=attachment_filename,
            mimetype="video/mp4" 
        )
        
        return response

    except subprocess.CalledProcessError as e:
        # **Catches yt-dlp failures**
        error_output = e.stderr or "No specific error message provided by yt-dlp."
        print(f"yt-dlp Failed (Exit Code {e.returncode}): {error_output}")
        return f"Download Failed (yt-dlp Error): {error_output.strip()}", 500

    except Exception as e:
        # Catches other system errors (like the RuntimeError we manually raised)
        print(f"An unexpected server error occurred: {e}")
        return f"An unexpected server error occurred: {e}", 500

    finally:
        # 5. Cleanup: Delete the file from the container's disk
        if actual_file_path and os.path.exists(actual_file_path):
            os.remove(actual_file_path)
            print(f"Cleaned up temporary file: {actual_file_path}")
        # Note: No need for 'elif' cleanup here; the primary cleanup is robust enough.

# NOTE: The app.run() block is REMOVED to let Gunicorn start the application.