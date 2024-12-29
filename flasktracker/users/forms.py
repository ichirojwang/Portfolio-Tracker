from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, NumberRange

from flasktracker.users.models import User


class SignUpForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(max=40)],
                       render_kw={"placeholder": "First and Last Name"})
    email = StringField("Email", validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField("Password",
                             validators=[DataRequired(),
                                         Length(min=8, message="Password must be at least 8 characters")],
                             render_kw={"placeholder": "Password"})
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo("password", message="Passwords must match")],
                                     render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField("Sign Up")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email already exists crodie.")


class LogInForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField("Password", validators=[DataRequired()], render_kw={"placeholder": "Password"})
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class UpdateAccountForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(max=40)],
                       render_kw={"placeholder": "First and Last Name"})
    email = StringField("Email", validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    submit = SubmitField("Confirm Changes")

    def validate_email(self, email):
        if current_user.email != email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email already exists crodie.')


class UpdateYearEligibleForm(FlaskForm):
    year = IntegerField("Year", validators=[DataRequired(), NumberRange(min=2009, max=2100,
                                                                        message="Year must be between 2009 and 2100")],
                        render_kw={"placeholder": "Year"})
    submit = SubmitField("Confirm Changes")
