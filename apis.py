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