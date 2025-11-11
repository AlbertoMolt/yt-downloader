import os
import yt_dlp
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

def my_hook(d):
    if d['status'] == 'downloading':
        porcentaje = d['_percent_str']
        print("Progreso:", porcentaje)
    elif d['status'] == 'finished':
        print("Completado:", d['filename'])

def get_info_video(url):
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
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/startDownload', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    
    video_format_id = data.get('video_format_id')
    audio_format_id = data.get('audio_format_id')
    
    format = f'{video_format_id}+{audio_format_id}'
    
    if video_format_id == "none":
        format = f'{audio_format_id}'
    
    if audio_format_id == "none":
        format = f'{video_format_id}'
    
    try:
        filename_template = '%(title)s - [%(format)s].%(ext)s'
        
        ydl_opts = {
            'format': format,
            'quiet': True,
            'outtmpl': f'downloads/{filename_template}',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            filename = ydl.prepare_filename(info)
            filename_clean = os.path.basename(filename)

            ydl.download([url])
                        
        return jsonify({
            "success": True,
            "filename": filename_clean
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@app.route('/api/download/<path:filename>')
def download_file(filename):
    try:
        filepath = os.path.join('downloads', filename)
        
        if not os.path.exists(filepath):
            safe_filename = secure_filename(filename)
            filepath = os.path.join('downloads', safe_filename)
            
            if not os.path.exists(filepath):
                return jsonify({"success": False, "error": "File not found"}), 404
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/')
def home():
    return render_template('index.html') 

if __name__ == "__main__":
    print("✅ Started")
    app.run(host="0.0.0.0", debug=True)