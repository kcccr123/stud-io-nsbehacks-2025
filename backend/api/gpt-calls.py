import os
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import io
from PyPDF2 import PdfReader
import json

from controllers.flashcards_controller import add_flashcard  # <--- Your existing add_flashcard() function

# Load environment variables
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

# Store chat contexts if you want ongoing conversation
chats = {}

# -------------------------------------------------------------------
# No more 'create_flashcard_in_db' helper. We'll directly call add_flashcard().
# -------------------------------------------------------------------

@app.route("/question", methods=["POST"])
def question():
    """
    Expects:
      - multipart/form-data with:
          - One or more PDF files under the field name "pdfs"
          - A "chat_id" field to identify the conversation
          - An optional "user_request" field: e.g., "multiple choice," "focus on definitions," etc.
    """
    chat_id = request.form.get("chat_id", None)
    if not chat_id:
        return jsonify({"error": "Missing chat_id."}), 400

    # If this chat doesn't exist yet, initialize with a special system prompt
    if chat_id not in chats:
        chats[chat_id] = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that processes PDF documents and extracts information. "
                    "Generate multiple flashcards in valid JSON format, with each flashcard containing "
                    "the keys: question, answer, topic, difficulty. Return ONLY JSON, e.g.:\n"
                    "[\n  {\n    \"question\": \"...\",\n    \"answer\": \"...\",\n    \"topic\": \"...\",\n    \"difficulty\": \"...\"\n  },\n  ...\n]"
                )
            }
        ]

    user_request = request.form.get("user_request", "").strip()

    # Check for PDFs
    if "pdfs" not in request.files:
        return jsonify({"error": "No PDFs uploaded. Include files with key 'pdfs'."}), 400

    files = request.files.getlist("pdfs")
    if not files:
        return jsonify({"error": "No PDF files found."}), 400

    # Extract text from PDFs
    extracted_text = ""
    for file in files:
        if file.filename.lower().endswith(".pdf"):
            try:
                file_bytes = file.read()
                reader = PdfReader(io.BytesIO(file_bytes))
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += page_text + "\n"
            except Exception as e:
                return jsonify({"error": f"Error processing {file.filename}: {str(e)}"}), 500
        else:
            return jsonify({"error": f"File {file.filename} is not a PDF."}), 400

    if not extracted_text.strip():
        return jsonify({"error": "No text could be extracted from the uploaded PDFs."}), 400

    # Combine PDF text with user request
    user_content = extracted_text
    if user_request:
        user_content += f"\n\nUser request: {user_request}"

    # Add user content to chat
    chats[chat_id].append({"role": "user", "content": user_content})

    # Call OpenAI
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=chats[chat_id],
    )

    assistant_reply = response.choices[0].message.content
    chats[chat_id].append({"role": "assistant", "content": assistant_reply})

    # Print GPT's raw reply (for debugging)
    print("\n" + "="*50)
    print("GPT Reply (triple-quoted):\n")
    print(f"""\"\"\"{assistant_reply}\"\"\"""")
    print("="*50 + "\n")

    # Attempt to parse JSON flashcards
    try:
        flashcards = json.loads(assistant_reply)

        if not isinstance(flashcards, list):
            raise ValueError("Expected a JSON array of flashcards.")

        # For each flashcard, call add_flashcard() by simulating a POST request context
        flashcards_added = 0
        for fc in flashcards:
            # 'fc' is a dictionary like {"question": "...", "answer": "...", ...}

            # We must simulate a JSON request body for add_flashcard().
            with app.test_request_context(
                "/add_flashcard",
                method="POST",
                json=fc   # <--- The dictionary data will be available via request.get_json() inside add_flashcard()
            ):
                resp = add_flashcard()  # This calls your existing function, which uses request.get_json()
                if resp[1] == 201:
                    flashcards_added += 1

        return jsonify({"flashcards_added": flashcards_added, "flashcards": flashcards}), 200

    except (json.JSONDecodeError, ValueError) as e:
        # If GPT returned invalid JSON or the structure isn't what we expect
        return jsonify({
            "error": "Could not parse JSON flashcards from GPT response.",
            "raw_reply": assistant_reply,
            "exception": str(e)
        }), 500


@app.route("/", methods=["GET"])
def index():
    return "Flask server is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
