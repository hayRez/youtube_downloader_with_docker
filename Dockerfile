FROM python:3.11-slim

# 1. Set the working directory
WORKDIR /app

# 2. Update package lists, install necessary dependencies (curl, ffmpeg), and clean up
# ffmpeg is essential for yt-dlp to handle various video formats and re-muxing.
RUN apt-get update \
    && apt-get install -y curl ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Download and install yt-dlp
# Installing it to /usr/local/bin ensures it's available system-wide.
RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp \
    -o /usr/local/bin/yt-dlp \
    && chmod a+x /usr/local/bin/yt-dlp

# 4. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the application code
# Assuming your Flask app (server.py) and templates are in the current directory
COPY . .

# 6. Expose the port (Render often handles this automatically, but it's good practice)
EXPOSE 5000

# 7. Start the application
# Ensure your Flask app runs on host="0.0.0.0" to be accessible inside the container
CMD ["python", "server.py"]