from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL

app = Flask(__name__)

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")

    ydl_opts = {"skip_download": True, "quiet": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return jsonify(info)

@app.route("/ping")
def ping():
    return "pong",200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)