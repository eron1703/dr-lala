from flask import Flask, render_template_string, jsonify, request
import json
import random
import os

app = Flask(__name__)

# Store user progress (in production, use a database)
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
            # Try different paths for Vercel deployment
            possible_paths = [
                os.path.join(os.path.dirname(__file__), '..', 'questions', f'{subject}.json'),
                os.path.join(os.path.dirname(__file__), 'questions', f'{subject}.json'),
                f'questions/{subject}.json'
            ]
            
            for file_path in possible_paths:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        QUESTIONS[subject] = json.load(f)
                    break
            else:
                QUESTIONS[subject] = []
        except Exception as e:
            print(f"Error loading {subject} questions: {e}")
            QUESTIONS[subject] = []

# Load questions on startup
load_questions()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>💗 Dr. Lala 💗 - Medical Entrance Exam Prep</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 0;
            margin: 0;
            overflow-x: hidden;
            min-height: 100vh;
        }

        .header {
            background: linear-gradient(135deg, #e91e63 0%, #f06292 100%);
            color: white;
            padding: 20px;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 4px 20px rgba(233, 30, 99, 0.3);
        }

        .header h1 {
            font-size: 32px;
            margin-bottom: 5px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .header p {
            font-size: 16px;
            opacity: 0.95;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        .back-button {
            position: absolute;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255,255,255,0.2);
            border: 2px solid white;
            color: white;
            padding: 8px 16px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            display: none;
        }

        .back-button:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-50%) scale(1.05);
        }

        .back-button.show {
            display: inline-block;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }

        @media (min-width: 600px) {
            .stats-grid {
                grid-template-columns: repeat(4, 1fr);
            }
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }

        .stat-card.active {
            background: linear-gradient(135deg, #ffe0ec 0%, #ffc1e3 100%);
            border-color: #e91e63;
            transform: scale(1.05);
        }

        .stat-card h3 {
            font-size: 18px;
            color: #e91e63;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .stat-card .score {
            font-size: 36px;
            font-weight: bold;
            background: linear-gradient(135deg, #e91e63 0%, #f06292 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 10px 0;
        }

        .stat-card .total {
            font-size: 14px;
            color: #666;
        }

        .flashcard {
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            overflow: hidden;
            animation: slideIn 0.5s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .card-header {
            background: linear-gradient(135deg, #f8bbd0 0%, #fce4ec 100%);
            padding: 20px;
            border-bottom: 2px solid #fce4ec;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .question-number {
            font-weight: bold;
            color: #c2185b;
            font-size: 18px;
        }

        .subject-tag {
            background: white;
            color: #e91e63;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 2px 10px rgba(233, 30, 99, 0.2);
        }

        .card-content {
            padding: 30px;
            min-height: 300px;
        }

        .question {
            font-size: 20px;
            line-height: 1.8;
            margin-bottom: 30px;
            color: #2c3e50;
        }

        .options {
            list-style: none;
        }

        .option {
            margin-bottom: 15px;
            padding: 18px;
            background: #f8f9fa;
            border: 3px solid #e9ecef;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 17px;
        }

        .option:hover {
            border-color: #f06292;
            background: #fce4ec;
            transform: translateX(5px);
        }

        .option.selected {
            border-color: #e91e63;
            background: #fce4ec;
            font-weight: 600;
        }

        .option.correct {
            border-color: #4caf50;
            background: #e8f5e9;
            animation: correctPulse 0.5s ease;
        }

        .option.incorrect {
            border-color: #f44336;
            background: #ffebee;
            animation: shake 0.5s ease;
        }

        @keyframes correctPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }

        .answer-section {
            display: none;
            margin-top: 25px;
            padding: 25px;
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-radius: 12px;
            border-left: 5px solid #2196f3;
            animation: fadeIn 0.5s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .answer-section.show {
            display: block;
        }

        .answer-label {
            font-weight: bold;
            color: #1565c0;
            margin-bottom: 15px;
            font-size: 18px;
        }

        .explanation {
            margin-bottom: 20px;
            line-height: 1.8;
            color: #333;
        }

        .topic-explanation {
            margin-top: 20px;
            padding: 20px;
            background: linear-gradient(135deg, #fff9c4 0%, #ffecb3 100%);
            border-radius: 12px;
            border-left: 5px solid #ffa726;
        }

        .topic-explanation h4 {
            color: #e65100;
            margin-bottom: 12px;
            font-size: 18px;
        }

        .controls {
            display: flex;
            gap: 15px;
            margin-top: 25px;
        }

        .btn {
            flex: 1;
            background: linear-gradient(135deg, #e91e63 0%, #f06292 100%);
            color: white;
            border: none;
            padding: 18px;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(233, 30, 99, 0.3);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(233, 30, 99, 0.4);
        }

        .btn:active {
            transform: scale(0.98);
        }

        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            box-shadow: none;
        }

        .btn-secondary {
            background: linear-gradient(135deg, #90a4ae 0%, #b0bec5 100%);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        .mode-selector {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            padding: 20px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .mode-btn {
            flex: 1;
            padding: 15px;
            border: 3px solid #e9ecef;
            background: #f8f9fa;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
        }

        .mode-btn.active {
            background: linear-gradient(135deg, #ffe0ec 0%, #ffc1e3 100%);
            border-color: #e91e63;
            transform: scale(1.05);
        }

        .progress-bar {
            height: 12px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 25px;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #e91e63 0%, #f06292 100%);
            transition: width 0.5s ease;
            border-radius: 10px;
        }

        .quick-stats {
            background: white;
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-around;
            text-align: center;
        }

        .quick-stat h4 {
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .quick-stat p {
            font-size: 28px;
            font-weight: bold;
            background: linear-gradient(135deg, #e91e63 0%, #f06292 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .loading {
            text-align: center;
            padding: 60px;
            color: #666;
        }

        .heart-loader {
            display: inline-block;
            position: relative;
            width: 80px;
            height: 80px;
            margin: 0 auto 20px;
        }

        .heart-loader:before,
        .heart-loader:after {
            content: '💗';
            position: absolute;
            font-size: 40px;
            animation: heartbeat 1.2s infinite;
        }

        .heart-loader:after {
            animation-delay: 0.6s;
        }

        @keyframes heartbeat {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.8; }
        }

        .reset-btn {
            background: linear-gradient(135deg, #f44336 0%, #ef5350 100%);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 20px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
        }

        .reset-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(244, 67, 54, 0.4);
        }
    </style>
</head>
<body>
    <div class="header">
        <button class="back-button" id="backButton" onclick="goBack()">← Back</button>
        <h1>💗 Dr. Lala 💗</h1>
        <p>Your Personal Medical Exam Coach - 400 Questions with Love!</p>
    </div>

    <div class="container">
        <div class="quick-stats">
            <div class="quick-stat">
                <h4>Progress</h4>
                <p id="totalProgress">0%</p>
            </div>
            <div class="quick-stat">
                <h4>Questions</h4>
                <p id="questionsSeen">0/400</p>
            </div>
            <div class="quick-stat">
                <h4>Accuracy</h4>
                <p id="accuracy">0%</p>
            </div>
        </div>

        <div class="mode-selector">
            <div class="mode-btn active" onclick="setMode('study')">
                <strong>📚 Study Mode</strong><br>
                <small>Learn with explanations</small>
            </div>
            <div class="mode-btn" onclick="setMode('test')">
                <strong>✍️ Test Mode</strong><br>
                <small>Practice like real exam</small>
            </div>
            <div class="mode-btn" onclick="setMode('review')">
                <strong>🔄 Review Mode</strong><br>
                <small>Focus on mistakes</small>
            </div>
        </div>

        <div class="stats-grid" id="subjectGrid">
            <div class="stat-card" onclick="selectSubject('biology')">
                <h3>🧬 Biology</h3>
                <div class="score" id="biology-score">0%</div>
                <div class="total" id="biology-total">0/100 seen</div>
            </div>
            <div class="stat-card" onclick="selectSubject('chemistry')">
                <h3>⚗️ Chemistry</h3>
                <div class="score" id="chemistry-score">0%</div>
                <div class="total" id="chemistry-total">0/100 seen</div>
            </div>
            <div class="stat-card" onclick="selectSubject('physics')">
                <h3>⚡ Physics</h3>
                <div class="score" id="physics-score">0%</div>
                <div class="total" id="physics-total">0/100 seen</div>
            </div>
            <div class="stat-card" onclick="selectSubject('mathematics')">
                <h3>📐 Mathematics</h3>
                <div class="score" id="mathematics-score">0%</div>
                <div class="total" id="mathematics-total">0/100 seen</div>
            </div>
        </div>

        <div class="progress-bar">
            <div class="progress-fill" id="progressBar" style="width: 0%"></div>
        </div>

        <div id="flashcardContainer">
            <div class="loading">
                <div class="heart-loader"></div>
                <p>Select a subject to start your journey! 💪</p>
            </div>
        </div>

        <center>
            <button class="reset-btn" onclick="resetProgress()">🔄 Reset All Progress</button>
        </center>
    </div>

    <script>
        let currentSubject = null;
        let currentQuestion = null;
        let currentMode = 'study';
        let selectedAnswer = null;

        function setMode(mode) {
            currentMode = mode;
            document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
            event.target.closest('.mode-btn').classList.add('active');
            
            if (currentSubject) {
                loadQuestion(currentSubject);
            }
        }

        function selectSubject(subject) {
            currentSubject = subject;
            document.querySelectorAll('.stat-card').forEach(card => card.classList.remove('active'));
            document.querySelectorAll('.stat-card')[['biology', 'chemistry', 'physics', 'mathematics'].indexOf(subject)].classList.add('active');
            
            // Show back button when a subject is selected
            document.getElementById('backButton').classList.add('show');
            
            // Hide subject grid and show flashcard
            document.getElementById('subjectGrid').style.display = 'none';
            
            loadQuestion(subject);
        }

        function goBack() {
            currentSubject = null;
            document.getElementById('backButton').classList.remove('show');
            document.getElementById('subjectGrid').style.display = 'grid';
            document.getElementById('flashcardContainer').innerHTML = `
                <div class="loading">
                    <div class="heart-loader"></div>
                    <p>Select a subject to start your journey! 💪</p>
                </div>
            `;
        }

        async function loadQuestion(subject) {
            const response = await fetch(`/api/question/${subject}/${currentMode}`);
            const data = await response.json();
            
            if (data.error) {
                document.getElementById('flashcardContainer').innerHTML = `
                    <div class="flashcard">
                        <div class="card-content">
                            <p style="text-align: center; color: #e91e63; font-size: 20px;">
                                ${data.error} 💗
                            </p>
                        </div>
                    </div>
                `;
                return;
            }
            
            currentQuestion = data;
            displayQuestion(data);
        }

        function displayQuestion(question) {
            const container = document.getElementById('flashcardContainer');
            
            container.innerHTML = `
                <div class="flashcard">
                    <div class="card-header">
                        <span class="question-number">Question ${question.index + 1} of 100</span>
                        <span class="subject-tag">${getSubjectEmoji(question.subject)} ${question.subject.charAt(0).toUpperCase() + question.subject.slice(1)}</span>
                    </div>
                    <div class="card-content">
                        <div class="question">${question.question}</div>
                        <ul class="options">
                            ${question.options.map((option, index) => `
                                <li class="option" onclick="selectAnswer(${index})">
                                    ${String.fromCharCode(65 + index)}. ${option}
                                </li>
                            `).join('')}
                        </ul>
                        <div class="answer-section" id="answerSection">
                            <div class="answer-label">✅ Correct Answer: ${String.fromCharCode(65 + question.correct)}</div>
                            <div class="explanation">${question.explanation}</div>
                            ${question.topic_explanation ? `
                                <div class="topic-explanation">
                                    <h4>💡 Need to Know:</h4>
                                    <div>${question.topic_explanation}</div>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
                <div class="controls">
                    <button class="btn btn-secondary" onclick="showAnswer()" id="showBtn">Show Answer</button>
                    <button class="btn" onclick="nextQuestion()" id="nextBtn" style="display: none;">Next Question →</button>
                </div>
            `;
            
            selectedAnswer = null;
        }

        function getSubjectEmoji(subject) {
            const emojis = {
                'biology': '🧬',
                'chemistry': '⚗️',
                'physics': '⚡',
                'mathematics': '📐'
            };
            return emojis[subject] || '📚';
        }

        function selectAnswer(index) {
            if (selectedAnswer !== null) return;
            
            selectedAnswer = index;
            const options = document.querySelectorAll('.option');
            options[index].classList.add('selected');
            
            if (currentMode === 'study') {
                checkAnswer();
            }
        }

        function showAnswer() {
            if (selectedAnswer === null && currentMode !== 'study') {
                alert('Please select an answer first! 💗');
                return;
            }
            checkAnswer();
        }

        async function checkAnswer() {
            const options = document.querySelectorAll('.option');
            options[currentQuestion.correct].classList.add('correct');
            
            if (selectedAnswer !== null && selectedAnswer !== currentQuestion.correct) {
                options[selectedAnswer].classList.add('incorrect');
            }
            
            document.getElementById('answerSection').classList.add('show');
            document.getElementById('showBtn').style.display = 'none';
            document.getElementById('nextBtn').style.display = 'block';
            
            // Record answer
            if (selectedAnswer !== null) {
                await fetch('/api/record-answer', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        subject: currentQuestion.subject,
                        question_id: currentQuestion.id,
                        correct: selectedAnswer === currentQuestion.correct
                    })
                });
                updateStats();
            }
        }

        function nextQuestion() {
            loadQuestion(currentSubject);
        }

        async function updateStats() {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            let totalSeen = 0;
            let totalCorrect = 0;
            let totalAttempted = 0;
            
            for (const subject in stats) {
                const data = stats[subject];
                const score = data.total > 0 ? Math.round((data.correct / data.total) * 100) : 0;
                document.getElementById(`${subject}-score`).textContent = `${score}%`;
                document.getElementById(`${subject}-total`).textContent = 
                    `${data.seen.length}/100 seen`;
                
                totalSeen += data.seen.length;
                totalCorrect += data.correct;
                totalAttempted += data.total;
            }
            
            // Update overall progress
            document.getElementById('totalProgress').textContent = 
                Math.round((totalSeen / 400) * 100) + '%';
            document.getElementById('questionsSeen').textContent = 
                `${totalSeen}/400`;
            document.getElementById('accuracy').textContent = 
                totalAttempted > 0 ? Math.round((totalCorrect / totalAttempted) * 100) + '%' : '0%';
            
            // Update progress bar
            document.getElementById('progressBar').style.width = 
                `${(totalSeen / 400) * 100}%`;
        }

        async function resetProgress() {
            if (confirm('Are you sure you want to reset all progress? This cannot be undone! 💔')) {
                await fetch('/api/reset', {method: 'POST'});
                updateStats();
                location.reload();
            }
        }

        // Initial load
        updateStats();
    </script>
</body>
</html>
'''

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

# Handler for Vercel
app = app