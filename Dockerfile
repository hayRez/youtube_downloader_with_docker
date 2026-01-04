FROM python:3.11-slim

WORKDIR /app

# 1. Install Dependencies (ffmpeg, curl, AND unzip)
# We add 'unzip' here to satisfy the Deno installer requirement.
RUN apt-get update \
    && apt-get install -y curl ffmpeg unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Deno (JavaScript runtime)
RUN curl -fsSL https://deno.land/install.sh | sh
# Ensure deno is accessible on the PATH for yt-dlp
ENV PATH="/root/.deno/bin:$PATH"

# 3. Install yt-dlp
RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp \
    -o /usr/local/bin/yt-dlp \
    && chmod a+x /usr/local/bin/yt-dlp

# 4. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the application code AND the cookies file
COPY . .

EXPOSE 5000

# 6. Start the application
CMD ["python", "server.py"]