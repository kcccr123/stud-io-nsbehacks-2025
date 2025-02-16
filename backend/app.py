import os
from flask import Flask, request, jsonify
import io
from PyPDF2 import PdfReader
import json
from dotenv import load_dotenv
from controllers.user_controller import register_user, login_user, save_rl_data, get_rl_data
from controllers.flashcards_controller import get_flashcards, get_flashcard, add_flashcard, update_flashcard, delete_flashcard, find_similar_flashcards, add_flashcard_func
from controllers.performance_controller import get_performance, add_update_performance, delete_performance, get_q_table, log_user_performance, get_recommended_flashcards
from utils.db import db
from api.gpt import question

app = Flask(__name__)

chats = {}

# Load environment variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

def question():
    """
    Expects:
      - multipart/form-data with:
          - PDF files under the field "pdfs"
          - A "chat_id" to identify conversation
          - Optional "user_request" field
    Generates flashcards via ChatGPT in JSON format, parses them, and
    stores each one in MongoDB using add_flashcard_func.
    """
    chat_id = request.form.get("chat_id", None)
    if not chat_id:
        return jsonify({"error": "Missing chat_id."}), 400

    # 1. Initialize conversation if needed
    if chat_id not in chats:
        chats[chat_id] = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that processes PDF documents and extracts information. "
                    "Generate 10 flashcards in valid JSON format, with each flashcard containing "
                    "the keys: question, answer, topic, difficulty. Return ONLY VALID JSON, WHICH CAN BE USED WITH json.loads() e.g.:\n"
                    "without any Markdown code block formatting. Do NOT include ```json or ```."
                    "[\n  {\n    \"question\": \"...\",\n   \"topic\": \"...\",\n    \"difficulty\": \"...\"\n  },\n  ...\n]"
                )
            }
        ]

    user_request = request.form.get("user_request", "").strip()

    # 2. Extract PDFs
    if "pdfs" not in request.files:
        return jsonify({"error": "No PDFs uploaded. Include files with key 'pdfs'."}), 400

    files = request.files.getlist("pdfs")
    if not files:
        return jsonify({"error": "No PDF files found."}), 400

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

    chats[chat_id].append({"role": "user", "content": user_content})

    # 3. Call ChatGPT
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=chats[chat_id],
    )
    assistant_reply = response.choices[0].message.content
    chats[chat_id].append({"role": "assistant", "content": assistant_reply})

    # Debug print
    print("\n============ GPT Reply ============")
    print(f"""\"\"\"{assistant_reply}\"\"\"""")
    print("===================================\n")

    # 4. Parse JSON flashcards
    try:
        flashcards = json.loads(assistant_reply)
        if not isinstance(flashcards, list):
            raise ValueError("Expected a JSON array of flashcards.")

        # 5. Insert each flashcard into the DB using the new function
        flashcards_added = 0
        for fc in flashcards:
            resp, status_code = add_flashcard_func(fc)
            if status_code == 201:
                flashcards_added += 1

        return jsonify({
            "flashcards_added": flashcards_added,
            "flashcards": flashcards
        }), 200

    except (json.JSONDecodeError, ValueError) as e:
        return jsonify({
            "error": "Could not parse JSON flashcards from GPT response.",
            "raw_reply": assistant_reply,
            "exception": str(e)
        }), 500



try:
    db.command('ping')
    print("Successfully connected to the database")
except Exception as e:
    print("Failed to connect to the database:", e)

# Register routes from user_controller
app.add_url_rule('/users/register', 'register_user', register_user, methods=['POST'])
app.add_url_rule('/users/login', 'login_user', login_user, methods=['POST'])
app.add_url_rule('/users/<user_id>/rl', 'save_rl_data', save_rl_data, methods=['POST'])
app.add_url_rule('/users/<user_id>/rl', 'get_rl_data', get_rl_data, methods=['GET'])

# Register routes from flashcards_controller
app.add_url_rule('/flashcards', 'get_flashcards', get_flashcards, methods=['GET'])
app.add_url_rule('/flashcards/<flashcard_id>', 'get_flashcard', get_flashcard, methods=['GET'])
app.add_url_rule('/flashcards', 'add_flashcard', add_flashcard, methods=['POST'])
app.add_url_rule('/flashcards/<flashcard_id>', 'update_flashcard', update_flashcard, methods=['PUT'])
app.add_url_rule('/flashcards/<flashcard_id>', 'delete_flashcard', delete_flashcard, methods=['DELETE'])
app.add_url_rule('/flashcards/similar', 'find_similar_flashcards', find_similar_flashcards, methods=['GET'])

app.add_url_rule('/question', 'question', question, methods=['POST'])

# Register routes from performance_controller
app.add_url_rule('/performance/<user_id>', 'get_performance', get_performance, methods=['GET'])
app.add_url_rule('/performance/<user_id>', 'add_update_performance', add_update_performance, methods=['POST', 'PUT'])
app.add_url_rule('/performance/<user_id>', 'delete_performance', delete_performance, methods=['DELETE'])
app.add_url_rule('/performance/<user_id>/q_table', 'get_q_table', get_q_table, methods=['GET'])
app.add_url_rule('/performance/<user_id>/log', 'log_user_performance', log_user_performance, methods=['GET'])
app.add_url_rule('/performance/<user_id>/recommendations', 'get_recommended_flashcards', get_recommended_flashcards, methods=['GET'])



if __name__ == "__main__":
    app.run(debug=True)
