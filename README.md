# Universal Video Downloader

Download videos from 1000+ platforms in different formats and qualities.

## Supported Platforms
YouTube, Vimeo, Twitter/X, Instagram, TikTok, Twitch, Facebook, Reddit, Dailymotion, and [1000+ more sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

## Features
- 🌐 Support for 1000+ video platforms
- 🎬 Select video and audio quality separately
- 🎨 Modern UI with smooth animations
- ⚡ Fast downloads powered by yt-dlp

## Installation
### 🐋 Docker
For install yt-downloader in docker go [here](README-DOCKER.md)
### 🐍 Native installation
```bash
pip install -r requirements.txt
python app.py
```

## Configuration
File config.json with this structure:
```json
{
    "port": 6776,
    "mb_max_storage_size": 512.0,
    "yt_cookies_path": "www.youtube.com_cookies.txt"
}
```
### Port
Here you define which port on yout server you want to use, by default is setted to 6776.
### Max storage size
Here you define how much content "cache" space you want to store before it is deleted if it is exceeded.
### YouTube cookies path
If you want to download from YouTube, which requires authentication, you need to define a text file with your cookies.
An easy way to get the cookies is by using the Chrome extension "Get cookies.txt LOCALLY"

###

## Usage
1. Paste any video URL from supported platforms
2. Choose video and/or audio format
3. Download!

## Note
⚠️ Please note that this project is being developed by someone with limited skill; please be patient.

Respect copyright and terms of service of each platform.
