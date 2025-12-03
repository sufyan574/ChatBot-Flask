# Sufyan Ajmal
#SU92-BSAIM-F24-017

from flask import Flask, render_template, request, jsonify
import requests, os, base64
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")

# --- Config ---
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY in .env")

MODEL = os.getenv("MODEL", "gemini-2.5-flash")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

# In-memory chat history
chat_history = []

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True)
    message = data.get("message", "").strip()
    file_data = data.get("file")

    if not message and not file_data:
        return jsonify(error="Please provide a message or file."), 400

    # Handle file attachment
    user_text = message
    if file_data and file_data.get("data"):
        try:
            b64 = file_data["data"].split(",")[1]
            decoded = base64.b64decode(b64)
            file_info = f"[File attached: {file_data.get('mime_type', 'unknown')}, {len(decoded)} bytes]"
            user_text = f"{message}\n{file_info}" if message else file_info
        except Exception:
            return jsonify(error="Invalid file data."), 400

    # Include last 5 messages for context
    contents = chat_history[-5:] if chat_history else []
    contents.append({"role": "user", "parts": [{"text": user_text}]})

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 512
        }
    }

    try:
        res = requests.post(API_URL, headers={"Content-Type": "application/json"}, json=payload)
        res.raise_for_status()
        data = res.json()

        reply = (
            data.get("candidates", [{}])[0]
            .get("content", {} )
            .get("parts", [{}])[0]
            .get("text", "")
        )

        if not reply:
            return jsonify(error="Empty response from Gemini."), 500

        # Save chat history
        chat_history.extend([
            {"role": "user", "parts": [{"text": user_text}]},
            {"role": "model", "parts": [{"text": reply}]}
        ])

        return jsonify(response=reply.strip())

    except requests.exceptions.RequestException as e:
        return jsonify(error=f"API request failed: {e}"), 500

@app.route("/reset", methods=["POST"])
def reset():
    chat_history.clear()
    return jsonify(message="Chat history cleared.")

@app.route("/debug")
def debug():
    return jsonify(
        api_key=bool(API_KEY),
        model=MODEL,
        chat_history=len(chat_history)
    )

if __name__ == "__main__":
    app.run(debug=True)
