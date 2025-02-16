import os
from flask import Flask, request, jsonify
import io
from PyPDF2 import PdfReader
import json
from dotenv import load_dotenv
from controllers.user_controller import register_user, login_user, save_rl_data, get_rl_data
from controllers.flashcards_controller import get_flashcards, get_flashcard, add_flashcard, update_flashcard, delete_flashcard, find_similar_flashcards, add_flashcard_func
from controllers.performance_controller import get_performance, add_update_performance, delete_performance, get_q_table, log_user_performance, get_recommended_flashcards, update_q_table, get_top_failed_flashcard
from utils.db import db
from api.gpt import question
from flask_cors import CORS
import random
from openai import OpenAI


app = Flask(__name__)
CORS(app)

chats = {}

# Load environment variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

def question_review():
    """
    Generates a new flashcard based on recommended flashcards for the user.
    Expects:
      - "chat_id" to maintain conversation context.
      - "user_id" for personalized recommendations.
    Returns:
      - The generated flashcards, recommended flashcards used, and the ID of the newly generated flashcard.
    """

    chat_id = request.form.get("chat_id", None)
    user_id = request.form.get("user_id", None)

    if not chat_id:
        return jsonify({"error": "Missing chat_id."}), 400
    if not user_id:
        return jsonify({"error": "Missing user_id."}), 400

    # 1. Fetch Recommended Flashcards
    recommended_flashcards = get_recommended_flashcards(user_id)
    print(recommended_flashcards)
    if not recommended_flashcards:
        return jsonify({"error": "No recommended flashcards found for this user."}), 400

    # 2. Format Data for GPT
    formatted_recommendations = "\n".join([
        f"- Q: {fc['question']} A: {fc.get('answer', 'N/A')}" for fc in recommended_flashcards
    ])

    # 3. Prepare ChatGPT prompt
    system_prompt = (
        "You are an AI that generates a new, unique flashcard based on previous flashcards. "
        "Use the given recommended flashcards to generate a new, challenging question. "
        "Your output must be a valid JSON array containing one or more flashcard objects. Each flashcard object "
        "must have exactly the following keys: 'question', 'topic', and 'difficulty'. "
        "Output ONLY valid JSON that can be decoded using json.loads() and do NOT include any Markdown formatting (e.g., no triple backticks). "
        "Do not include any additional keys or text. Here is an example format:\n"
        "[\n"
        "  {\n"
        "    \"question\": \"What is the significance of backpropagation in neural networks?\",\n"
        "    \"topic\": \"Machine Learning\",\n"
        "    \"difficulty\": \"Medium\"\n"
        "  }\n"
        "]"
    )

    user_prompt = f"Here are previous flashcards:\n{formatted_recommendations}\nGenerate a new flashcard."

    # Maintain chat history
    if chat_id not in chats:
        chats[chat_id] = [{"role": "system", "content": system_prompt}]
    chats[chat_id].append({"role": "user", "content": user_prompt})

    # 4. Call ChatGPT
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=chats[chat_id],
    )
    assistant_reply = response.choices[0].message.content

    # Debug Print
    print("\n============ GPT Reply ============")
    print(f"""\"\"\"{assistant_reply}\"\"\"""")
    print("===================================\n")

    # Remove Markdown formatting if present
    assistant_reply = assistant_reply.strip()
    if assistant_reply.startswith("```"):
        lines = assistant_reply.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        assistant_reply = "\n".join(lines).strip()

    # 5. Parse JSON flashcard
    try:
        new_flashcards = json.loads(assistant_reply)
        if not isinstance(new_flashcards, list):
            raise ValueError("Expected a JSON array of flashcards.")
        new_flashcard = new_flashcards[0]
        if not isinstance(new_flashcard, dict) or "question" not in new_flashcard:
            raise ValueError("Invalid flashcard format received.")

        # 6. Insert the new flashcard into the database
        resp, status_code = add_flashcard_func(new_flashcard)
        if status_code != 201:
            return jsonify({"error": "Failed to save the new flashcard."}), 500

        # Extract the flashcard ID from the response
        flashcard_id = resp.get("flashcard_id")

        new_flashcard["id"] = flashcard_id

        # 7. Return all original data plus the selected flashcard ID.
        return jsonify({
            "recommended_flashcards": recommended_flashcards,
            "selected_flashcard": new_flashcard,
        }), 200

    except (json.JSONDecodeError, ValueError) as e:
        return jsonify({
            "error": "Could not parse the generated flashcard JSON.",
            "raw_reply": assistant_reply,
            "exception": str(e)
        }), 500


