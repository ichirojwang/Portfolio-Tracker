from datetime import datetime

from flask_login import UserMixin
from sqlalchemy.orm import Mapped

from flasktracker import db, login_manager
from flasktracker.portfolios.models import Portfolio


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(80), nullable=False)
    email: Mapped[str] = db.Column(db.String(120), unique=True, nullable=False)
    password: Mapped[str] = db.Column(db.String(80), nullable=False)
    year_eligible: Mapped[int] = db.Column(db.Integer)
    start_date: Mapped[datetime] = db.Column(db.DateTime, nullable=False, default=datetime.now)

    portfolios: Mapped[list['Portfolio']] = db.relationship(backref='owner', lazy=True,
                                                            cascade='all, delete-orphan',
                                                            order_by="Portfolio.start_date")

    def __init__(self, name: str, email: str, password: str, year_eligible: int = None):
        self.name = name
        self.email = email
        self.password = password
        self.year_eligible = year_eligible

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}', '{self.email}', '{self.password}', {self.year_eligible})"
