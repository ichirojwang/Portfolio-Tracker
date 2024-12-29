from datetime import datetime

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange, Optional

from flasktracker.portfolios.models import StockTransactionType


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
