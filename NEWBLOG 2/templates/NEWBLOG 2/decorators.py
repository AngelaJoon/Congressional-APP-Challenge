from functools import wraps
from flask import session, url_for, render_template, redirect

def welcome_screen(original_function):
    @wraps(original_function)
    def decorated_function(*args, **kwargs):
        if session.get('visited'):
            return original_function(*args, **kwargs)
        else:
            session['visited'] = True
            return render_template('welcome.html')

    return decorated_function

def login_required(original_function):
    @wraps(original_function)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in'):
            return original_function(*args, **kwargs)
        else:
            return redirect(url_for('login'))

    return decorated_function