from flask import Flask, render_template, request, url_for, redirect, flash, session, jsonify
from flask_login import login_required, current_user
from database import db, User, Subject, Chapter, Quiz, Question, Option, Score
from flask import Flask, render_template, request, url_for, redirect, flash, session, jsonify
from database import *
from flask import render_template
from database import db, Subject, Chapter, Question 
from datetime import datetime, timedelta,date 
from functools import wraps
from flask import session, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_login import LoginManager
from datetime import datetime, date
login_manager = LoginManager()
from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(IST)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    def home():
        return render_template("index.html")
    def validate_password(password):
        """Common password validation function"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"

        return True, "Password is valid"

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            fullname = request.form['fullname']
            qualification = request.form['qualification']
            dob = request.form['dob']

            # Password validation
            is_valid, message = validate_password(password)
            if not is_valid:
                return f"""
                    <script>
                        alert('{message}');
                        window.location.href = '/signup';
                    </script>
                """

            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return """
                    <script>
                        alert('Email already registered!');
                        window.location.href = '/signup';
                    </script>
                """

            user = User(email=email, password=password, role='user', 
                    username=fullname, qualification=qualification, dob=dob)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('signup.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['username']  
            password = request.form['password']
            
            user = User.query.filter(
                db.or_(
                    User.email == email,
                    User.username == email
                )
            ).first()

            if user and user.password == password: 
                session['user_id'] = user.id
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            else:
                return """
                    <script>
                        alert('Invalid credentials!');
                        window.location.href = '/login';
                    </script>
                """
        return render_template('login.html')

    @app.route('/forgot-password', methods=['GET', 'POST'])
    def forgot_password():
        if request.method == 'POST':
            try:
                username_or_email = request.form.get('email')
                new_password = request.form.get('new_password')
                confirm_password = request.form.get('confirm_password')
                
            
                if new_password != confirm_password:
                    return """
                        <script>
                            alert('Passwords do not match!');
                            window.location.href = '/forgot-password';
                        </script>
                    """

                is_valid, message = validate_password(new_password)
                if not is_valid:
                    return f"""
                        <script>
                            alert('{message}');
                            window.location.href = '/forgot-password';
                        </script>
                    """

                user = User.query.filter(
                    db.or_(
                        User.email == username_or_email,
                        User.username == username_or_email
                    )
                ).first()
                
                if not user:
                    return """
                        <script>
                            alert('Account not found!');
                            window.location.href = '/forgot-password';
                        </script>
                    """
                    
                # Update password
                user.password = new_password
                db.session.commit()
                
                return """
                    <script>
                        alert('Password updated successfully!');
                        window.location.href = '/login';
                    </script>
                """
                
            except Exception as e:
                return """
                    <script>
                        alert('An error occurred. Please try again.');
                        window.location.href = '/forgot-password';
                    </script>
                """
                
        return render_template('forgot_password.html')

    @app.route('/quiz/start/<int:quiz_id>')
    @app.route('/quiz/start/<int:quiz_id>/<int:question_number>')
    @login_required
    def start_quiz(quiz_id, question_number=1):
        quiz = Quiz.query.options(
            db.joinedload(Quiz.chapter).joinedload(Chapter.subject),
            db.joinedload(Quiz.questions).joinedload(Question.options)
        ).get_or_404(quiz_id)

        if 'quiz_start_time' not in session:
            session['quiz_start_time'] = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
            session['answers'] = {}
        
        start_time = datetime.strptime(session['quiz_start_time'], '%Y-%m-%d %H:%M:%S')
        start_time = IST.localize(start_time)
        current_time = datetime.now(IST)
        
        time_elapsed = current_time - start_time
        
        try:
            if ':' in quiz.time_duration:
                hours, minutes = map(int, quiz.time_duration.split(':'))
                total_minutes = hours * 60 + minutes
            else:
                total_minutes = int(quiz.time_duration)
        except (ValueError, TypeError):
            total_minutes = 60
            
        time_left = timedelta(minutes=total_minutes) - time_elapsed
        
        # If time is up, redirect to submit_quiz
        if time_left.total_seconds() <= 0:
            return redirect(url_for('submit_quiz', quiz_id=quiz_id))
        
        questions = quiz.questions
        if not questions:
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

    
    def auto_submit_quiz(quiz_id):
        """Handle automatic quiz submission when time runs out"""
        answers = session.get('answers', {})
        quiz = Quiz.query.options(
            db.joinedload(Quiz.chapter).joinedload(Chapter.subject),
            db.joinedload(Quiz.questions).joinedload(Question.options)
        ).get_or_404(quiz_id)
        
        total_marks = 0
        scored_marks = 0
        correct_answers = 0
        total_questions = len(quiz.questions)
        
        for question in quiz.questions:
            total_marks += question.marks
            user_answer_id = answers.get(str(question.id))
            
            if user_answer_id:
                selected_option = Option.query.get(int(user_answer_id))
                if selected_option and selected_option.is_correct:
                    scored_marks += question.marks
                    correct_answers += 1
        
        percentage = (scored_marks / total_marks * 100) if total_marks > 0 else 0
        
        try:
            user_id = session.get('user_id')
            if not user_id:
                raise ValueError("No user_id in session")
                
            new_score = Score(
                user_id=user_id,
                quiz_id=quiz_id,
                score=int(percentage),
                time_stamp=datetime.now(IST)
            )
            db.session.add(new_score)
            db.session.commit()
            
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
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
            
            # Clear session data
            session.pop('quiz_start_time', None)
            session.pop('answers', None)
            
            
            return render_template('scores.html',
                                quiz=quiz,
                                current_score=new_score,
                                all_scores=all_scores,
                                total_questions=total_questions,
                                correct_answers=correct_answers,
                                percentage=percentage,
                                user=user,
                                today=datetime.now(IST).date(),
                                auto_submitted=True)
                                
        except Exception as e:
            print(f"Error in auto-submitting quiz: {e}")
            db.session.rollback()
            return redirect(url_for('user_dashboard'))

    
    @app.route('/quiz/details/<int:quiz_id>')
    @login_required
    def view_quiz_details(quiz_id):
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
            return redirect(url_for('user_dashboard'))
        
        user_score = Score.query.filter_by(
            user_id=session.get('user_id'),
            quiz_id=quiz_id
        ).first()
        
        today = date.today()
        
        return render_template('quiz_details.html',
                            quiz_data=quiz_data,
                            user_score=user_score,
                            today=today)
    
    @app.route('/admin/unified-search')  
    @login_required
    def admin_unified_search():
        query = request.args.get('q', '')
        if query:
            # Search in all entities
            subjects = Subject.query.filter(
                db.or_(
                    Subject.name.ilike(f'%{query}%'),
                    Subject.description.ilike(f'%{query}%')
                )
            ).all()

            chapters = Chapter.query.filter(
                db.or_(
                    Chapter.name.ilike(f'%{query}%'),
                    Chapter.description.ilike(f'%{query}%')
                )
            ).all()

            quizzes = Quiz.query.join(Chapter).join(Subject).filter(
                db.or_(
                    Quiz.remarks.ilike(f'%{query}%'),
                    Chapter.name.ilike(f'%{query}%'),
                    Subject.name.ilike(f'%{query}%')
                )
            ).all()

            questions = Question.query.filter(
                db.or_(
                    Question.title.ilike(f'%{query}%'),
                    Question.question.ilike(f'%{query}%')
                )
            ).all()

            #for debugging
            print(f"Search query: {query}")
            print(f"Found subjects: {len(subjects)}")
            print(f"Found chapters: {len(chapters)}")
            print(f"Found quizzes: {len(quizzes)}")
            print(f"Found questions: {len(questions)}")

            return render_template(
                'unified_search_results.html',
                subjects=subjects,
                chapters=chapters,
                quizzes=quizzes,
                questions=questions,
                query=query
            )
        return redirect(url_for('admin_dashboard'))

    
    @app.route('/admin/search/users')
    @login_required
    def admin_search_users():
        query = request.args.get('user_q', '')
        if query:
            search_results = User.query.filter(
                db.or_(
                    User.username.ilike(f'%{query}%'),
                    User.email.ilike(f'%{query}%')
                )
            ).all()
            
            for user in search_results:
                if user.dob:
                    try:
                        user.dob = user.dob.strftime('%Y-%m-%d')
                    except:
                        pass
                        
            return render_template('user_search_results.html',
                                results=search_results, 
                                query=query)
        return redirect(url_for('admin_dashboard'))


    @app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
    @login_required
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)
        if user.role != 'admin':
            db.session.delete(user)
            db.session.commit()
        else:
            flash('Cannot delete admin users.', 'error')
        return redirect(url_for('admin_dashboard'))


    @app.route('/user/dashboard', methods=['GET', 'POST'])
    @login_required
    def user_dashboard():
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


    @app.route('/quiz/handle/<int:quiz_id>/<int:question_number>', methods=['POST'])
    @login_required
    def handle_quiz(quiz_id, question_number):
        action = request.form.get('action')
        answer = request.form.get('answer')
        timer_value = request.form.get('timer_value')
        print(f"Handle quiz - Action: {action}, Answer: {answer}")  # Debug print
            
        quiz = Quiz.query.get_or_404(quiz_id)
        question = quiz.questions[question_number - 1]
            
        if answer:
            if 'answers' not in session:
                session['answers'] = {}
            session['answers'][str(question.id)] = answer  
            session.modified = True
            print(f"Saved answer {answer} for question {question.id}")  # Debug print
            
        if timer_value == '0:00' or action == 'submit':
            print("Time's up or submit action - Submitting quiz...")
            return redirect(url_for('submit_quiz', quiz_id=quiz_id))
        
        if action == 'next':
            return redirect(url_for('start_quiz', quiz_id=quiz_id, question_number=question_number + 1))
        elif action == 'prev':
            return redirect(url_for('start_quiz', quiz_id=quiz_id, question_number=question_number - 1))
    
    from datetime import datetime, date

    @app.route('/quiz/submit/<int:quiz_id>', methods=['GET', 'POST'])
    @login_required
    def submit_quiz(quiz_id):
        print(f"Current user_id in session: {session.get('user_id')}")
        
        answers = session.get('answers', {})
        
        quiz = Quiz.query.options(
            db.joinedload(Quiz.chapter).joinedload(Chapter.subject),
            db.joinedload(Quiz.questions).joinedload(Question.options)
        ).get_or_404(quiz_id)
        
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
            
            session.pop('quiz_start_time', None)
            session.pop('answers', None)
            
            return render_template('scores.html',
                                quiz=quiz,
                                current_score=new_score,
                                all_scores=all_scores,
                                total_questions=total_questions,
                                correct_answers=correct_answers,
                                percentage=percentage,
                                user=user,
                                today=datetime.now(IST).date()
                                )
                                
        except Exception as e:
            print(f"Error submitting quiz: {e}")
            db.session.rollback()
            return redirect(url_for('user_dashboard'))
    
    @app.route('/search')
    @login_required
    def search_quizzes():
        query = request.args.get('q', '')
        if query:
            chapters = Chapter.query\
                .join(Subject)\
                .filter(
                    db.or_(
                        Chapter.name.ilike(f'%{query}%'),  # Match the chapter name
                        Chapter.description.ilike(f'%{query}%')  
                    )
                ).all()

            #search for quizzes that belong to the exact matching chapter requested by the user
            quizzes = Quiz.query\
                .join(Chapter)\
                .filter(
                    db.or_(
                        Quiz.remarks.ilike(f'%{query}%'),  # Match quiz remarks
                        Quiz.chapter_id.in_([chapter.id for chapter in chapters])  
                    )
                ).all()

            print(f"\nSearch query: {query}")
            print(f"Found chapters: {[chapter.name for chapter in chapters]}")
            print(f"Found quizzes: {[quiz.chapter.name for quiz in quizzes]}")

            return render_template('search_results.html',
                                chapters=chapters,
                                quizzes=quizzes,
                                query=query)
        return redirect(url_for('user_dashboard'))


  
  


    @app.route('/scores')
    @login_required
    def user_scores():
        scores = Score.query.filter_by(user_id=session['user_id'])\
                        .order_by(Score.time_stamp.desc())\
                        .all()
        
        return render_template('all_scores.html', 
                            scores=scores,
                            today=date.today())  




    @app.route('/user/summary')
    @login_required
    def user_summary():
        #get users subjectwise performance
        subject_performance = db.session.query(
            Subject.name,
            db.func.avg(Score.score).label('average_score'),
            db.func.count(Score.id).label('attempt_count')
        ).select_from(Subject)\
        .join(Chapter, Chapter.subject_id == Subject.id)\
        .join(Quiz, Quiz.chapter_id == Chapter.id)\
        .join(Score, Score.quiz_id == Quiz.id)\
        .filter(Score.user_id == session['user_id'])\
        .group_by(Subject.name)\
        .all()

        recent_attempts = db.session.query(
            Quiz.id,
            Chapter.name.label('chapter_name'),
            Subject.name.label('subject_name'),
            Score.score,
            Score.time_stamp
        ).select_from(Score)\
        .join(Quiz, Score.quiz_id == Quiz.id)\
        .join(Chapter, Quiz.chapter_id == Chapter.id)\
        .join(Subject, Chapter.subject_id == Subject.id)\
        .filter(Score.user_id == session['user_id'])\
        .order_by(Score.time_stamp.desc())\
        .limit(5)\
        .all()

        from datetime import datetime, timedelta
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        daily_performance = db.session.query(
            db.func.date(Score.time_stamp).label('date'),
            db.func.avg(Score.score).label('average_score'),
            db.func.count(Score.id).label('attempts')
        ).select_from(Score)\
        .filter(Score.user_id == session['user_id'])\
        .filter(Score.time_stamp >= seven_days_ago)\
        .group_by(db.func.date(Score.time_stamp))\
        .order_by(db.func.date(Score.time_stamp))\
        .all()

        overall_stats = db.session.query(
            db.func.count(Score.id).label('total_quizzes'),
            db.func.avg(Score.score).label('average_score'),
            db.func.max(Score.score).label('highest_score')
        ).select_from(Score)\
        .filter(Score.user_id == session['user_id'])\
        .first()

        if not overall_stats.total_quizzes:
            overall_stats = {
                'total_quizzes': 0,
                'average_score': 0,
                'highest_score': 0
            }

        return render_template('user_summary.html',
                            subject_performance=subject_performance,
                            recent_attempts=recent_attempts,
                            daily_performance=daily_performance,
                            overall_stats=overall_stats)



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
                return redirect(url_for('admin_dashboard'))
            return render_template('edit_chapter.html', chapter=chapter)

    @app.route('/chapter/delete/<int:chapter_id>', methods=['POST', 'GET'])
    def delete_chapter(chapter_id):
            chapter = Chapter.query.get_or_404(chapter_id)
            db.session.delete(chapter)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
    @app.route('/subject/add', methods=['GET', 'POST'])
    def add_subject():
            if request.method == 'POST':
                subject_name = request.form['name']
                subject_description = request.form['description']
                new_subject = Subject(name=subject_name, description=subject_description)
                db.session.add(new_subject)
                db.session.commit()
                return redirect(url_for('admin_dashboard'))
            return render_template('add_subject.html')
    @app.route('/chapter/add/<int:subject_id>', methods=['GET', 'POST'])
    def add_chapter(subject_id): 
            subject = Subject.query.get_or_404(subject_id)  # Get the subject or return 404 if not found
            
            if request.method == 'POST':
                chapter_name = request.form['name']
                chapter_description = request.form['description']
                new_chapter = Chapter(
                    name=chapter_name,
                    description=chapter_description,
                    subject_id=subject_id  
                )
                db.session.add(new_chapter)
                db.session.commit()
                return redirect(url_for('admin_dashboard'))
            
            return render_template('add_chapter.html', subject=subject)

    @app.route('/admin/quiz')
    def admin_quiz():
            quizzes = Quiz.query.all()
            chapters = Chapter.query.all()
            return render_template('admin_quiz.html', quizzes=quizzes, chapters=chapters)

    @app.route('/admin/summary')
    @login_required
    def admin_summary():
        # Subject-wise performance
        subject_performance = db.session.query(
            Subject.name,
            db.func.avg(Score.score).label('average_score'),
            db.func.count(Score.id).label('attempt_count')
        ).join(Chapter)\
        .join(Quiz)\
        .join(Score)\
        .group_by(Subject.name)\
        .all()

        # Chapter-wise performance
        chapter_performance = db.session.query(
            Chapter.name,
            Subject.name.label('subject_name'),
            db.func.avg(Score.score).label('average_score'),
            db.func.count(Score.id).label('attempt_count')
        ).join(Subject)\
        .join(Quiz)\
        .join(Score)\
        .group_by(Chapter.name, Subject.name)\
        .all()

        # Time-based performance (last 7 days)
        from datetime import datetime, timedelta
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        daily_performance = db.session.query(
            db.func.date(Score.time_stamp).label('date'),
            db.func.avg(Score.score).label('average_score'),
            db.func.count(Score.id).label('attempt_count')
        ).filter(Score.time_stamp >= seven_days_ago)\
        .group_by(db.func.date(Score.time_stamp))\
        .order_by(db.func.date(Score.time_stamp))\
        .all()

        # Top performing students
        top_students = db.session.query(
            User.username,
            db.func.avg(Score.score).label('average_score'),
            db.func.count(Score.id).label('quiz_count')
        ).join(Score)\
        .group_by(User.id)\
        .order_by(db.func.avg(Score.score).desc())\
        .limit(5)\
        .all()

        return render_template('admin_summary.html',
                            subject_performance=subject_performance,
                            chapter_performance=chapter_performance,
                            daily_performance=daily_performance,
                            top_students=top_students)





    @app.route('/quiz/add', methods=['GET', 'POST'])
    def add_quiz():
            if request.method == 'POST':
                chapter_id = request.form['chapter_id']
                quiz_date = request.form['date']
                quiz_duration = request.form['duration']
                
                new_quiz = Quiz(
                    chapter_id=chapter_id,
                    date_of_quiz=datetime.strptime(quiz_date, '%Y-%m-%d').date(),
                    time_duration=quiz_duration
                )
                db.session.add(new_quiz)
                db.session.commit()
                
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
                db.session.flush()  

                correct_option = request.form['correct_option']
                for i in range(4):
                    option = Option(
                        question_id=new_question.id,
                        option_text=request.form[f'option_{i}'],
                        is_correct=(str(i) == correct_option)
                    )
                    db.session.add(option)
                
                db.session.commit()
                return redirect(url_for('view_quiz_questions', quiz_id=quiz_id))
            
            return render_template('add_question.html', quiz=quiz)


    @app.route('/quiz/question/<int:question_id>/edit', methods=['GET', 'POST'])
    def edit_questions(question_id):
        question = Question.query.get_or_404(question_id)
        
        if request.method == 'POST':
            question.title = request.form['title']
            question.question = request.form['question']
            question.marks = int(request.form['marks'])
            
            Option.query.filter_by(question_id=question.id).delete()
            
            correct_option = request.form['correct_option']
            for i in range(4):
                option = Option(
                    question_id=question.id,
                    option_text=request.form[f'option_{i}'],
                    is_correct=(str(i) == correct_option)
                )
                db.session.add(option)
                
            db.session.commit()
            return redirect(url_for('view_quiz_questions', quiz_id=question.quiz_id))
            
        return render_template('edit_questions.html', question=question)

    @app.route('/quiz/question/<int:question_id>/delete', methods=['POST'])
    def delete_question(question_id):
        question = Question.query.get_or_404(question_id)
        quiz_id = question.quiz_id
        
        db.session.delete(question)
        db.session.commit()
        return redirect(url_for('view_quiz_questions', quiz_id=quiz_id))
    
    @app.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
    def edit_subject(subject_id):
        subject = Subject.query.get_or_404(subject_id)
        if request.method == 'POST':
            subject.name = request.form.get('subject_name')
            db.session.commit()
            return """
                <script>
                    alert('Subject updated successfully!');
                    window.location.href = '/admin/dashboard';
                </script>
            """
        return render_template('edit_subject.html', subject=subject)

    @app.route('/delete_subject/<int:subject_id>')
    def delete_subject(subject_id):
        subject = Subject.query.get_or_404(subject_id)
        
        try:
            chapters = Chapter.query.filter_by(subject_id=subject_id).all()
            
            for chapter in chapters:
                quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()
                
                for quiz in quizzes:
                    questions = Question.query.filter_by(quiz_id=quiz.id).all()
                    for question in questions:
                        Option.query.filter_by(question_id=question.id).delete()
                    Question.query.filter_by(quiz_id=quiz.id).delete()
                    
                    # Delete quiz scores
                    Score.query.filter_by(quiz_id=quiz.id).delete()
                    
                    # Delete the quiz
                    db.session.delete(quiz)
            
            # Delete all chapters for this subject
            Chapter.query.filter_by(subject_id=subject_id).delete()
            
            #delete the subject
            db.session.delete(subject)
            db.session.commit()
            
            return """
                <script>
                    alert('Subject and all associated data deleted successfully!');
                    window.location.href = '/admin/dashboard';
                </script>
            """
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting subject: {str(e)}") 
            return """
                <script>
                    alert('Error deleting subject. Please try again.');
                    window.location.href = '/admin_quiz';
                </script>
            """


    @app.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
    def edit_quiz(quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        chapters = db.session.query(Chapter).join(Subject).all()
        
        if request.method == 'POST':
            try:
                quiz.chapter_id = request.form.get('chapter_id')
                quiz.date_of_quiz = datetime.strptime(request.form.get('date_of_quiz'), '%Y-%m-%d')
                quiz.time_duration = request.form.get('time_duration')
                quiz.remarks = request.form.get('remarks', '')
                
                db.session.commit()
                return """
                    <script>
                        alert('Quiz updated successfully!');
                        window.location.href = '/admin/quiz';
                    </script>
                """
            except Exception as e:
                db.session.rollback()
                print(f"Error updating quiz: {str(e)}")
                return """
                    <script>
                        alert('Error updating quiz. Please try again.');
                        window.location.href = '/edit_quiz/{}';
                    </script>
                """.format(quiz_id)
                
        return render_template('edit_quiz.html', quiz=quiz, chapters=chapters)

    @app.route('/delete_quiz/<int:quiz_id>')
    def delete_quiz(quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        Question.query.filter_by(quiz_id=quiz_id).delete()
        Score.query.filter_by(quiz_id=quiz_id).delete()
        db.session.delete(quiz)
        db.session.commit()
        return """
            <script>
                alert('Quiz and all associated data deleted successfully!');
                window.location.href = '/admin/quiz';
            </script>
        """
