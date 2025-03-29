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
login_manager = LoginManager()

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

            # Check if user already exists
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
            email = request.form['username']  # Form field name is 'username'
            password = request.form['password']
            
            # Find user by email or username
            user = User.query.filter(
                db.or_(
                    User.email == email,
                    User.username == email
                )
            ).first()

            if user and user.password == password:  # In production, use proper password hashing
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
                
                # Check if passwords match
                if new_password != confirm_password:
                    return """
                        <script>
                            alert('Passwords do not match!');
                            window.location.href = '/forgot-password';
                        </script>
                    """

                # Password validation
                is_valid, message = validate_password(new_password)
                if not is_valid:
                    return f"""
                        <script>
                            alert('{message}');
                            window.location.href = '/forgot-password';
                        </script>
                    """

                # Find user by email or username
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

    # @app.route('/forgot-password', methods=['GET', 'POST'])
    # def forgot_password():
    #     if request.method == 'POST':
    #         try:
    #             username_or_email = request.form.get('email')
    #             new_password = request.form.get('new_password')
    #             confirm_password = request.form.get('confirm_password')
                
    #             # Check if passwords match
    #             if new_password != confirm_password:
    #                 return """
    #                     <script>
    #                         alert('Passwords do not match!');
    #                         window.location.href = '/forgot-password';
    #                     </script>
    #                 """

    #             # Password validation
    #             if len(new_password) < 8:
    #                 return """
    #                     <script>
    #                         alert('Password must be at least 8 characters long');
    #                         window.location.href = '/forgot-password';
    #                     </script>
    #                 """

    #             # Check for uppercase
    #             if not any(c.isupper() for c in new_password):
    #                 return """
    #                     <script>
    #                         alert('Password must contain at least one uppercase letter');
    #                         window.location.href = '/forgot-password';
    #                     </script>
    #                 """

    #             # Check for lowercase
    #             if not any(c.islower() for c in new_password):
    #                 return """
    #                     <script>
    #                         alert('Password must contain at least one lowercase letter');
    #                         window.location.href = '/forgot-password';
    #                     </script>
    #                 """

    #             # Check for digits
    #             if not any(c.isdigit() for c in new_password):
    #                 return """
    #                     <script>
    #                         alert('Password must contain at least one number');
    #                         window.location.href = '/forgot-password';
    #                     </script>
    #                 """

    #             # Check for special characters
    #             special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    #             if not any(c in special_chars for c in new_password):
    #                 return """
    #                     <script>
    #                         alert('Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)');
    #                         window.location.href = '/forgot-password';
    #                     </script>
    #                 """

    #             # Find user by email or username
    #             user = User.query.filter(
    #                 db.or_(
    #                     User.email == username_or_email,
    #                     User.username == username_or_email
    #                 )
    #             ).first()
                
    #             if not user:
    #                 return """
    #                     <script>
    #                         alert('Account not found!');
    #                         window.location.href = '/forgot-password';
    #                     </script>
    #                 """
                    
    #             # Update password
    #             user.password = new_password
    #             db.session.commit()
                
    #             return """
    #                 <script>
    #                     alert('Password updated successfully!');
    #                     window.location.href = '/login';
    #                 </script>
    #             """
                
    #         except Exception as e:
    #             return """
    #                 <script>
    #                     alert('An error occurred. Please try again.');
    #                     window.location.href = '/forgot-password';
    #                 </script>
    #             """
                
    #     return render_template('forgot_password.html')


    # def is_valid_password(password):
    #     """
    #     Validate password meets requirements:
    #     - At least 8 characters long
    #     - Contains at least one uppercase letter
    #     - Contains at least one lowercase letter
    #     - Contains at least one number
    #     - Contains at least one special character
    #     """
    #     if len(password) < 8:
    #         return False
        
    #     has_upper = False
    #     has_lower = False
    #     has_digit = False
    #     has_special = False
    #     special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
    #     for char in password:
    #         if char.isupper():
    #             has_upper = True
    #         elif char.islower():
    #             has_lower = True
    #         elif char.isdigit():
    #             has_digit = True
    #         elif char in special_chars:
    #             has_special = True
        
    #     return all([has_upper, has_lower, has_digit, has_special])



    # @app.route('/login', methods=['GET', 'POST'])
    # def login():
    #     if request.method == 'POST':
    #         username_or_email = request.form['username']
    #         password = request.form['password']
    #         # user = User.query.filter_by(email=email).first()
    #         user = User.query.filter(
    #                 db.or_(
    #                     User.email == username_or_email,
    #                     User.username == username_or_email
    #                 )
    #             ).first()
                
    #         if user and user.password == password:
    #             session['user_id'] = user.id
    #             if user.role == 'admin':
    #                 return redirect(url_for('admin_dashboard'))
    #             else:
    #                 return redirect(url_for('user_dashboard'))
    #     return render_template('login.html')
    
    # @app.route('/signup', methods=['GET', 'POST'])
    # def signup():
    #     if request.method == 'POST':
    #         email = request.form['email']
    #         password = request.form['password']
    #         fullname = request.form['fullname']
    #         qualification = request.form['qualification']
    #         dob = request.form['dob']
    #         user = User(email=email, password=password, role='user' , username=fullname, qualification=qualification, dob=dob)
    #         db.session.add(user)
    #         db.session.commit()
    #         return redirect(url_for('login'))
    #     return render_template('signup.html')

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

    @app.route('/admin/search/quizzes')
    @login_required
    def admin_search_quizzes():
        query = request.args.get('quiz_q', '')
        if query:
            search_results = Quiz.query.join(Chapter).join(Subject)\
                .filter(
                    db.or_(
                        Chapter.name.ilike(f'%{query}%'),
                        Subject.name.ilike(f'%{query}%')
                    )
                ).all()
            return render_template('quiz_search_results.html',  # Changed from admin/quiz_search_results.html
                                results=search_results, 
                                query=query)
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
            
            # Format dates if needed
            for user in search_results:
                if user.dob:
                    try:
                        # Assuming dob is a datetime object
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
            # flash('User has been deleted successfully.', 'success')
        else:
            flash('Cannot delete admin users.', 'error')
        return redirect(url_for('admin_dashboard'))



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

    @app.route('/search')
    @login_required
    def search_quizzes():
        query = request.args.get('q', '')
        if query:
            # Search in quizzes, chapters, and subjects
            search_results = db.session.query(Quiz, Chapter, Subject)\
                .join(Chapter, Quiz.chapter_id == Chapter.id)\
                .join(Subject, Chapter.subject_id == Subject.id)\
                .filter(
                    db.or_(
                        Chapter.name.ilike(f'%{query}%'),
                        Subject.name.ilike(f'%{query}%'),
                        Chapter.description.ilike(f'%{query}%'),
                        Subject.description.ilike(f'%{query}%')
                    )
                ).all()
            
            return render_template('search_results.html', 
                                results=search_results, 
                                query=query)
        return redirect(url_for('user_dashboard'))
    @app.route('/scores')
    @login_required
    def user_scores():
        # Get all scores for the current user, ordered by timestamp (newest first)
        scores = Score.query.filter_by(user_id=session['user_id'])\
                        .order_by(Score.time_stamp.desc())\
                        .all()
        
        return render_template('all_scores.html', scores=scores)


    @app.route('/user/summary')
    @login_required
    def user_summary():
        # Get user's subject-wise performance
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

        # Get user's recent quiz attempts (last 5)
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

        # Get user's performance trend (last 7 days)
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

        # Calculate overall statistics
        overall_stats = db.session.query(
            db.func.count(Score.id).label('total_quizzes'),
            db.func.avg(Score.score).label('average_score'),
            db.func.max(Score.score).label('highest_score')
        ).select_from(Score)\
        .filter(Score.user_id == session['user_id'])\
        .first()

        # Handle the case when there are no scores yet
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
                # flash('Chapter updated successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            return render_template('edit_chapter.html', chapter=chapter)

    @app.route('/chapter/delete/<int:chapter_id>', methods=['POST', 'GET'])
    def delete_chapter(chapter_id):
            chapter = Chapter.query.get_or_404(chapter_id)
            db.session.delete(chapter)
            db.session.commit()
            # flash('Chapter deleted successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
    @app.route('/subject/add', methods=['GET', 'POST'])
    def add_subject():
            if request.method == 'POST':
                subject_name = request.form['name']
                subject_description = request.form['description']
                new_subject = Subject(name=subject_name, description=subject_description)
                db.session.add(new_subject)
                db.session.commit()
                # flash('Subject added successfully!', 'success')
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
                # flash('Chapter added successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            
            return render_template('add_chapter.html', subject=subject)

    @app.route('/admin/quiz')
    def admin_quiz():
            # Get all quizzes instead of chapters
            quizzes = Quiz.query.all()
            chapters = Chapter.query.all()
            return render_template('admin_quiz.html', quizzes=quizzes, chapters=chapters)

    # Route in your Flask application
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
                
                # Create new quiz
                new_quiz = Quiz(
                    chapter_id=chapter_id,
                    date_of_quiz=datetime.strptime(quiz_date, '%Y-%m-%d').date(),
                    time_duration=quiz_duration
                )
                db.session.add(new_quiz)
                db.session.commit()
                
                # flash('Quiz created successfully!', 'success')
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
                # flash('Question added successfully!', 'success')
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
            # flash('Question updated successfully!', 'success')
            return redirect(url_for('view_quiz_questions', quiz_id=question.quiz_id))
            
        return render_template('edit_questions.html', question=question)

    @app.route('/quiz/question/<int:question_id>/delete', methods=['POST'])
    def delete_question(question_id):
        question = Question.query.get_or_404(question_id)
        quiz_id = question.quiz_id
        
        db.session.delete(question)
        db.session.commit()
        
        # flash('Question deleted successfully!', 'success')
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
            # Get all chapters for this subject
            chapters = Chapter.query.filter_by(subject_id=subject_id).all()
            
            # For each chapter, delete associated quizzes and their data
            for chapter in chapters:
                # Get all quizzes for this chapter
                quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()
                
                for quiz in quizzes:
                    # Delete quiz questions and options
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
            
            # Finally delete the subject
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
            print(f"Error deleting subject: {str(e)}")  # For debugging
            return """
                <script>
                    alert('Error deleting subject. Please try again.');
                    window.location.href = '/admin_quiz';
                </script>
            """


    @app.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
    def edit_quiz(quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        # Get all chapters with their subjects
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
        # Delete associated questions first
        Question.query.filter_by(quiz_id=quiz_id).delete()
        # Delete quiz scores
        Score.query.filter_by(quiz_id=quiz_id).delete()
        db.session.delete(quiz)
        db.session.commit()
        return """
            <script>
                alert('Quiz and all associated data deleted successfully!');
                window.location.href = '/admin/quiz';
            </script>
        """
