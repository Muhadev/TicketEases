import re
import logging
from flask import Blueprint, jsonify, request, redirect, current_app, url_for, render_template, flash
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Mail, Message
from .models import User
from . import db, mail
from .email import send_email
from .forms import RegisterForm
from .token_utils import generate_confirmation_token, confirm_token
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'

mail = Mail()

def create_response(message, status='success', code=200):
    return jsonify({'message': message, 'status': status}), code

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.form
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return create_response('All fields are required.', 'error', 400)

            user = User.query.filter_by(email=email).first()

            if user and user.check_password(password):
                login_user(user)
                return create_response('Logged in successfully.')
            else:
                return create_response('Invalid email or password.', 'error', 401)
        except Exception as e:
            logging.exception("An error occurred during login: %s", str(e))
            return create_response('An error occurred.', 'error', 500)

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Validate email and password format
        if not re.match(EMAIL_REGEX, email):
            flash('Invalid email format.', 'error')
            return render_template('register.html', form=form)
        
        if not re.match(PASSWORD_REGEX, password):
            flash('Password must be at least 8 characters long and include both letters and numbers.', 'error')
            return render_template('register.html', form=form)

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email address already exists.', 'error')
            return render_template('register.html', form=form)

        # Create and add user to the database
        new_user = User(username=username, email=email, password=password, confirmed=False)
        # new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Generate confirmation token and send confirmation email
        token = generate_confirmation_token(email)
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        html = render_template('confirm_email.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(email, subject, html)

        # Log in the user
        login_user(new_user)

        flash('A confirmation email has been sent via email.', 'success')
        return redirect(url_for("home.home"))

    return render_template('register.html', form=form)


@auth_bp.route('/test_email')
def test_email():
    try:
        msg = Message('Test Email', sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=['your_email@example.com'])
        msg.body = 'This is a test email.'
        mail.send(msg)
        return 'Email sent successfully'
    except Exception as e:
        logging.exception("An error occurred while sending the test email.")
        return str(e)

@auth_bp.route('/confirm_email/<token>', methods=['GET'])
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')

    user = User.query.filter_by(email=email).first_or_404()

    if user.confirmed:
        flash('Account already confirmed!', 'success')
    else:
        user.confirmed = True
        user.confirmed_on = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thank you!', 'success')

    return redirect(url_for('dashboard.dashboard'))

@auth_bp.route('/confirm/resend')
@login_required
def resend_confirmation():
    if current_user.confirmed:
        return redirect(url_for('dashboard.dashboard'))

    if current_user.confirm_attempts >= 3:
        flash('The maximum number of confirmation attempts has been reached.', 'warning') 
    else:
        token = generate_confirmation_token(current_user.email)
        confirm_url = url_for('confirm_email', token=token, _external=True)

        html = render_template('confirm_email.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(subject, current_user.email, html)

        current_user.confirm_attempts += 1
        db.session.commit()

        flash('A new confirmation link has been sent to your email address.', 'info')

    return redirect(url_for('unconfirmed'))

@auth_bp.route('/reset_password_request', methods=['POST'])
def reset_password_request():
    try:
        data = request.get_json()
        email = data.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            serializer = get_serializer()
            token = serializer.dumps(email, salt='password-reset')
            reset_link = url_for('auth.reset_password', token=token, _external=True, _scheme='https')
            email_html = render_template('password_reset.html', reset_link=reset_link)
            msg = Message('Password Reset Request', sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=[email])
            msg.html = email_html
            mail.send(msg)

        return create_response('If an account with that email exists, we have sent you a password reset email.')
    except Exception as e:
        logging.exception("An error occurred during password reset request: %s", str(e))
        return create_response('An error occurred.', 'error', 500)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        if request.method == 'POST':
            serializer = get_serializer()
            email = serializer.loads(token, salt='password-reset', max_age=3600)
            data = request.get_json()
            password = data.get('password')

            if not re.match(PASSWORD_REGEX, password):
                return create_response('Password must be at least 8 characters long and include both letters and numbers.', 'error', 400)

            user = User.query.filter_by(email=email).first()

            if user:
                user.set_password(password)
                db.session.commit()
                return create_response('Password reset successful.')
            else:
                return create_response('Invalid token.', 'error', 400)

        return render_template('reset_password.html', token=token)
    except SignatureExpired:
        return create_response('The password reset link has expired.', 'error', 400)
    except BadSignature:
        return create_response('Invalid password reset link.', 'error', 400)

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    try:
        if request.method == 'GET':
            return jsonify({'username': current_user.username, 'email': current_user.email}), 200
        elif request.method == 'POST':
            data = request.get_json()
            new_username = data.get('username')
            new_email = data.get('email')

            current_user.username = new_username
            current_user.email = new_email
            db.session.commit()

            return create_response('Profile updated successfully.')
    except Exception as e:
        logging.exception("An error occurred during profile update: %s", str(e))
        return create_response('An error occurred.', 'error', 500)

@auth_bp.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        return create_response('Logged out successfully.')
    except Exception as e:
        logging.exception("An error occurred during logout: %s", str(e))
        return create_response('An error occurred.', 'error', 500)
