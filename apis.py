from flask import Flask, render_template, request, url_for, redirect, flash, session, jsonify
from database import *
from flask import render_template
from database import db, Subject, Chapter, Question 
def configure_routes(app):
    @app.route("/")
    def hello_world():
        return render_template("index.html")

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            
            user = User.query.filter_by(email=email, password=password).first()
            
            if user:
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid email or password')
                return redirect(url_for('login'))
                
        return render_template('login.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            name = request.form.get('fullname')
            email = request.form.get('email')
            password = request.form.get('password')
            qualification = request.form.get('qualification')
            dob = request.form.get('dob')
            role = 'customer'

            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("Email already exists. Try logging in.", "error")
                return redirect(url_for('signup'))

            try:
                new_user = User(username=name, email=email, password=password, 
                              qualification=qualification, dob=dob, role=role)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                return jsonify({"message": "Database error. Please try again."}), 500

        return render_template('signup.html')

 # Import necessary models

    @app.route('/admin_dashboard')
    def admin_dashboard():
        subjects = Subject.query.all()

        # Create a structured data list
        subjects_data = []
        for subject in subjects:
            chapters_data = []
            for chapter in subject.chapters:
                question_count = Question.query.filter_by(chapter_id=chapter.id).count()
                chapters_data.append({
                    "chapter_id": chapter.id,
                    "chapter_name": chapter.name,
                    "question_count": question_count
                })
            
            subjects_data.append({
                "subject_id": subject.id,
                "subject_name": subject.name,
                "chapters": chapters_data
            })

        return render_template('admin_dashboard.html', subjects=subjects_data)



    @app.route('/quiz_management')
    def quiz_management():
        return render_template('quiz_management.html')

    @app.route('/admin_summary')
    def admin_summary():
        return render_template('admin_summary.html')

    @app.route('/user_dashboard')
    def user_dashboard():
        if 'user_id' not in session:
            flash('Please login to access this page')
            return redirect(url_for('login'))
        
        user_scores = UserScore.query.filter_by(user_id=session['user_id']).all()
        available_quizzes = Quiz.query.all()
        
        return render_template('user_dashboard.html', 
                             user_scores=user_scores, 
                             quizzes=available_quizzes)

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))
    @app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
    def edit_chapter(chapter_id):
        chapter = Chapter.query.get_or_404(chapter_id)
        if request.method == 'POST':
            chapter.name = request.form['name']
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        return render_template('edit_chapter.html', chapter=chapter)

    @app.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
    def delete_chapter(chapter_id):
        chapter = Chapter.query.get_or_404(chapter_id)
        db.session.delete(chapter)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

