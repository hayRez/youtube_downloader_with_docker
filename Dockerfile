
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update &&     apt-get install -y curl ffmpeg &&     apt-get clean

RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp     -o /usr/local/bin/yt-dlp && chmod a+x /usr/local/bin/yt-dlp

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

VOLUME ["/downloads"]

CMD ["python", "server.py"]
