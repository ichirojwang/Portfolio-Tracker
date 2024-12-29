from datetime import datetime
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField, FloatField, DateTimeField, \
    SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, NumberRange, Optional
from flasktracker.models import User, StockTransactionType


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


class CreatePortfolioForm(FlaskForm):
    name = StringField("Portfolio Name", validators=[DataRequired(), Length(max=40)],
                       render_kw={"placeholder": "Portfolio Name"})
    submit = SubmitField("Create Portfolio")

    def validate_name(self, name):
        for port in current_user.portfolios:
            if port.name == name.data:
                raise ValidationError("You already have a portfolio with that name crodie.")


class PortfolioTransactionForm(FlaskForm):
    type = SelectField("Type",
                       choices=[(StockTransactionType.BUY.value, 'Buy'), (StockTransactionType.SELL.value, 'Sell')])
    ticker = StringField("Ticker", validators=[DataRequired(), Length(max=20)], render_kw={"placeholder": "Ticker"})
    date = DateTimeField("Date", validators=[DataRequired()], format="%Y-%m-%d",
                         render_kw={"placeholder": "yyyy-mm-dd", "type": "date",
                                    "value": datetime.now().strftime("%Y-%m-%d")})
    quantity = FloatField("Quantity", validators=[DataRequired(), NumberRange(min=0)],
                          render_kw={"placeholder": "Quantity", "type": "number", "min": 0, "step": 0.01})
    price = FloatField("Price", validators=[DataRequired(), NumberRange(min=0)],
                       render_kw={"placeholder": "Price", "type": "number", "min": 0, "step": 0.01})
    fees = FloatField("Fees", validators=[Optional(), NumberRange(min=0)],
                      render_kw={"placeholder": "Fees", "type": "number", "min": 0, "step": 0.01})
    submit = SubmitField("Confirm")

    def validate_date(self, date):
        if date.data > datetime.now():
            raise ValidationError("You cannot select a future date croski.")
