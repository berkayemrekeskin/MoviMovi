# 150240721
# Berkay Emre Keskin
# BLG317E

from flask import Blueprint, g, render_template, request, redirect, url_for, flash, session
from app.db import create_connection

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = create_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s AND user_password = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user:
                session['logged_in'] = True
                session['user_id'] = user['userId']
                session['email'] = user['email']
                session['username'] = user['username']
                flash("Login successful!", "success")
                return redirect(url_for('user.get_user', id=user['userId']))
            else:
                flash("Login failed, check your credentials", "danger")
    return render_template('/auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash("Username already taken", "danger")
                return render_template('/auth/register.html')
            
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("Email already taken", "danger")
                return render_template('/auth/register.html')
            
            cursor.execute("INSERT INTO users (username, email, user_password) VALUES (%s, %s, %s)", (username, email, password))
            connection.commit()
            cursor.close()
            connection.close()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('auth.login'))
    return render_template('/auth/register.html')

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session['logged_in'] = False
    session.pop('email', None)  
    flash("You have been logged out.", "info")
    return redirect(url_for('main.index'))

@auth.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        connection = create_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE userId = %s", (user_id,))
            g.user = cursor.fetchone()
            cursor.close()
            connection.close()