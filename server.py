from flask import Flask, request, render_template, send_file
import subprocess
import os
import tempfile
import uuid 
import shutil # Added for robust file path handling if needed, though os.path.join is fine

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
    
    # Initialize the variable to None outside the try block for cleanup purposes
    # Although temp_filepath is defined above, this is a good practice.
    file_to_cleanup = None 

    try:
        # 2. Run yt-dlp to download the file to the temp path
        # check=True raises CalledProcessError if yt-dlp returns a non-zero exit code
        result = subprocess.run(
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
        
        # 3. VERIFICATION: Check if the file was created.
        # If subprocess.run finished without error (check=True was OK), the file MUST exist.
        if not os.path.exists(temp_filepath):
             # This means yt-dlp exited successfully (return code 0) but didn't write the file.
             # This is extremely rare but possible; we treat it as an internal failure.
             raise RuntimeError(f"Download process succeeded, but output file was not found at {temp_filepath}.")

        file_to_cleanup = temp_filepath

        # 4. Serve the file to the browser
        response = send_file(
            file_to_cleanup,
            as_attachment=True,
            download_name=attachment_filename,
            mimetype="video/mp4" 
        )
        
        return response

    except subprocess.CalledProcessError as e:
        # **Catches yt-dlp failures** (e.g., video removed, geo-blocked, invalid URL)
        error_output = e.stderr or "No specific error message provided by yt-dlp."
        print(f"yt-dlp Failed (Exit Code {e.returncode}): {error_output}")
        # Return the actual yt-dlp error output to the user
        return f"Download Failed (yt-dlp Error): {error_output.strip()}", 500

    except Exception as e:
        # Catches other system errors (e.g., file system failure, Runtime Error above)
        print(f"An unexpected server error occurred: {e}")
        return f"An unexpected server error occurred: {e}", 500

    finally:
        # 5. Cleanup: Delete the file from the container's disk
        # We use temp_filepath here, which is set above the try block
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            print(f"Cleaned up temporary file: {temp_filepath}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)