from flask import Flask, render_template, request, url_for, redirect, flash, session, jsonify
from database import *
from flask import render_template
from database import db, Subject, Chapter, Question 
from datetime import datetime, timedelta,date 
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
def configure_routes(app):
    @app.route("/")
    def hello_world():
        return render_template("index.html")

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()
            if user and user.password == password:
                session['user_id'] = user.id
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
        return render_template('login.html')
    
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            fullname = request.form['fullname']
            qualification = request.form['qualification']
            dob = request.form['dob']
            user = User(email=email, password=password, role='user' , username=fullname, qualification=qualification, dob=dob)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('signup.html')

    from datetime import date
    @app.route('/quiz/start/<int:quiz_id>')
    @app.route('/quiz/start/<int:quiz_id>/<int:question_number>')
    @login_required
    def start_quiz(quiz_id, question_number=1):
        quiz = Quiz.query.options(
            db.joinedload(Quiz.chapter).joinedload(Chapter.subject),
            db.joinedload(Quiz.questions).joinedload(Question.options)
        ).get_or_404(quiz_id)
        
        # Initialize quiz session
        if 'quiz_start_time' not in session:
            session['quiz_start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            session['answers'] = {}
        
        # Calculate time left
        start_time = datetime.strptime(session['quiz_start_time'], '%Y-%m-%d %H:%M:%S')
        time_elapsed = datetime.now() - start_time
        
        try:
            if ':' in quiz.time_duration:
                hours, minutes = map(int, quiz.time_duration.split(':'))
                total_minutes = hours * 60 + minutes
            else:
                total_minutes = int(quiz.time_duration)
        except (ValueError, TypeError):
            total_minutes = 60
            
        time_left = timedelta(minutes=total_minutes) - time_elapsed
        
        # Check if time is up
        if time_left.total_seconds() <= 0:
            return redirect(url_for('submit_quiz', quiz_id=quiz_id))
        
        questions = quiz.questions  # Changed from quiz.question to quiz.questions
        if not questions:
            flash('No questions available for this quiz.', 'error')
            return redirect(url_for('user_dashboard'))
        
        current_question = min(max(1, question_number), len(questions))
        question = questions[current_question - 1]
        
        minutes_left = int(time_left.total_seconds() // 60)
        seconds_left = int(time_left.total_seconds() % 60)
        time_left_str = f"{minutes_left}:{seconds_left:02d}"
        
        return render_template('quiz.html',
                            quiz=quiz,
                            question=question,
                            current_question=current_question,
                            total_questions=len(questions),
                            time_left=time_left_str)

    @app.route('/quiz/details/<int:quiz_id>')
    @login_required
    def view_quiz_details(quiz_id):
        # Get the quiz with all related data
        quiz_data = db.session.query(
            Quiz,
            Chapter,
            Subject,
            db.func.count(Question.id).label('question_count')
        ).join(
            Chapter, Quiz.chapter_id == Chapter.id
        ).join(
            Subject, Chapter.subject_id == Subject.id
        ).outerjoin(
            Question, Question.quiz_id == Quiz.id
        ).filter(
            Quiz.id == quiz_id
        ).group_by(
            Quiz.id, Chapter.id, Subject.id
        ).first()
        
        if not quiz_data:
            flash('Quiz not found', 'error')
            return redirect(url_for('user_dashboard'))
        
        # Get user's score if exists
        user_score = Score.query.filter_by(
            user_id=session.get('user_id'),
            quiz_id=quiz_id
        ).first()
        
        today = date.today()
        
        return render_template('quiz_details.html',
                            quiz_data=quiz_data,
                            user_score=user_score,
                            today=today)


    @app.route('/user/dashboard', methods=['GET', 'POST'])
    @login_required
    def user_dashboard():
        # Get all quizzes with their question counts and related data
        quizzes = db.session.query(
            Quiz,
            db.func.count(Question.id).label('question_count')
        ).join(
            Chapter
        ).join(
            Subject
        ).outerjoin(
            Question
        ).group_by(Quiz.id).all()
        
        today = date.today()
        return render_template('user_dashboard.html', quizzes=quizzes, today=today)

    # @app.route('/user/dashboard', methods=['GET', 'POST'])
    # def user_dashboard():
    #     # Get all quizzes with their question counts
    #     quizzes = db.session.query(
    #         Quiz,
    #         db.func.count(Question.id).label('question_count')
    #     ).outerjoin(
    #         Question
    #     ).group_by(Quiz.id).all()
        
    #     today = date.today()  # Use date.today() instead of datetime.now().date()
    #     return render_template('user_dashboard.html', quizzes=quizzes, today=today)

    # @app.route('/quiz/start/<int:quiz_id>')
    # @app.route('/quiz/start/<int:quiz_id>/<int:question_number>')
    # @login_required
    # def start_quiz(quiz_id, question_number=1):
    #     quiz = Quiz.query.options(
    #         db.joinedload(Quiz.chapter).joinedload(Chapter.subject),
    #         db.joinedload(Quiz.questions).joinedload(Question.options)
    #     ).get_or_404(quiz_id)
        
    #     # Initialize quiz session
    #     if 'quiz_start_time' not in session:
    #         session['quiz_start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #         session['answers'] = {}
        
    #     # Calculate time left
    #     start_time = datetime.strptime(session['quiz_start_time'], '%Y-%m-%d %H:%M:%S')
    #     time_elapsed = datetime.now() - start_time
        
    #     try:
    #         if ':' in quiz.time_duration:
    #             hours, minutes = map(int, quiz.time_duration.split(':'))
    #             total_minutes = hours * 60 + minutes
    #         else:
    #             total_minutes = int(quiz.time_duration)
    #     except (ValueError, TypeError):
    #         total_minutes = 60
            
    #     time_left = timedelta(minutes=total_minutes) - time_elapsed
        
    #     # Check if time is up
    #     if time_left.total_seconds() <= 0:
    #         return redirect(url_for('submit_quiz', quiz_id=quiz_id))  # Changed from 'scores' to 'submit_quiz'
        
    #     questions = quiz.questions
    #     if not questions:
    #         flash('No questions available for this quiz.', 'error')
    #         return redirect(url_for('user_dashboard'))
        
    #     current_question = min(max(1, question_number), len(questions))
    #     question = questions[current_question - 1]
        
    #     minutes_left = int(time_left.total_seconds() // 60)
    #     seconds_left = int(time_left.total_seconds() % 60)
    #     time_left_str = f"{minutes_left}:{seconds_left:02d}"
        
    #     return render_template('quiz.html',
    #                         quiz=quiz,
    #                         question=question,
    #                         current_question=current_question,
    #                         total_questions=len(questions),
    #                         time_left=time_left_str)

    
    # Add this relationship to Quiz model
    @app.route('/quiz/handle/<int:quiz_id>/<int:question_number>', methods=['POST'])
    @login_required
    def handle_quiz(quiz_id, question_number):
        action = request.form.get('action')
        answer = request.form.get('answer')
            
        print(f"Handle quiz - Action: {action}, Answer: {answer}")  # Debug print
            
            # Get the current question
        quiz = Quiz.query.get_or_404(quiz_id)
        question = quiz.questions[question_number - 1]
            
            # Save the answer in session using question.id as key
        if answer:
            if 'answers' not in session:
                session['answers'] = {}
            session['answers'][str(question.id)] = answer  # Use question.id instead of question_number
            session.modified = True
            print(f"Saved answer {answer} for question {question.id}")  # Debug print
            
        if action == 'submit':
            print("Submitting quiz...")
            return redirect(url_for('submit_quiz', quiz_id=quiz_id))
            
        if action == 'next':
            return redirect(url_for('start_quiz', quiz_id=quiz_id, question_number=question_number + 1))
        elif action == 'prev':
            return redirect(url_for('start_quiz', quiz_id=quiz_id, question_number=question_number - 1))

    @app.route('/quiz/submit/<int:quiz_id>', methods=['GET', 'POST'])
    @login_required
    def submit_quiz(quiz_id):
        print(f"Current user_id in session: {session.get('user_id')}")
        
        # Get the answers from session
        answers = session.get('answers', {})
        
        # Get the quiz with all related data
        quiz = Quiz.query.options(
            db.joinedload(Quiz.chapter).joinedload(Chapter.subject),
            db.joinedload(Quiz.questions).joinedload(Question.options)
        ).get_or_404(quiz_id)
        
        # Calculate score
        total_marks = 0
        scored_marks = 0
        correct_answers = 0
        total_questions = len(quiz.questions)
        
        for question in quiz.questions:
            total_marks += question.marks
            user_answer_id = answers.get(str(question.id))
            
            if user_answer_id:
                print(f"Checking question {question.id}")
                print(f"User answer ID: {user_answer_id}")
                
                selected_option = Option.query.get(int(user_answer_id))
                print(f"Selected option is_correct: {selected_option.is_correct if selected_option else 'No option found'}")
                
                if selected_option and selected_option.is_correct:
                    scored_marks += question.marks
                    correct_answers += 1
                    print(f"Correct answer! Score: {scored_marks}")
        
        percentage = (scored_marks / total_marks * 100) if total_marks > 0 else 0
        print(f"Final percentage: {percentage}%")
        
        try:
            user_id = session.get('user_id')
            if not user_id:
                raise ValueError("No user_id in session")
                
            new_score = Score(
                user_id=user_id,
                quiz_id=quiz_id,
                score=int(percentage)
            )
            db.session.add(new_score)
            db.session.commit()
            
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Get all scores for this user with related data
            all_scores = Score.query\
                .filter_by(user_id=user_id)\
                .join(Quiz)\
                .join(Chapter)\
                .join(Subject)\
                .options(
                    db.joinedload(Score.quiz)
                    .joinedload(Quiz.chapter)
                    .joinedload(Chapter.subject)
                )\
                .order_by(Score.time_stamp.desc())\
                .all()
            
            # Clear quiz session data
            session.pop('quiz_start_time', None)
            session.pop('answers', None)
            
            return render_template('scores.html',
                                quiz=quiz,
                                current_score=new_score,
                                all_scores=all_scores,
                                total_questions=total_questions,
                                correct_answers=correct_answers,
                                percentage=percentage,
                                user=user)
                                
        except Exception as e:
            print(f"Error submitting quiz: {e}")
            db.session.rollback()
            flash('Error submitting quiz. Please try again.', 'error')
            return redirect(url_for('user_dashboard'))
        
        # @app.route('/quiz/view/<int:quiz_id>')
        # @login_required
        # def view_quiz_details(quiz_id):
        #     # Get the quiz with all related information
        #     quiz_data = db.session.query(
        #         Quiz,
        #         Chapter,
        #         Subject,
        #         db.func.count(Question.id).label('question_count')
        #     ).select_from(Quiz).join(
        #         Chapter, Quiz.chapter_id == Chapter.id
        #     ).join(
        #         Subject, Chapter.subject_id == Subject.id
        #     ).outerjoin(
        #         Question, Question.quiz_id == Quiz.id
        #     ).filter(
        #         Quiz.id == quiz_id
        #     ).group_by(
        #         Quiz.id, Chapter.id, Subject.id
        #     ).first()
            
        #     if not quiz_data:
        #         flash('Quiz not found', 'error')
        #         return redirect(url_for('user_dashboard'))
            
        #     today = date.today()
        #     return render_template('view_quiz.html', quiz_data=quiz_data, today=today)


    @app.route('/admin/dashboard' , methods=['GET', 'POST'])
    def admin_dashboard():
            subjects = Subject.query.all()
            return render_template('admin_dashboard.html', subjects=subjects)

    @app.route('/chapter/edit/<int:chapter_id>', methods=['GET', 'POST'])
    def edit_chapter(chapter_id):
            chapter = Chapter.query.get_or_404(chapter_id)
            if request.method == 'POST':
                chapter.name = request.form['name']
                db.session.commit()
                flash('Chapter updated successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            return render_template('edit_chapter.html', chapter=chapter)

    @app.route('/chapter/delete/<int:chapter_id>', methods=['POST', 'GET'])
    def delete_chapter(chapter_id):
            chapter = Chapter.query.get_or_404(chapter_id)
            db.session.delete(chapter)
            db.session.commit()
            flash('Chapter deleted successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
    @app.route('/subject/add', methods=['GET', 'POST'])
    def add_subject():
            if request.method == 'POST':
                subject_name = request.form['name']
                subject_description = request.form['description']
                new_subject = Subject(name=subject_name, description=subject_description)
                db.session.add(new_subject)
                db.session.commit()
                flash('Subject added successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            return render_template('add_subject.html')
    @app.route('/chapter/add/<int:subject_id>', methods=['GET', 'POST'])
    def add_chapter(subject_id):  # Make sure subject_id is included as a parameter
            subject = Subject.query.get_or_404(subject_id)  # Get the subject or return 404 if not found
            
            if request.method == 'POST':
                chapter_name = request.form['name']
                chapter_description = request.form['description']
                new_chapter = Chapter(
                    name=chapter_name,
                    description=chapter_description,
                    subject_id=subject_id  # Associate the chapter with the subject
                )
                db.session.add(new_chapter)
                db.session.commit()
                flash('Chapter added successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            
            return render_template('add_chapter.html', subject=subject)

    @app.route('/admin/quiz')
    def admin_quiz():
            # Get all quizzes instead of chapters
            quizzes = Quiz.query.all()
            chapters = Chapter.query.all()
            return render_template('admin_quiz.html', quizzes=quizzes, chapters=chapters)

    @app.route('/quiz/add', methods=['GET', 'POST'])
    def add_quiz():
            if request.method == 'POST':
                chapter_id = request.form['chapter_id']
                quiz_date = request.form['date']
                quiz_duration = request.form['duration']
                
                # Create new quiz
                new_quiz = Quiz(
                    chapter_id=chapter_id,
                    date_of_quiz=datetime.strptime(quiz_date, '%Y-%m-%d').date(),
                    time_duration=quiz_duration
                )
                db.session.add(new_quiz)
                db.session.commit()
                
                flash('Quiz created successfully!', 'success')
                return redirect(url_for('admin_quiz'))
            
            chapters = Chapter.query.all()
            return render_template('add_quiz.html', chapters=chapters)

    @app.route('/quiz/<int:quiz_id>/questions')
    def view_quiz_questions(quiz_id):
            quiz = Quiz.query.get_or_404(quiz_id)
            questions = Question.query.filter_by(quiz_id=quiz_id).all()
            return render_template('quiz_questions.html', quiz=quiz, questions=questions)

    @app.route('/quiz/<int:quiz_id>/question/add', methods=['GET', 'POST'])
    def add_quiz_question(quiz_id):
            quiz = Quiz.query.get_or_404(quiz_id)
            
            if request.method == 'POST':
                new_question = Question(
                    quiz_id=quiz_id,
                    title=request.form['title'],
                    question=request.form['question'],
                    marks=request.form['marks']
                )
                db.session.add(new_question)
                db.session.flush()  # To get the question ID

                # Add options
                correct_option = request.form['correct_option']
                for i in range(4):
                    option = Option(
                        question_id=new_question.id,
                        option_text=request.form[f'option_{i}'],
                        is_correct=(str(i) == correct_option)
                    )
                    db.session.add(option)
                
                db.session.commit()
                flash('Question added successfully!', 'success')
                return redirect(url_for('view_quiz_questions', quiz_id=quiz_id))
            
            return render_template('add_question.html', quiz=quiz)
    # Add these routes to your apis.py

    @app.route('/quiz/question/<int:question_id>/edit', methods=['GET', 'POST'])
    def edit_questions(question_id):
        question = Question.query.get_or_404(question_id)
        
        if request.method == 'POST':
            question.title = request.form['title']
            question.question = request.form['question']
            question.marks = int(request.form['marks'])
            
            # Delete existing options
            Option.query.filter_by(question_id=question.id).delete()
            
            # Add new options
            correct_option = request.form['correct_option']
            for i in range(4):
                option = Option(
                    question_id=question.id,
                    option_text=request.form[f'option_{i}'],
                    is_correct=(str(i) == correct_option)
                )
                db.session.add(option)
                
            db.session.commit()
            flash('Question updated successfully!', 'success')
            return redirect(url_for('view_quiz_questions', quiz_id=question.quiz_id))
            
        return render_template('edit_questions.html', question=question)

    @app.route('/quiz/question/<int:question_id>/delete', methods=['POST'])
    def delete_question(question_id):
        question = Question.query.get_or_404(question_id)
        quiz_id = question.quiz_id
        
        db.session.delete(question)
        db.session.commit()
        
        flash('Question deleted successfully!', 'success')
        return redirect(url_for('view_quiz_questions', quiz_id=quiz_id))
