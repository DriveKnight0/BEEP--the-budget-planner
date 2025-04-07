from flask import Flask, request, jsonify, render_template
from chatbot import SmartBudgetAIChatbot
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
chatbot = SmartBudgetAIChatbot()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data or 'input' not in data:
            return jsonify({'error': 'Missing "input" field in request body'}), 400
        
        user_input = data['input']
        if not isinstance(user_input, str):
            return jsonify({'error': 'Input must be a string'}), 400
        
        response = chatbot.get_ai_response(user_input)
        return jsonify({'response': response})
    
    except Exception as e:
        print(f"Error in chat route: {str(e)}")  # Add error logging
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Use environment variables for port with a fallback to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
