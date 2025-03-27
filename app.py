from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate  # Import Migrate
from flask_login import login_required, current_user
from flask_login import LoginManager, login_required, current_user
from config import Config

# Initialize the Flask app
app = Flask(__name__)
app.config.from_object(Config)


# Initialize the database and migrate objects
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Migrate after defining app
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login" 
# ✅ Fix: Use db.session.get() for retrieving User in Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # ✅ Corrected method
# Initialize the login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models (make sure this part is below the app initialization)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    quizzes = db.relationship('Quiz', backref='topic', lazy=True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    option1 = db.Column(db.String(100), nullable=False)
    option2 = db.Column(db.String(100), nullable=False)
    option3 = db.Column(db.String(100), nullable=False)
    option4 = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.String(100), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)  # Make sure this is included
  # Ensure this is defined

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='SET NULL'), nullable=True)
    attempt_count = db.Column(db.Integer, default=0)


    user = db.relationship('User', backref='quiz_attempts')
    quiz = db.relationship('Quiz', backref='quiz_attempts')

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Integer, default=0)

    user = db.relationship('User', backref='scores')  # Allow multiple scores


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/user_dashboard', methods=['GET'])
@login_required
def user_dashboard():
    topics = Topic.query.all()  # Fetch all topics from the database
    topic_names = [t.name for t in topics]  # Convert topics to a list of names
    selected_topic = request.args.get('topic')  # Get the selected topic from request

    quizzes = []
    if selected_topic and selected_topic in topic_names:
        quizzes = Quiz.query.join(Topic).filter(Topic.name == selected_topic).all()

    # Fetch user's latest score from the database
    existing_score = Score.query.filter_by(user_id=current_user.id).first()
    user_score = existing_score.score if existing_score else "Not Attempted Yet"

    # Fetch the number of attempts for the user
    attempts_count = Score.query.filter_by(user_id=current_user.id).count()  # Count the number of attempts

    return render_template(
        'user_dashboard.html',
        topics=topic_names,  # Pass topic names for the dropdown
        selected_topic=selected_topic,
        quizzes=quizzes,
        score=user_score,  # Pass database score to the template
        attempts=attempts_count  # Pass the number of attempts to the template
    )

@app.route('/submit_quiz', methods=['POST'])
@login_required
def submit_quiz():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))  # Prevent admin from submitting quiz

    score = 0
    for quiz in Quiz.query.all():
        selected_answer = request.form.get(str(quiz.id))
        if selected_answer == quiz.correct_answer:
            score += 1

        # Track quiz attempt
        quiz_attempt = QuizAttempt.query.filter_by(user_id=current_user.id, quiz_id=quiz.id).first()

        if quiz_attempt:
            # Increment the attempt count if the quiz was already attempted
            quiz_attempt.attempt_count += 1
        else:
            # Create a new attempt if this is the first attempt
            quiz_attempt = QuizAttempt(user_id=current_user.id, quiz_id=quiz.id, attempt_count=1)
            db.session.add(quiz_attempt)

    db.session.commit()

    # Fetch the existing score, if any
    existing_score = Score.query.filter_by(user_id=current_user.id).first()

    if existing_score:
        existing_score.score += score  # Accumulate the new score
    else:
        db.session.add(Score(user_id=current_user.id, score=score))  # Insert new score if none exists

    db.session.commit()

    flash(f"You scored {score} points! Total Score: {existing_score.score if existing_score else score}", "success")
    return redirect(url_for('user_dashboard'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Admin Setup (Runs Once)
def create_admin():
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", password=generate_password_hash("admin123"), is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin/admin123")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for('register'))

        user = User(username=username, password=password, is_admin=False)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  # Get selected role

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            if role == 'admin' and user.is_admin:
                login_user(user)
                return redirect(url_for('admin_dashboard'))
            elif role == 'user' and not user.is_admin:
                login_user(user)
                return redirect(url_for('user_dashboard'))
            else:
                return "Invalid role selection", 403  # Prevents users from logging in as admins

    return render_template('login.html')


@app.route('/admin/dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    quizzes = Quiz.query.all()
    scores = Score.query.all()
    users = User.query.all()
    topics = Topic.query.all()  # Get all topics
    return render_template('admin_dashboard.html', quizzes=quizzes, users=users, scores=scores, topics=topics)

@app.route('/admin/create_quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))  # Redirect if not admin
    
    topics = Topic.query.all()  # Get all topics for the dropdown

    if request.method == 'POST':
        selected_topic = request.form['topic']  # Get selected topic ID
        new_topic = request.form.get('new_topic')  # Get new topic name if entered

        # If new topic is provided, create a new topic
        if new_topic:
            topic = Topic(name=new_topic)
            db.session.add(topic)
            db.session.commit()

            # Fetch the updated list of topics (including the new one)
            topics = Topic.query.all()

            flash(f"New topic '{new_topic}' created!", "success")
            selected_topic = topic.id  # Set selected topic to newly created topic

        # If no topic selected and no new topic provided, show error
        if not selected_topic:
            flash("Please select an existing topic or create a new one.", "danger")
            return redirect(url_for('create_quiz'))

        # Create and save the quiz with the selected/new topic
        quiz = Quiz(
            question=request.form['question'],
            option1=request.form['option1'],
            option2=request.form['option2'],
            option3=request.form['option3'],
            option4=request.form['option4'],
            correct_answer=request.form['correct_answer'],
            topic_id=selected_topic  # Link quiz to topic
        )

        db.session.add(quiz)
        db.session.commit()
        flash("Quiz added successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('create_quiz.html', topics=topics)


@app.route('/admin/create_topic', methods=['GET', 'POST'])
@login_required
def create_topic():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))  # Redirect if not admin

    if request.method == 'POST':
        topic_name = request.form['name']
        if topic_name:
            topic = Topic(name=topic_name)
            db.session.add(topic)
            db.session.commit()
            flash("Topic added successfully!", "success")
            return redirect(url_for('create_topic'))  # Stay on the topic creation page after adding the topic
        else:
            flash("Topic name cannot be empty", "danger")

    return render_template('create_topic.html')

@app.route('/view_quizzes')
def view_quizzes():
    quizzes = Quiz.query.all()  # Assuming you have a Quiz model
    return render_template('view_quizzes.html', quizzes=quizzes)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged out.", "info")
    return redirect(url_for('login'))

@app.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    if not current_user.is_admin:
        flash("You do not have permission to delete quizzes.", "danger")
        return redirect(url_for('admin_dashboard'))

    quiz = Quiz.query.get_or_404(quiz_id)  # Fetch quiz or return 404 if not found

    # Delete any quiz attempts associated with the quiz
    QuizAttempt.query.filter_by(quiz_id=quiz_id).delete()

    # Now delete the quiz itself
    db.session.delete(quiz)
    db.session.commit()

    flash("Quiz deleted successfully!", "success")
    return redirect(url_for('view_quizzes'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()  # Ensures admin exists
    app.run(debug=True)