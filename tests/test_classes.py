# this file is for testing @property methods of classes

import responses
from datetime import datetime

from flasktracker.portfolios.models import *
from flasktracker.users.models import User
from tests.test_portfolios_endpoints import create_transaction


def mock_api():
    responses.add(
        responses.GET,
        "https://www.alphavantage.co/query",
        json={
            "Global Quote": {
                "05. price": "150.00",
                "10. change percent": "1.50%"
            }
        },
        status=200
    )


@responses.activate
def test_stock_transaction_properties(app, client, auth):
    mock_api()
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        create_transaction(client, ticker="TEST.TO", price=100, quantity=10)
        create_transaction(client, ticker="LBJ", price=60.00, quantity=5)
        create_transaction(client, ticker="LBJ2", price=150, quantity=5)
        with app.app_context():
            t_1: StockTransaction = db.session.get(StockTransaction, 1)
            t_2: StockTransaction = db.session.get(StockTransaction, 2)
            t_3: StockTransaction = db.session.get(StockTransaction, 3)
            assert t_1.value == 1000
            assert t_1.open_pl == 1000
            assert t_2.value == 300
            assert t_2.open_pl == 450
            assert t_3.value == 750
            assert t_3.open_pl == 0


@responses.activate
def test_stock_wrapper_properties(app, client, auth):
    mock_api()
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        create_transaction(client, ticker="LBJ")
        with app.app_context():
            wrapper: StockWrapper = db.session.get(StockWrapper, 1)
            assert wrapper.ticker == "LBJ"
            assert wrapper.mkt_price == 150
            assert wrapper.mkt_change_percent == 1.5
            assert round(wrapper.mkt_change_value, 2) == 2.22


@responses.activate
def test_stock_properties(app, client, auth):
    mock_api()
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        create_transaction(client, ticker="LBJ", price=100, quantity=10)
        create_transaction(client, ticker="LBJ", price=50.00, quantity=5)
        create_transaction(client, ticker="LBJ", t_type="sell", price=120.00, quantity=4)
        create_transaction(client, ticker="LBJ", t_type="sell", price=70.00, quantity=2)
        with app.app_context():
            stock: Stock = db.session.get(Stock, 1)
            assert stock.total_qty == 15
            assert stock.close_qty == 6
            assert stock.open_qty == 9
            assert round(stock.avg_price, 2) == 83.33
            assert stock.mkt_price == 150
            assert round(stock.mkt_change_value, 2) == 2.22
            assert stock.mkt_change_percent == 1.5
            assert round(stock.mkt_value, 2) == 1350
            assert round(stock.open_cost_basis, 2) == 750
            assert round(stock.open_pl, 2) == 600
            assert round(stock.open_pl_percent, 2) == 80
            assert round(stock.close_cost_basis, 2) == 500
            assert round(stock.close_pl, 2) == 120
            assert round(stock.close_pl_percent, 2) == 24


@responses.activate
def test_port_properties(app, client, auth):
    mock_api()
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        create_transaction(client, ticker="LBJ", price=100, quantity=10)
        create_transaction(client, ticker="LBJ", price=50, quantity=10)
        create_transaction(client, ticker="LBJ2", price=80, quantity=10)
        create_transaction(client, ticker="LBJ2", price=75, quantity=10)
        create_transaction(client, ticker="LBJ3", price=70, quantity=10)
        create_transaction(client, ticker="LBJ3", price=120, quantity=10)
        with app.app_context():
            port: Portfolio = db.session.get(Portfolio, 1)
            assert port.total_mkt_value == 9000
            assert port.total_open_cost_basis == 4950
            assert port.total_open_pl == 4050
            assert round(port.total_open_pl_percent, 2) == 81.82


@responses.activate
def test_user_properties(app, client, auth):
    mock_api()
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        auth.create_port("LeBrons port 2")
        auth.create_port("LeBrons port 3")
        create_transaction(client, ticker="LBJ", price=100, quantity=10, port_id=1)
        create_transaction(client, ticker="LBJ", price=50, quantity=10, port_id=2)
        create_transaction(client, ticker="LBJ2", price=80, quantity=10, port_id=3)
        create_transaction(client, ticker="LBJ2", price=75, quantity=10, port_id=1)
        create_transaction(client, ticker="LBJ3", price=70, quantity=10, port_id=2)
        create_transaction(client, ticker="LBJ3", price=120, quantity=10, port_id=3)
        with app.app_context():
            user: User = db.session.get(User, 1)
            assert user.total_mkt_value == 9000
            assert user.total_open_cost_basis == 4950
            assert user.total_open_pl == 4050
            assert round(user.total_open_pl_percent, 2) == 81.82
