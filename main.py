from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DATABASE = '/nfs/gpa.db'

GRADE_POINTS = {
    'A+': 4.0, 'A': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7,
    'D+': 1.3, 'D': 1.0, 'D-': 0.7,
    'F': 0.0
}

def get_db():
    db = sqlite3.connect(app.config.get('DATABASE', DATABASE))
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_name TEXT NOT NULL,
                credits INTEGER NOT NULL,
                grade TEXT NOT NULL,
                grade_points REAL NOT NULL
            );
        ''')
        db.commit()

def calculate_gpa(courses):
    if not courses:
        return 0.0
    total_points = sum(c['grade_points'] * c['credits'] for c in courses)
    total_credits = sum(c['credits'] for c in courses)
    if total_credits == 0:
        return 0.0
    return round(total_points / total_credits, 2)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            course_id = request.form.get('course_id')
            if course_id:
                db = get_db()
                db.execute('DELETE FROM courses WHERE id = ?', (course_id,))
                db.commit()
                message = 'Course deleted successfully.'
            else:
                message = 'Missing course id.'
            return redirect(url_for('index', message=message))

        course_name = request.form.get('course_name')
        credits = request.form.get('credits')
        grade = request.form.get('grade')

        if course_name and credits and grade:
            if grade not in GRADE_POINTS:
                message = 'Invalid grade entered.'
                return redirect(url_for('index', message=message))
            grade_points = GRADE_POINTS[grade]
            db = get_db()
            db.execute(
                'INSERT INTO courses (course_name, credits, grade, grade_points) VALUES (?, ?, ?, ?)',
                (course_name, int(credits), grade, grade_points)
            )
            db.commit()
            message = 'Course added successfully.'
        else:
            message = 'Please fill in all fields.'

        return redirect(url_for('index', message=message))

    message = request.args.get('message', '')
    db = get_db()
    courses = db.execute('SELECT * FROM courses').fetchall()
    gpa = calculate_gpa(courses)
    total_credits = sum(c['credits'] for c in courses)

    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>GPA Calculator</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; background: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h2 { color: #1a237e; }
                .gpa-display { font-size: 48px; font-weight: bold; color: #1a237e; text-align: center; padding: 20px; }
                .gpa-label { text-align: center; color: #666; font-size: 14px; margin-bottom: 20px; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th { background-color: #1a237e; color: white; padding: 10px; text-align: left; }
                td { border-bottom: 1px solid #ddd; padding: 10px; }
                tr:hover { background-color: #f5f5f5; }
                input[type=text], input[type=number], select { padding: 8px; width: 180px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
                input[type=submit] { padding: 10px 20px; background-color: #1a237e; color: white; border: none; cursor: pointer; border-radius: 4px; }
                input[type=submit]:hover { background-color: #283593; }
                .message { color: green; font-weight: bold; padding: 10px; }
                .form-row { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin-bottom: 10px; }
                .delete-btn { padding: 5px 10px; background-color: #c62828; color: white; border: none; cursor: pointer; border-radius: 4px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>📚 GPA Calculator</h2>
                <h4>CI/CD Pipeline - Lab 5.1 | Shrikar Neredimelli</h4>

                <div class="gpa-display">{{ gpa }}</div>
                <div class="gpa-label">Current GPA ({{ total_credits }} total credits)</div>

                <h3>Add a Course</h3>
                <form method="POST" action="{{ url_for('index') }}">
                    <div class="form-row">
                        <input type="text" name="course_name" placeholder="Course Name" required>
                        <input type="number" name="credits" placeholder="Credits" min="1" max="6" required>
                        <select name="grade" required>
                            <option value="">Select Grade</option>
                            <option value="A+">A+</option>
                            <option value="A">A</option>
                            <option value="A-">A-</option>
                            <option value="B+">B+</option>
                            <option value="B">B</option>
                            <option value="B-">B-</option>
                            <option value="C+">C+</option>
                            <option value="C">C</option>
                            <option value="C-">C-</option>
                            <option value="D+">D+</option>
                            <option value="D">D</option>
                            <option value="D-">D-</option>
                            <option value="F">F</option>
                        </select>
                        <input type="submit" value="Add Course">
                    </div>
                </form>

                {% if message %}
                  <p class="message">{{ message }}</p>
                {% endif %}

                {% if courses %}
                    <table>
                        <tr>
                            <th>Course</th>
                            <th>Credits</th>
                            <th>Grade</th>
                            <th>Grade Points</th>
                            <th>Delete</th>
                        </tr>
                        {% for course in courses %}
                            <tr>
                                <td>{{ course['course_name'] }}</td>
                                <td>{{ course['credits'] }}</td>
                                <td>{{ course['grade'] }}</td>
                                <td>{{ course['grade_points'] }}</td>
                                <td>
                                    <form method="POST" action="{{ url_for('index') }}">
                                        <input type="hidden" name="course_id" value="{{ course['id'] }}">
                                        <input type="hidden" name="action" value="delete">
                                        <input type="submit" value="Delete" class="delete-btn">
                                    </form>
                                </td>
                            </tr>
                        {% endfor %}
                    </table>
                {% else %}
                    <p>No courses added yet. Add your first course above!</p>
                {% endif %}
            </div>
        </body>
        </html>
    ''', message=message, courses=courses, gpa=gpa, total_credits=total_credits)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    init_db()
    app.run(debug=False, host='0.0.0.0', port=port)