def question_study():
    """
    Expects:
      - multipart/form-data with:
          - PDF files under the field "pdfs" (optional)
          - A "chat_id" to identify conversation
          - A "user_id" for personalized recommendations
          - A "user_request" to specify type of flashcards (e.g., multiple choice, word problems, specific topic)
    Generates flashcards via ChatGPT in JSON format, parses them, and
    stores each one in MongoDB using add_flashcard_func.
    Returns all generated flashcards, along with the complete data of one randomly selected flashcard and its ID.
    """
    
    chat_id = request.form.get("chat_id", None)
    user_id = request.form.get("user_id", None)
    user_request = request.form.get("user_request", "").strip()

    if not chat_id:
        return jsonify({"error": "Missing chat_id."}), 400
    if not user_id:
        return jsonify({"error": "Missing user_id."}), 400

    # 1. Extract PDFs (if provided)
    extracted_text = ""
    if "pdfs" in request.files:
        files = request.files.getlist("pdfs")
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

    if not extracted_text.strip() and not user_request:
        return jsonify({"error": "No PDFs provided and no user request specified."}), 400

    # 2. Construct GPT prompt with updated system prompt
    system_prompt = (
        "You are a helpful AI that generates flashcards. Based on the provided content and user request, create 10 flashcards in JSON format. "
        "Each flashcard must contain exactly the following keys: 'question', 'topic', and 'difficulty'. "
        "Ensure the flashcard questions are varied, unique, and effective for student practice, covering as much of the provided PDF content as possible. "
        "IMPORTANT: Your output must be exactly a valid JSON array that can be decoded using json.loads(). DO NOT include any Markdown formatting, "
        "such as triple backticks (```), language specifiers, or any extra text. "
        "The output should look exactly like this (with 10 flashcard objects in the array):\n"
        "[\n"
        "  {\n"
        "    \"question\": \"What is the significance of backpropagation in neural networks?\",\n"
        "    \"topic\": \"Machine Learning\",\n"
        "    \"difficulty\": \"Medium\"\n"
        "  }\n"
        "]\n"
        "Output only the JSON array and nothing else."
    )

    prompt_content = extracted_text if extracted_text.strip() else ""
    if user_request:
        prompt_content += f"\n\nUser Request: {user_request}"

    if chat_id not in chats:
        chats[chat_id] = [{"role": "system", "content": system_prompt}]
    chats[chat_id].append({"role": "user", "content": prompt_content})

    # 3. Call ChatGPT
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=chats[chat_id],
    )
    assistant_reply = response.choices[0].message.content
    chats[chat_id].append({"role": "assistant", "content": assistant_reply})

    print("\n============ GPT Reply ============")
    print(f"""\"\"\"{assistant_reply}\"\"\"""")
    print("===================================\n")

    # 4. Parse JSON flashcards
    try:
        flashcards = json.loads(assistant_reply)
        if not isinstance(flashcards, list):
            raise ValueError("Expected a JSON array of flashcards.")

        # 5. Insert each flashcard into the DB using add_flashcard_func
        for fc in flashcards:
            resp, status_code = add_flashcard_func(fc)
            fc['id'] = resp
            if status_code != 201:
                # Optionally log failures here.
                pass

        # 6. Randomly select one flashcard from the generated list
        selected_flashcard = random.choice(flashcards) if flashcards else None
        if not selected_flashcard:
            return jsonify({"error": "No flashcard generated."}), 500

        # 7. Return all generated flashcards along with the complete data of the selected flashcard and its ID.
        return jsonify({
            "flashcards": flashcards,
            "selected_flashcard": selected_flashcard,
        }), 200

    except (json.JSONDecodeError, ValueError) as e:
        return jsonify({
            "error": "Could not parse JSON flashcards from GPT response.",
            "raw_reply": assistant_reply,
            "exception": str(e)
        }), 500



 
def question():
    """
    Expects:
      - multipart/form-data with:
          - PDF files under the field "pdfs"
          - A "chat_id" to identify conversation
          - A "user_id" for personalized recommendations
          - Optional "user_request" field
    Generates flashcards via ChatGPT in JSON format, parses them, and
    stores each one in MongoDB using add_flashcard_func.
    Also recommends a flashcard using Q-learning.
    """
    chat_id = request.form.get("chat_id", None)
    user_id = request.form.get("user_id", None)
 
    if not chat_id:
        return jsonify({"error": "Missing chat_id."}), 400
    if not user_id:
        return jsonify({"error": "Missing user_id."}), 400

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
        flashcard_ids = []  # Store flashcard IDs
        for fc in flashcards:
            resp, status_code = add_flashcard_func(fc)
            if status_code == 201:
                flashcards_added += 1
                flashcard_ids.append(resp["flashcard_id"])  # Store ID

        # 6. Get a recommended flashcard for the user
        print('here')
        recommended_flashcard = get_recommended_flashcards(user_id)
        print(recommended_flashcard)

        return jsonify({
            "flashcards_added": flashcards_added,
            "flashcards": flashcards,
            "recommended_flashcard": recommended_flashcard  # Includes flashcard ID
        }), 200

    except (json.JSONDecodeError, ValueError) as e:
        return jsonify({
            "error": "Could not parse JSON flashcards from GPT response.",
            "raw_reply": assistant_reply,
            "exception": str(e)
        }), 500

