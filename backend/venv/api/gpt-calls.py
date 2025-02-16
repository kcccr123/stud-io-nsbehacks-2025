import os
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import io
from PyPDF2 import PdfReader

# Load environment variables from .env if present
load_dotenv()

# Retrieve your API key from environment or set it directly (not recommended for production)
openai_api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

chats = {}  # Global dictionary to store chat contexts

@app.route("/question", methods=["POST"])
def question():
    """
    Expects:
      - multipart/form-data with:
          - One or more PDF files under the field name "pdfs"
          - A "chat_id" field to identify the conversation
          - An optional "user_request" field to specify how the user wants the question generated
            (e.g., "multiple choice," "focus on definitions," etc.)
    """
    # 1. Get chat_id from the request form (adjust as needed if using JSON or query param)
    chat_id = request.form.get("chat_id", None)
    if not chat_id:
        return jsonify({"error": "Missing chat_id."}), 400

    # 2. If this chat doesn't exist yet, initialize with a system prompt
    if chat_id not in chats:
        chats[chat_id] = [{
            "role": "system",
            "content": (
                "You are a helpful assistant that processes PDF documents and extracts information. "
                "Create a study question from the given material, while considering any user-specific requests."
            )
        }]

    # 3. Get the optional user_request
    user_request = request.form.get("user_request", "").strip()

    # 4. Get the PDFs from the request
    if "pdfs" not in request.files:
        return jsonify({"error": "No PDFs uploaded. Include files with key 'pdfs'."}), 400

    files = request.files.getlist("pdfs")
    if not files:
        return jsonify({"error": "No PDF files found."}), 400

    # 5. Extract text from each PDF
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

    # 6. Combine extracted PDF text and user's additional request into one message
    user_content = extracted_text
    if user_request:
        user_content += f"\n\nUser request: {user_request}"

    # 7. Append the user's message to the chat
    chats[chat_id].append({
        "role": "user",
        "content": user_content
    })

    # 8. Call the GPT API with the entire conversation
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=chats[chat_id],
    )

    # 9. Extract and store the new assistant reply
    assistant_reply = response.choices[0].message.content
    chats[chat_id].append({
        "role": "assistant",
        "content": assistant_reply
    })

    # 10. Print the assistant's reply (optional)
    print("\n" + "="*50)
    print("GPT Reply (triple-quoted):\n")
    print(f"""\"\"\"{assistant_reply}\"\"\"""")
    print("="*50 + "\n")

    # 11. Return the reply
    return jsonify({"reply": assistant_reply}), 200






@app.route("/test", methods=["POST"])
def test():
    # takes base64 encoded receipt and makes api call to chatGPT to decipher contents.
    client = OpenAI(
        api_key=openai_api_key,
    )

    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Missing 'question' in request body"}), 400

    question = data["question"]

    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions succinctly and accurately."
            },
            {
                "role": "user",
                "content": question
            }
        ],
    )

    # Extract the assistant's reply from the response
    assistant_reply = response.choices[0].message.content

    # Return the reply as JSON
    return jsonify({"reply": assistant_reply}), 200

@app.route("/", methods=["GET"])
def index():
    return "Flask server is running!"

if __name__ == "__main__":
    # Run the Flask server
    app.run(host="0.0.0.0", port=5000, debug=True)
