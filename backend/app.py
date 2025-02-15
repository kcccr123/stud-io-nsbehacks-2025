from flask import Flask
from controllers.user_controller import register_user, login_user, save_rl_data, get_rl_data
from controllers.flashcards_controller import get_flashcards, get_flashcard, add_flashcard, update_flashcard, delete_flashcard, find_similar_flashcards
from controllers.performance_controller import get_performance, add_update_performance, delete_performance, get_q_table, log_user_performance, get_recommended_flashcards
from utils.db import db

app = Flask(__name__)

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


# Register routes from performance_controller
app.add_url_rule('/performance/<user_id>', 'get_performance', get_performance, methods=['GET'])
app.add_url_rule('/performance/<user_id>', 'add_update_performance', add_update_performance, methods=['POST', 'PUT'])
app.add_url_rule('/performance/<user_id>', 'delete_performance', delete_performance, methods=['DELETE'])
app.add_url_rule('/performance/<user_id>/q_table', 'get_q_table', get_q_table, methods=['GET'])
app.add_url_rule('/performance/<user_id>/log', 'log_user_performance', log_user_performance, methods=['GET'])
app.add_url_rule('/performance/<user_id>/recommendations', 'get_recommended_flashcards', get_recommended_flashcards, methods=['GET'])


if __name__ == "__main__":
    app.run(debug=True)