def answer():
    """
    Expects:
      - 'chat_id' to load the correct conversation.
      - 'user_id' user id
      - 'flashcard_id' to track Q-learning updates.
      - 'question' that the user is answering.
      - 'answer' provided by the user.

    GPT will determine if the answer is correct (no need for a separate correct answer input).
    Updates Q-learning table with:
      - "correct" or "incorrect" as action.
      - A fixed reward of 10.

    Returns JSON:
      - If correct: {"correct": true, "correct_answer": "Good job!"}
      - If incorrect: {"correct": false, "correct_answer": "... explanation ..."}
    """

    chat_id = request.form.get("chat_id", None)
    user_id = request.form.get("user_id", None)
    flashcard_id = request.form.get("flashcard_id", None)
    question_text = request.form.get("question", "").strip()
    user_answer = request.form.get("answer", "").strip()

    if not chat_id:
        return jsonify({"error": "Missing chat_id."}), 400
    if not user_id:
        return jsonify({"error": "Missing user_id."}), 400
    if not flashcard_id:
        return jsonify({"error": "Missing flashcard_id."}), 400
    if not question_text:
        return jsonify({"error": "Missing question."}), 400
    if not user_answer:
        return jsonify({"error": "Missing answer."}), 400

    # Ensure chat context exists
    if chat_id not in chats:
        return jsonify({"error": "Invalid chat_id. No previous conversation found."}), 400

    # GPT Validation Prompt
    verification_prompt = {
        "role": "system",
        "content": (
            "You are an AI assistant that checks whether a given answer is correct for a given question."
            "Analyze the provided answer based on the context of the question."
            "Return JSON ONLY with:"
            " - 'correct': true or false"
            " - 'correct_answer': If incorrect, provide an explanation. If correct, say 'Good job!'"
            "Do NOT include any markdown formatting or extra text."
            "VALID JSON USABLE WITH json.loads()"
        )
    }

    chats[chat_id].append({
        "role": "user",
        "content": f"Question: {question_text}\nUser Answer: {user_answer}"
    })

    # Call ChatGPT to verify the answer
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[verification_prompt] + chats[chat_id],
    )

    assistant_reply = response.choices[0].message.content
    chats[chat_id].append({"role": "assistant", "content": assistant_reply})

    # Debug print
    print("\n============ Answer Check ============")
    print(f"""\"\"\"{assistant_reply}\"\"\"""")
    print("===================================\n")

    # Parse GPT response
    try:
        answer_feedback = json.loads(assistant_reply)

        if "correct" not in answer_feedback:
            raise ValueError("Invalid JSON response from GPT.")

        # Determine Q-learning action
        action = "correct" if answer_feedback["correct"] else "incorrect"

        # Update Q-table with reward = 10
        update_q_table(user_id, flashcard_id, action, reward=10)

        return jsonify(answer_feedback), 200

    except (json.JSONDecodeError, ValueError) as e:
        return jsonify({
            "error": "Could not parse the answer validation response.",
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


app.add_url_rule('/question/review', 'question_review', question_review, methods=['POST'])
app.add_url_rule('/question/study', 'question_study', question_study, methods=['POST'])
app.add_url_rule('/question', 'question', question, methods=['POST'])
app.add_url_rule('/answer', 'answer', answer, methods=['POST'])

# Register routes from performance_controller
app.add_url_rule('/performance/<user_id>', 'get_performance', get_performance, methods=['GET'])
app.add_url_rule('/performance/<user_id>', 'add_update_performance', add_update_performance, methods=['POST', 'PUT'])
app.add_url_rule('/performance/<user_id>', 'delete_performance', delete_performance, methods=['DELETE'])
app.add_url_rule('/performance/<user_id>/q_table', 'get_q_table', get_q_table, methods=['GET'])
app.add_url_rule('/performance/<user_id>/log', 'log_user_performance', log_user_performance, methods=['GET'])
# app.add_url_rule('/performance/<user_id>/recommendations', 'get_recommended_flashcards', get_recommended_flashcards, methods=['GET'])



if __name__ == "__main__":
    app.run(debug=True)
    
