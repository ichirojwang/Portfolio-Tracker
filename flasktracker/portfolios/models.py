from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy.orm import Mapped

from flasktracker import db
from flasktracker.portfolios.stock_api import get_price


class Portfolio(db.Model):
    __tablename__ = 'portfolios'

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(80), nullable=False)
    start_date: Mapped[datetime] = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('User', back_populates='portfolios')

    stocks: Mapped[list['Stock']] = db.relationship('Stock', back_populates='portfolio', lazy=True,
                                                    cascade='all, delete-orphan')

    def __init__(self, name: str, user_id: int):
        self.name = name
        self.user_id = user_id

    @property
    def total_mkt_value(self):
        return sum(s.mkt_value for s in self.stocks)

    @property
    def total_open_cost_basis(self):
        return sum(s.open_cost_basis for s in self.stocks)

    @property
    def total_open_pl(self):
        return sum(s.open_pl for s in self.stocks)

    @property
    def total_open_pl_percent(self):
        return (self.total_open_pl / self.total_open_cost_basis) * 100 if self.total_open_cost_basis > 0 else 0

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"


class StockWrapper(db.Model):
    __tablename__ = 'stock_wrappers'
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    ticker: Mapped[str] = db.Column(db.String(10), nullable=False)
    market_cache: Mapped[float] = db.Column(db.Float)
    date_cache: Mapped[datetime] = db.Column(db.DateTime)
    market_change_percent_cache: Mapped[float] = db.Column(db.Float)

    stocks: Mapped[list['Stock']] = db.relationship('Stock', back_populates='wrapper', lazy=True,
                                                    cascade='all, delete-orphan')

    def __init__(self, ticker: str):
        self.ticker = ticker

    def __update_cache(self) -> None:
        if self.date_cache is None or self.date_cache < datetime.now() - timedelta(hours=5):
            data = get_price(self.ticker)
            if data is None:
                self.market_cache = 0
                self.market_change_percent_cache = 0
                self.date_cache = datetime.now()
            else:
                self.market_cache = data.get("market")
                self.market_change_percent_cache = data.get("change")
                self.date_cache = datetime.now()
            db.session.commit()

    @property
    def mkt_price(self) -> float:
        self.__update_cache()
        return self.market_cache

    @property
    def mkt_change_percent(self) -> float:
        self.__update_cache()
        return self.market_change_percent_cache

    @property
    def mkt_change_value(self):
        self.__update_cache()
        return (self.mkt_price * self.mkt_change_percent) / (100 + self.mkt_change_percent)

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.ticker}')"


class Stock(db.Model):
    __tablename__ = 'stocks'
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    ticker: Mapped[str] = db.Column(db.String(10), nullable=False)
    comments: Mapped[str] = db.Column(db.Text, nullable=False, default="")
    sector: Mapped[str] = db.Column(db.String(10), nullable=False, default="")

    portfolio_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    portfolio: Mapped['Portfolio'] = db.relationship('Portfolio', back_populates='stocks')

    stock_wrapper_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('stock_wrappers.id'), nullable=False)
    wrapper: Mapped['StockWrapper'] = db.relationship('StockWrapper', back_populates='stocks')

    transactions: Mapped[list['StockTransaction']] = db.relationship('StockTransaction', back_populates='stock',
                                                                     lazy=True, cascade='all, delete-orphan',
                                                                     order_by='desc(StockTransaction.date)')

    def __init__(self, ticker: str, stock_wrapper_id: int, portfolio_id: int):
        self.ticker = ticker
        self.stock_wrapper_id = stock_wrapper_id
        self.portfolio_id = portfolio_id

    @property
    def total_qty(self) -> float:
        return sum(t.quantity for t in self.transactions if t.type == StockTransactionType.BUY)

    @property
    def close_qty(self) -> float:
        return sum(t.quantity for t in self.transactions if t.type == StockTransactionType.SELL)

    @property
    def open_qty(self) -> float:
        return self.total_qty - self.close_qty

    @property
    def avg_price(self) -> float:
        total_value: float = sum(
            (t.quantity * t.price) for t in self.transactions if t.type == StockTransactionType.BUY)
        return total_value / self.total_qty if self.total_qty > 0 else 0

    @property
    def mkt_price(self) -> float:
        return self.wrapper.mkt_price

    @property
    def mkt_change_value(self) -> float:
        return self.wrapper.mkt_change_value

    @property
    def mkt_change_percent(self) -> float:
        return self.wrapper.mkt_change_percent

    @property
    def mkt_value(self) -> float:
        return self.wrapper.mkt_price * self.open_qty

    @property
    def open_cost_basis(self) -> float:
        return self.avg_price * self.open_qty

    @property
    def open_pl(self) -> float:
        return (self.mkt_price - self.avg_price) * self.open_qty

    @property
    def open_pl_percent(self) -> float:
        return (self.open_pl / self.open_cost_basis) * 100 if self.open_cost_basis > 0 else 0

    @property
    def close_cost_basis(self) -> float:
        return self.avg_price * self.close_qty

    @property
    def close_pl(self) -> float:
        return sum((t.quantity * (t.price - self.avg_price)) for t in self.transactions if
                   t.type == StockTransactionType.SELL)

    @property
    def close_pl_percent(self) -> float:
        return (self.close_pl / self.close_cost_basis) * 100 if self.close_cost_basis > 0 else 0

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.ticker}')"


class StockTransactionType(Enum):
    BUY: str = "buy"
    SELL: str = "sell"


class StockTransaction(db.Model):
    __tablename__ = 'transactions'
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    type: Mapped[StockTransactionType] = db.Column(db.Enum(StockTransactionType), nullable=False)
    date: Mapped[datetime] = db.Column(db.DateTime, nullable=False, default=datetime.now)
    ticker: Mapped[str] = db.Column(db.String(10), nullable=False)
    quantity: Mapped[float] = db.Column(db.Float, nullable=False, default=0)
    price: Mapped[float] = db.Column(db.Float, nullable=False, default=0)
    fees: Mapped[float] = db.Column(db.Float, default=0)

    stock_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    stock: Mapped['Stock'] = db.relationship('Stock', back_populates='transactions')

    def __init__(self, trans_type: StockTransactionType, date: datetime, ticker: str, quantity: float, price: float,
                 fees: float, stock_id: int):
        self.type = trans_type
        self.date = date
        self.ticker = ticker
        self.quantity = quantity
        self.price = price
        self.fees = fees
        self.stock_id = stock_id

    @property
    def value(self) -> float:
        return self.quantity * self.price

    @property
    def open_pl(self) -> float:
        return (self.stock.mkt_price - self.price) * self.quantity

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.type}', '{self.ticker}', {self.quantity}, {self.fees})"
