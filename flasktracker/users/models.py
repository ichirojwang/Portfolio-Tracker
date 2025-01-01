from datetime import datetime

from flask_login import UserMixin
from sqlalchemy.orm import Mapped

from flasktracker import db, login_manager
from flasktracker.portfolios.models import Portfolio


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(80), nullable=False)
    email: Mapped[str] = db.Column(db.String(120), unique=True, nullable=False)
    password: Mapped[str] = db.Column(db.String(80), nullable=False)
    year_eligible: Mapped[int] = db.Column(db.Integer)
    start_date: Mapped[datetime] = db.Column(db.DateTime, nullable=False, default=datetime.now)

    portfolios: Mapped[list['Portfolio']] = db.relationship('Portfolio', back_populates='owner', lazy=True,
                                                            cascade='all, delete-orphan',
                                                            order_by="Portfolio.start_date")

    def __init__(self, name: str, email: str, password: str, year_eligible: int = None):
        self.name = name
        self.email = email
        self.password = password
        self.year_eligible = year_eligible

    @property
    def total_mkt_value(self):
        return sum(port.total_mkt_value for port in self.portfolios)

    @property
    def total_open_cost_basis(self):
        return sum(port.total_open_cost_basis for port in self.portfolios)

    @property
    def total_open_pl(self):
        return sum(port.total_open_pl for port in self.portfolios)

    @property
    def total_open_pl_percent(self):
        return (self.total_open_pl / self.total_open_cost_basis) * 100 if self.total_open_cost_basis else 0

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}', '{self.email}', '{self.password}', {self.year_eligible})"
