from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os
import uuid

app = Flask(__name__)

DOWNLOAD_DIR = "/tmp"  # En Render, /tmp es la carpeta temporal permitida

@app.route("/info", methods=["POST"])
def get_info():
    """Devuelve los links directos de video y audio"""
    data = request.get_json()
    url = data.get("url")

    ydl_opts = {"skip_download": True, "quiet": True, "format": "best"}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = info.get("formats", [])
    video_links = []
    audio_links = []

    for f in formats:
        if f.get("vcodec") != "none" and f.get("acodec") != "none":
            video_links.append(f["url"])
        elif f.get("vcodec") == "none":
            audio_links.append(f["url"])

    return jsonify({
        "title": info.get("title"),
        "duration": info.get("duration"),
        "video_links": video_links,
        "audio_links": audio_links
    })


@app.route("/video", methods=["POST"])
def download_video():
    """Descarga y envía el video completo"""
    data = request.get_json()
    url = data.get("url")

    file_id = str(uuid.uuid4())[:8]
    output_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp4")

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": output_path,
        "quiet": True
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return send_file(output_path, as_attachment=True, download_name="video.mp4")


@app.route("/audio", methods=["POST"])
def download_audio():
    """Descarga y envía solo el audio"""
    data = request.get_json()
    url = data.get("url")

    file_id = str(uuid.uuid4())[:8]
    output_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp3")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "quiet": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return send_file(output_path, as_attachment=True, download_name="audio.mp3")


@app.route("/ping")
def ping():
    return "pong", 200


if __name__ == "__main__":
    # Render usa el puerto asignado en la variable PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)