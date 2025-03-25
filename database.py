from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    qualification = db.Column(db.String(120), nullable=True)
    dob = db.Column(db.String(120), nullable=False)
    scores = db.relationship('Score', backref='user', cascade="all, delete-orphan", lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    chapters = db.relationship('Chapter', backref='subject', cascade="all, delete-orphan", lazy=True) #When lazy=True (or lazy='select'), SQLAlchemy does not load related objects immediately. Instead, it loads them only when accessed. 

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    questions = db.relationship('Quiz', backref='chapter', cascade="all, delete-orphan", lazy=True)
    

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz =db.Column(db.Date)
    time_duration = db.Column(db.String(10)) #format : hh:mm
    remarks= db.Column(db.Text)
    questions= db.relationship('Question', backref='quiz', cascade="all, delete-orphan", lazy=True)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    title = db.Column(db.String(200))
    question = db.Column(db.Text)
    marks = db.Column(db.Integer, default=1)
    options = db.relationship('Option', backref='question', cascade="all, delete-orphan", lazy=True)


class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    time_stamp = db.Column(db.DateTime,server_default=db.func.current_timestamp(), nullable=False)