from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('username', 
                            validators=[DataRequired(), Length(min=2, max=30)])

    email = StringField('Email',
                            validators=[DataRequired(), Email()])

    password = PasswordField('password',
                            validators=[DataRequired()])
    
    confirm_password = PasswordField('confirm password',
                            validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('register')

    def validate_username(self, username):
        
        user = User.query.filter_by(username=username.data).first()
        
        if user:
            raise ValidationError('That username is taken, please choose a different one.')

    def validate_email(self, email):
        
        user = User.query.filter_by(email=email.data).first()
        
        if user:
            raise ValidationError('That email is taken, please choose a different one.')

class LoginForm(FlaskForm):

    email = StringField('Email',
                            validators=[DataRequired(), Email()])

    password = PasswordField('Password',
                            validators=[DataRequired()])

    remember = BooleanField('Remember Me')

    submit = SubmitField('login')

class UpdateAccountForm(FlaskForm):
    username = StringField('username', 
                            validators=[DataRequired(), Length(min=2, max=30)])

    email = StringField('Email',
                            validators=[DataRequired(), Email()])                           

    submit = SubmitField('Update')

    def validate_username(self, username):
        
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            
            if user:
                raise ValidationError('That username is taken, please choose a different one.')

    def validate_email(self, email):
        
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            
            if user:
                raise ValidationError('That email is taken, please choose a different one.')   

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                            validators=[DataRequired(), Email()])  

    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        
        user = User.query.filter_by(email=email.data).first()
        
        if user is None:
            raise ValidationError('That email is not used, please register instead.')  


class ResetPasswordForm(FlaskForm):
    password = PasswordField('password',
                            validators=[DataRequired()])
    
    confirm_password = PasswordField('confirm password',
                            validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Submit Password Change')