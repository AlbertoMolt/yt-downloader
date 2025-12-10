# 🐋Docker setup
## Build
```bash
mkdir downloads logs

curl -O https://raw.githubusercontent.com/AlbertoMolt/yt-downloader/main/docker-compose.yml

docker-compose up -d
```
## Config
Edit `docker-compose.yml` file.
### Port
```bash
ports:
    - "6776:6776"
environment:
    - PORT=6776
```
### Storage limit
Here you define how much content "cache" space you want to store before it is deleted if it is exceeded.
```bash
environment:
    - MAX_STORAGE_MB=1024.0
```
### Set YouTube cookies (Optional)
If you want to download from YouTube, which requires authentication, you need to define a text file with your cookies.

An easy way to get the cookies is by using the Chrome extension "Get cookies.txt LOCALLY":

1. Download the extension [here](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc).

2. Make sure you're logged in YouTube.

3. Open the extension and click in `Export`.

4. Save the cookies file into a folder.

```bash
volumes:
    - ./cookies/cookies.txt:/app/cookies.txt
environment:
    - COOKIES_FILE=/app/cookies.txt
```

## Config example
### Basic configuration
```yaml
version: '3.8'
services:
  yt-downloader:
    image: albertomoltrasio/yt-downloader:latest
    ports:
      - "6776:6776"
    volumes:
      - ./downloads:/app/downloads
      - ./logs:/app/logs
    restart: unless-stopped
```
### Complete configuration
```yaml
version: '3.8'
services:
  yt-downloader:
    image: albertomoltrasio/yt-downloader:latest
    container_name: my-video-downloader
    ports:
      - "6776:6776"
    volumes:
      - ./downloads:/app/downloads
      - ./logs:/app/logs
      - ./cookies/cookies.txt:/app/cookies.txt
    environment:
      - PORT=6776
      - MAX_STORAGE_MB=2048.0
      - COOKIES_FILE=/app/cookies.txt
    restart: unless-stopped
```
