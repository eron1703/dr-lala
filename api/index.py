from flask import Flask, render_template_string, jsonify, request
import json
import random
import os

app = Flask(__name__)

# Store user progress
user_progress = {
    'biology': {'correct': 0, 'total': 0, 'seen': [], 'correct_ids': []},
    'chemistry': {'correct': 0, 'total': 0, 'seen': [], 'correct_ids': []},
    'physics': {'correct': 0, 'total': 0, 'seen': [], 'correct_ids': []},
    'mathematics': {'correct': 0, 'total': 0, 'seen': [], 'correct_ids': []}
}

# Load questions from JSON files
QUESTIONS = {}

def load_questions():
    """Load questions from JSON files"""
    subjects = ['biology', 'chemistry', 'physics', 'mathematics']
    for subject in subjects:
        try:
            file_path = os.path.join(os.path.dirname(__file__), '..', 'questions', f'{subject}.json')
            with open(file_path, 'r', encoding='utf-8') as f:
                QUESTIONS[subject] = json.load(f)
        except Exception as e:
            print(f"Error loading {subject} questions: {e}")
            QUESTIONS[subject] = []

# Load questions on startup
load_questions()

# Import the HTML template from the original app
from app import HTML_TEMPLATE

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/question/<subject>/<mode>')
def get_question(subject, mode):
    if subject not in QUESTIONS:
        return jsonify({"error": "Invalid subject"})
    
    subject_questions = QUESTIONS[subject]
    if not subject_questions:
        return jsonify({"error": "No questions available for this subject"})
    
    progress = user_progress[subject]
    
    if mode == 'review':
        missed = [q for q in subject_questions if q['id'] in progress['seen'] and q['id'] not in progress.get('correct_ids', [])]
        if not missed:
            return jsonify({"error": "No incorrect answers to review yet! Keep studying!"})
        question = random.choice(missed)
    else:
        unseen = [q for q in subject_questions if q['id'] not in progress['seen']]
        if unseen:
            question = random.choice(unseen)
        else:
            question = random.choice(subject_questions)
    
    return jsonify({
        "id": question['id'],
        "subject": subject,
        "index": question['id'] - 1,
        "question": question['question'],
        "options": question['options'],
        "correct": question['correct'],
        "explanation": question['explanation'],
        "topic_explanation": question.get('topic_explanation', '')
    })

@app.route('/api/record-answer', methods=['POST'])
def record_answer():
    data = request.json
    subject = data['subject']
    question_id = data['question_id']
    correct = data['correct']
    
    progress = user_progress[subject]
    
    if question_id not in progress['seen']:
        progress['seen'].append(question_id)
    
    progress['total'] += 1
    if correct:
        progress['correct'] += 1
        if question_id not in progress['correct_ids']:
            progress['correct_ids'].append(question_id)
    
    return jsonify({"success": True})

@app.route('/api/stats')
def get_stats():
    return jsonify(user_progress)

@app.route('/api/reset', methods=['POST'])
def reset_progress():
    global user_progress
    user_progress = {
        'biology': {'correct': 0, 'total': 0, 'seen': [], 'correct_ids': []},
        'chemistry': {'correct': 0, 'total': 0, 'seen': [], 'correct_ids': []},
        'physics': {'correct': 0, 'total': 0, 'seen': [], 'correct_ids': []},
        'mathematics': {'correct': 0, 'total': 0, 'seen': [], 'correct_ids': []}
    }
    return jsonify({"success": True})