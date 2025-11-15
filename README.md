# YouTube Video Downloader (Docker + Flask + yt-dlp)

A simple web-based YouTube downloader powered by:

-   **Flask** (Web UI)
-   **yt-dlp** (Video downloader)
-   **Docker** (Containerized environment)

Paste a YouTube link into the webpage, and the container will download
the video directly to your host machine.

------------------------------------------------------------------------

## Features

✔ Simple web interface\
✔ Runs fully inside Docker\
✔ Downloads saved to your host machine\
✔ Supports YouTube videos, Shorts, and more\
✔ Automatically avoids playlist bulk downloads (`--no-playlist`)

------------------------------------------------------------------------

## Project Structure

    .
    ├── Dockerfile
    ├── docker-compose.yml
    ├── requirements.txt
    ├── server.py
    ├── app/
    │   └── templates/
    │       └── index.html
    └── downloads/   <- downloaded videos appear here

------------------------------------------------------------------------

# How to Run

## 1. Clone the repository

``` bash
git clone https://github.com/hayRez/youtube_downloader_with_docker.git
cd yourrepo
```

------------------------------------------------------------------------

## 2. Build and start the container

``` bash
docker compose up --build
```

Docker will:

-   Build the image (Flask + yt-dlp + ffmpeg)
-   Start the Flask web server on **port 8080**
-   Mount the `downloads/` folder to store videos

------------------------------------------------------------------------

## 3. Open the web interface

Open your browser:

👉 **http://localhost:8080**

------------------------------------------------------------------------

## 4. Download a video

1.  Paste a YouTube link into the form\
2.  Click **Download**\
3.  The video will appear inside the **downloads/** folder

Example:

    https://www.youtube.com/watch?v=VIDEO_ID

The app downloads **only one video**, even if it's part of a playlist.

------------------------------------------------------------------------

## Stop the server

Press:

    CTRL + C

To clean up:

``` bash
docker compose down
```

------------------------------------------------------------------------

## License

MIT
