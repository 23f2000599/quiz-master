from flask import Flask, render_template, request, url_for, redirect, flash, session, jsonify
from database import *
from flask import render_template
from database import db, Subject, Chapter, Question 
from datetime import datetime, timedelta
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

    # @app.route('/admin/quiz')
    # def admin_quiz():
    #     chapters = Chapter.query.all()
    #     return render_template('admin_quiz.html', chapters=chapters)

    # @app.route('/question/add/<int:chapter_id>', methods=['GET', 'POST'])
    # def add_question(chapter_id):
    #     chapter = Chapter.query.get_or_404(chapter_id)
        
    #     if request.method == 'POST':
    #         # Create new quiz if date is provided
    #         quiz_date = request.form.get('date')
    #         quiz_duration = request.form.get('duration')
            
    #         # Check if a quiz already exists for this date and chapter
    #         quiz = Quiz.query.filter_by(
    #             chapter_id=chapter_id,
    #             date_of_quiz=datetime.strptime(quiz_date, '%Y-%m-%d').date()
    #         ).first()
            
    #         if not quiz:
    #             # Create new quiz if none exists
    #             quiz = Quiz(
    #                 chapter_id=chapter_id,
    #                 date_of_quiz=datetime.strptime(quiz_date, '%Y-%m-%d').date(),
    #                 time_duration=quiz_duration,
    #                 remarks=request.form.get('remarks', '')
    #             )
    #             db.session.add(quiz)
    #             db.session.flush()

    #         # Create question
    #         new_question = Question(
    #             quiz_id=quiz.id,
    #             question_text=request.form['question'],
    #             marks=request.form.get('marks', 1)
    #         )
    #         db.session.add(new_question)
    #         db.session.flush()

    #         # Create 4 options
    #         correct_option = request.form['correct_option']
    #         for i in range(4):
    #             option = Option(
    #                 question_id=new_question.id,
    #                 option_text=request.form[f'option_{i}'],
    #                 is_correct=(str(i) == correct_option)
    #             )
    #             db.session.add(option)
            
    #         db.session.commit()
    #         flash('Question added successfully!', 'success')
    #         return redirect(url_for('admin_quiz'))
        
    #     return render_template('add_question.html', chapter=chapter)
    # @app.route('/question/edit/<int:question_id>', methods=['GET', 'POST'])
    # def edit_question(question_id):
    #     question = Question.query.get_or_404(question_id)
        
    #     if request.method == 'POST':
    #         question.question_text = request.form['question']
    #         question.marks = request.form.get('marks', 1)
            
    #         # Update options
    #         correct_option = request.form['correct_option']
    #         for i, option in enumerate(question.options):
    #             option.option_text = request.form[f'option_{i}']
    #             option.is_correct = (str(i) == correct_option)
                
    #         db.session.commit()
    #         flash('Question updated successfully!', 'success')
    #         return redirect(url_for('admin_quiz'))
        
    #     return render_template('edit_question.html', question=question)

    # @app.route('/question/delete/<int:question_id>', methods=['POST'])
    # def delete_question(question_id):
    #     question = Question.query.get_or_404(question_id)
    #     db.session.delete(question)
    #     db.session.commit()
    #     flash('Question deleted successfully!', 'success')
    #     return redirect(url_for('admin_quiz'))
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
