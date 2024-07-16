# Import necessary modules
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, TimeField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from .email_validation import is_valid
from .models import User

# Define the RegisterForm class
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8)])

    def validate_email(self, field):
        if not is_valid(field.data):
            raise ValidationError("Email is invalid")
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError("Email already registered")
    
    def validate_confirm_password(self, field):
        if self.password.data != field.data:
            raise ValidationError("Passwords must match")


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Login')

class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    time = TimeField('Time', format='%H:%M', validators=[DataRequired()])
    venue = StringField('Venue', validators=[DataRequired()])