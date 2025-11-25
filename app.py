import utils
import file_cleanup

from config import downloads_path

import os
import json
import yt_dlp
import logging
import urllib.parse

from werkzeug.utils import secure_filename
from logging.handlers import RotatingFileHandler
from flask_socketio import SocketIO
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

socketio = SocketIO(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'app.log', 
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

flask_port = None
yt_cookies_path = None

def init_config():
    global flask_port, yt_cookies_path
    
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
        
        flask_port = config['port']
        logger.info(f"Flask port configured: {flask_port}")
        
        if utils.check_file(config['yt_cookies_path']):
            yt_cookies_path = config['yt_cookies_path']
            logger.info(f"YouTube cookies file found: {yt_cookies_path}")
        else:
            logger.warning("YouTube cookies file not found")
    
    except Exception as e:
        logger.error(f"Error loading configuration: {e}", exc_info=True)
        raise
    
def progress_hook(d):
    if d['status'] == 'downloading':
        # Intentar obtener porcentaje de varias formas
        percentage = None
        
        if d.get('downloaded_bytes') and d.get('total_bytes'):
            percentage = int((d['downloaded_bytes'] / d['total_bytes']) * 100)
        elif d.get('_percent_str'):
            # yt-dlp ya calcula el porcentaje
            percentage = int(float(d['_percent_str'].strip('%')))
        
        if percentage is not None:
            logger.debug(f"Download progress: {percentage}%")
            socketio.emit('progress', {'percentage': percentage}, namespace='/download')
        
    elif d['status'] == 'finished':
        logger.info(f"Download completed: {d.get('filename', 'unknown')}")

def get_info_video(url):
    logger.info(f"Fetching video info for URL: {url}")
    
    v_formats = list()
    a_formats = list()

    with yt_dlp.YoutubeDL({'quiet': False}) as ydl:
        info = ydl.extract_info(url, download=False)
                
        title = info.get('title', None)
        extractor = info.get('extractor', None)
        thumbnail = info.get('thumbnail', None)
        
        for format in info['formats']:
            if format.get("acodec") == 'none' and format.get("vcodec") != 'none':
                if ("sb" not in format.get("format_id")):                    
                    video_dict = {
                        "format_id": format.get("format_id"),
                        "resolution": format.get("resolution"),
                        "filesize": format.get("filesize"),
                        "ext": format.get("ext"),
                        "fps": format.get("fps"),
                        "format_note": format.get("format_note"),
                        "vcodec": format.get("vcodec")
                    }
                    v_formats.append(video_dict)
                    
            if format.get("acodec") != 'none' and format.get("vcodec") == 'none':
                if ("sb" not in format.get("format_id")):
                    audio_dict = {
                        "format_id": format.get("format_id"),
                        "resolution": format.get("resolution"),
                        "filesize": format.get("filesize"),
                        "ext": format.get("ext"),
                        "format_note": format.get("format_note"),
                        "acodec": format.get("acodec")
                    }
                    a_formats.append(audio_dict)
            
    return title, extractor, thumbnail, v_formats, a_formats
        
@app.route('/api/format', methods=['POST'])
def get_video_info():
    data = request.get_json()
    url = data.get('url')
    
    logger.info(f"API request - Get format info for: {url}")
    
    try:
        title, extractor, thumbnail, video_formats, audio_formats = get_info_video(url)
        
        return jsonify({
            "success": True,
            "title": title,
            "extractor": extractor,
            "thumbnail": thumbnail,
            "video_formats": video_formats,
            "audio_formats": audio_formats
        })
    except Exception as e:
        logger.error(f"Error in get_video_info endpoint: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/startDownload', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc
    
    video_format_id = data.get('video_format_id')
    audio_format_id = data.get('audio_format_id')
    
    format = f'{video_format_id}+{audio_format_id}'
    
    if video_format_id == "none":
        format = f'{audio_format_id}'
    
    if audio_format_id == "none":
        format = f'{video_format_id}'
        
    logger.info(f"API request - Start download: {url}, Format: {format}")
        
    utils.check_or_create_downloads_path()
    
    yt_urls = ['youtube', 'youtu.be']
    
    if any(yt_url in domain for yt_url in yt_urls) and not yt_cookies_path:
        logging.error(f"Unable to download from {domain} due to missing cookies.", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Unable to download from " + domain + " due to missing cookies."
        }), 500
    
    try:
        filename_template = '%(title)s - [%(format)s].%(ext)s'
        
        ydl_opts = {
            'format': format,
            'quiet': True,
            'outtmpl': f'{downloads_path}/{filename_template}',
            'progress_hooks': [progress_hook],
            'noplaylist': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            filename = ydl.prepare_filename(info)
            filename_clean = os.path.basename(filename)
            
            file_path = f'{downloads_path}/{filename_clean}'
            
            if utils.check_file(file_path):
                logger.info(f"File: {filename_clean} found in disk, skipping download.")
                return jsonify({
                    "success": True,
                    "filename": filename_clean
                })
                
            filesize = info.get('filesize')
            
            logger.info(f"Preparing download - File: {filename_clean}, Size: {filesize} bytes")
            
            if (filesize):
                file_cleanup.make_space(filesize)
            else:
                logger.warning("File size unknown, skipping space check")
            
            ydl.download([url])
            
            logger.info(f"Download successful: {filename_clean}")
                        
        return jsonify({
            "success": True,
            "filename": filename_clean
        })
        
    except Exception as e:
        logger.error(f"Error during download: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@app.route('/api/download/<path:filename>')
def download_file(filename):
    logger.info(f"API request - Download file: {filename}")
    
    try:
        filepath = os.path.join(downloads_path, filename)
        
        if not os.path.exists(filepath):
            safe_filename = secure_filename(filename)
            filepath = os.path.join(downloads_path, safe_filename)
            
            if not os.path.exists(filepath):
                logger.warning(f"File not found: {filename}")
                return jsonify({"success": False, "error": "File not found"}), 404
        
        logger.info(f"Sending file: {filename}")
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error sending file: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/')
def home():
    return render_template('index.html') 

if __name__ == "__main__":
    logger.info("Starting application...")
    
    init_config()
    file_cleanup.check_space()
    
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    logger.info(f"Running Flask app on port {flask_port}, debug={debug_mode}")
    
    app.run(host="0.0.0.0", port=flask_port, debug=True)