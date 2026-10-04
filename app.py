from flask import Flask, request, send_file
from flask_cors import CORS
import edge_tts
import asyncio
import io

app = Flask(__name__)
CORS(app)


@app.route("/tts", methods=["POST"])
def tts():
    data = request.get_json()

    text = data.get("text", "").strip()
    voice = data.get("voice", "en-IN-NeerjaNeural")

    if not text:
        return {"error": "No text provided"}, 400

    async def generate():
        communicate = edge_tts.Communicate(text, voice)
        audio = io.BytesIO()

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio.write(chunk["data"])

        audio.seek(0)
        return audio

    audio = asyncio.run(generate())

    return send_file(
        audio,
        mimetype="audio/mpeg",
        as_attachment=False,
        download_name="speech.mp3"
    )


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
