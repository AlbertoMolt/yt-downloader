FROM python:3.11-slim

LABEL maintainer="AlbertoMoltrasio"
LABEL description="Universal Video Downloader"

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/downloads /app/logs

ENV PORT=6776 \
    MAX_STORAGE_MB=512.0 \
    COOKIES_FILE="" \
    PYTHONUNBUFFERED=1

EXPOSE ${PORT}

RUN echo '#!/bin/sh\n\
import json\n\
import os\n\
\n\
config = {\n\
    "port": int(os.getenv("PORT", 6776)),\n\
    "mb_max_storage_size": float(os.getenv("MAX_STORAGE_MB", 512.0)),\n\
    "yt_cookies_path": os.getenv("COOKIES_FILE", "")\n\
}\n\
\n\
with open("/app/config.json", "w") as f:\n\
    json.dump(config, f, indent=4)\n\
\n\
print("Config generated:")\n\
print(json.dumps(config, indent=2))\n\
' > /app/generate_config.py

CMD python /app/generate_config.py && python app.py
